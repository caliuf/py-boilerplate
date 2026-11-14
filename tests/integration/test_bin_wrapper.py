"""Contratto dei wrapper in `bin/`.

Verifica che il wrapper risolva il repository, applichi il floor committato,
carichi l'environment del chiamante via direnv e fallisca con guida quando i
prerequisiti mancano o l'environment è bloccato.
"""

import os
import subprocess
from pathlib import Path

import pytest
from tests.support.process import REPO_ROOT, ProcessResult

WRAPPER = REPO_ROOT / "bin" / "py-boilerplate-hello-world"


def _find_in_path(name: str) -> Path | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def _run_wrapper(
    cwd: Path,
    args: list[str],
    *,
    xdg_data_home: Path | None = None,
    path: str | None = None,
) -> ProcessResult:
    env = {
        "PATH": path if path is not None else os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "XDG_DATA_HOME": str(xdg_data_home) if xdg_data_home is not None else "",
        "NO_COLOR": "1",
        "LOG_LEVEL": "error",
    }
    completed = subprocess.run(
        [str(WRAPPER), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return ProcessResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _allow_direnv(directory: Path, xdg_data_home: Path) -> None:
    xdg_data_home.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["direnv", "allow", str(directory)],
        env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "XDG_DATA_HOME": str(xdg_data_home),
        },
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )


def _setup_allowed_caller(tmp_path: Path, name: str) -> tuple[Path, Path]:
    caller = tmp_path / "caller"
    caller.mkdir()
    (caller / ".env").write_text(f'HELLO_WORLD_NAME="{name}"\n', encoding="utf-8")
    (caller / ".envrc").write_text("dotenv .env\n", encoding="utf-8")
    xdg = tmp_path / "xdg"
    _allow_direnv(caller, xdg)
    return caller, xdg


def test_wrapper_loads_caller_environment(tmp_path: Path) -> None:
    caller, xdg = _setup_allowed_caller(tmp_path, "Ada Lovelace")

    result = _run_wrapper(caller, ["--json"], xdg_data_home=xdg)

    assert result.returncode == 0
    assert "direnv: loading" in result.stderr
    assert '"message": "Hello, Ada Lovelace!"' in result.stdout


def test_cli_flag_overrides_caller_environment(tmp_path: Path) -> None:
    caller, xdg = _setup_allowed_caller(tmp_path, "Ada Lovelace")

    result = _run_wrapper(caller, ["--name", "Bob", "--json"], xdg_data_home=xdg)

    assert result.returncode == 0
    assert '"message": "Hello, Bob!"' in result.stdout


def test_wrapper_falls_back_to_the_committed_floor(tmp_path: Path) -> None:
    caller = tmp_path / "caller"
    caller.mkdir()
    floor = REPO_ROOT / ".env.default"

    syntax = subprocess.run(
        ["bash", "-n", str(floor)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert syntax.returncode == 0

    result = _run_wrapper(caller, ["--json"])

    assert result.returncode == 0
    assert '"message": "Hello, world!"' in result.stdout


def test_blocked_envrc_fails_with_guidance(tmp_path: Path) -> None:
    caller = tmp_path / "caller"
    caller.mkdir()
    (caller / ".env").write_text("HELLO_WORLD_NAME=Ada\n", encoding="utf-8")
    (caller / ".envrc").write_text("dotenv .env\n", encoding="utf-8")

    result = _run_wrapper(caller, ["--json"], xdg_data_home=tmp_path / "xdg")

    assert result.returncode != 0
    assert "direnv allow" in result.stderr


def test_missing_direnv_fails_with_guidance(tmp_path: Path) -> None:
    caller = tmp_path / "caller"
    caller.mkdir()
    minimal_path = tmp_path / "bin"
    minimal_path.mkdir()

    for tool in ("bash", "env", "readlink", "dirname", "uv"):
        found = _find_in_path(tool)
        if found is None:
            pytest.fail(f"required tool not found in PATH: {tool}")
        (minimal_path / tool).symlink_to(found)

    result = _run_wrapper(caller, ["--json"], path=str(minimal_path))

    assert result.returncode != 0
    assert "direnv" in result.stderr
