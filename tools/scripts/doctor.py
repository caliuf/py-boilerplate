"""`just doctor` — verifica runtime, tool e configurazione del repository.

Exit code 1 se un controllo hard fallisce; warning per i tool opzionali.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[2]
type Status = Literal["ok", "warn", "fail"]


@dataclass(frozen=True, slots=True)
class Check:
    """Esito di un controllo, con dettaglio leggibile."""

    label: str
    status: Status
    detail: str = ""


checks: list[Check] = []


def ok(label: str, detail: str = "") -> None:
    checks.append(Check(label, "ok", detail))


def warn(label: str, detail: str = "") -> None:
    checks.append(Check(label, "warn", detail))


def fail(label: str, detail: str = "") -> None:
    checks.append(Check(label, "fail", detail))


def _run(args: Sequence[str], timeout: float = 15) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            list(args),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _binary(name: str) -> str | None:
    return shutil.which(name)


def _version(name: str) -> str:
    path = _binary(name)
    if path is None:
        return ""
    for args in ([path, "--version"], [path, "version"]):
        completed = _run(args)
        if completed is not None and completed.returncode == 0:
            output = (completed.stdout or completed.stderr).strip().splitlines()
            if output:
                return output[0]
    return ""


def _check_required(name: str, detail: str) -> None:
    if _binary(name):
        ok(name, _version(name))
    else:
        fail(name, f"{detail} — run `just install` or `mise install`")


def _check_optional(name: str, detail: str) -> None:
    if _binary(name):
        ok(name, _version(name))
    else:
        warn(name, f"{detail} — local gate skipped, CI still blocks")


def _check_python() -> None:
    version_file = ROOT / ".python-version"
    try:
        expected = version_file.read_text(encoding="utf-8").strip()
    except OSError:
        fail("python", ".python-version is missing")
        return

    actual = platform.python_version()
    if actual == expected:
        ok("python", actual)
    elif actual.split(".")[:2] == expected.split(".")[:2]:
        warn("python", f"{actual} (pinned: {expected})")
    else:
        fail("python", f"{actual} does not match pinned {expected} — run `just setup`")


def _check_install_state() -> None:
    if (ROOT / ".venv").is_dir():
        ok("virtualenv", ".venv")
    else:
        fail("virtualenv", "missing — run `just setup`")

    if (ROOT / "uv.lock").is_file():
        ok("lockfile", "uv.lock")
    else:
        fail("lockfile", "uv.lock missing — run `uv lock`")

    if not (ROOT / ".env").is_file():
        warn(".env", "absent — optional; copy from .env.example if you need local overrides")


def _check_lockfile_coherence() -> None:
    completed = _run(["uv", "lock", "--check"], timeout=60)
    if completed is None:
        fail("uv.lock coherence", "could not run `uv lock --check`")
    elif completed.returncode == 0:
        ok("uv.lock coherence")
    else:
        fail("uv.lock coherence", "out of date — run `uv lock`, never edit it manually")


def _check_hooks() -> None:
    completed = _run(["git", "config", "--get", "core.hooksPath"])
    if completed is None or completed.returncode != 0:
        fail("git hooks", "core.hooksPath not set — run `just setup`")
        return
    hooks = completed.stdout.strip()
    if hooks == ".githooks":
        ok("git hooks", hooks)
    else:
        fail("git hooks", f'core.hooksPath is "{hooks}" — run `just setup`')


def _check_direnv() -> None:
    if not _binary("direnv"):
        fail("direnv", "required by bin/ wrappers — run `mise install`")
        return
    completed = _run(["direnv", "exec", ".", "true"], timeout=30)
    if completed is not None and completed.returncode == 0:
        ok(".envrc", "allowed")
    else:
        warn(".envrc", "blocked — run `direnv allow`")


def _check_local_binary(name: str, detail: str) -> None:
    if (ROOT / "node_modules/.bin" / name).exists():
        ok(name, f"installed in node_modules ({detail})")
    else:
        warn(name, f"not installed — run `npm ci` ({detail})")


def _check_playwright_browsers() -> None:
    if (Path.home() / ".cache/ms-playwright").exists():
        ok("playwright browsers")
    else:
        warn("playwright browsers", "run `npx playwright install chromium`")


def _check_playwright() -> None:
    if not (ROOT / "node_modules/.bin/playwright").exists():
        warn("playwright", "not installed — run `npm ci`")
        return
    ok("playwright", "installed in node_modules")
    _check_playwright_browsers()


def _check_node_tooling() -> None:
    _check_optional("node", "web UI and documentation tooling")
    _check_optional("npm", "installs web, Playwright and cspell dependencies")
    _check_local_binary("cspell", "documentation spelling")
    _check_playwright()


def _check_github_cli() -> None:
    if not _binary("gh"):
        warn("gh", "optional GitHub CLI not found")
        return
    completed = _run(["gh", "auth", "status"], timeout=15)
    if completed is not None and completed.returncode == 0:
        ok("gh auth")
    else:
        warn("gh auth", "not authenticated — run `gh auth login`")


def main() -> int:
    """Esegue tutti i controlli e stampa il report."""

    _check_python()
    _check_required("uv", "Python package/project manager")
    _check_required("just", "task runner")
    _check_required("git", "version control")
    _check_required("bash", "shell for hooks and scripts")
    _check_direnv()
    _check_install_state()
    _check_lockfile_coherence()
    _check_hooks()

    _check_optional("mise", "pinned tool installer")
    _check_node_tooling()
    _check_optional("gitleaks", "secret scanning")
    _check_optional("actionlint", "GitHub Actions syntax/semantics")
    _check_optional("zizmor", "GitHub Actions security")
    _check_optional("lychee", "link checking")
    _check_optional("shellcheck", "shell script linting")
    _check_optional("jq", "JSON inspection in scripts")
    _check_optional("parallel", "optional gate accelerator")
    _check_optional("codegraph", "optional code knowledge graph")
    _check_github_cli()

    icons: dict[Status, str] = {"ok": "✅", "warn": "⚠️ ", "fail": "❌"}
    for check in checks:
        suffix = f" — {check.detail}" if check.detail else ""
        print(f"{icons[check.status]} {check.label}{suffix}")

    return 1 if any(check.status == "fail" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
