"""Helper per eseguire processi reali nei test di contratto ed E2E."""

import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class ProcessResult:
    """Esito di un processo con stream separati."""

    returncode: int
    stdout: str
    stderr: str


def clean_env(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    """Environment deterministico per i sottoprocessi."""

    env = dict(os.environ)
    env.pop("HELLO_WORLD_NAME", None)
    env.pop("NO_COLOR", None)
    env.pop("FORCE_COLOR", None)
    env["LOG_LEVEL"] = "error"
    env["APP_ENV"] = "test"
    if extra is not None:
        env.update(extra)
    return env


def run_python_module(
    module: str,
    args: Sequence[str],
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> ProcessResult:
    """Esegue `python -m <module>` nel repository, senza shell."""

    completed = subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=cwd if cwd is not None else REPO_ROOT,
        env=dict(env) if env is not None else clean_env(),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return ProcessResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def run_cli(
    args: Sequence[str],
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> ProcessResult:
    """Esegue la CLI reale come processo separato."""

    return run_python_module("py_boilerplate.entrypoints.cli.main", args, env=env, cwd=cwd)
