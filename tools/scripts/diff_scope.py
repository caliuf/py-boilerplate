"""`diff-scope` — decide se il diff è docs-only o richiede i gate completi.

Uso:
  uv run python tools/scripts/diff_scope.py --staged  <regex>...
  uv run python tools/scripts/diff_scope.py --prepush <regex>...

Stampa esattamente `docs-only` o `full` su stdout. Ogni dubbio (nessun git,
nessun upstream, diff vuoto, pattern assenti) risolve in `full`: è il percorso
sicuro. La lista autorevole dei pattern vive nel justfile ed è protetta da
CODEOWNERS.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


def _git(args: Sequence[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except OSError, subprocess.SubprocessError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def _git_lines(args: Sequence[str]) -> list[str] | None:
    output = _git(args)
    if output is None:
        return None
    return [line for line in output.splitlines() if line]


def _staged_files() -> list[str] | None:
    return _git_lines(["diff", "--cached", "--name-only", "--diff-filter=ACMRD"])


def _working_tree_files() -> list[str] | None:
    unstaged = _git_lines(["diff", "--name-only", "--diff-filter=ACMRD"])
    staged = _staged_files()
    untracked = _git_lines(["ls-files", "--others", "--exclude-standard"])
    if unstaged is None or staged is None or untracked is None:
        return None
    return sorted(set(unstaged) | set(staged) | set(untracked))


def _upstream_files() -> list[str] | None:
    upstream = _git(["rev-parse", "--abbrev-ref", "@{upstream}"])
    if upstream is None or not upstream.strip():
        return None
    return _git_lines(["diff", "--name-only", f"{upstream.strip()}...HEAD", "--diff-filter=ACMRD"])


def _merge_base_files() -> list[str] | None:
    for base in ("origin/main", "main", "origin/master", "master"):
        merge_base = _git(["merge-base", base, "HEAD"])
        if merge_base is None or not merge_base.strip():
            continue
        files = _git_lines(
            ["diff", "--name-only", f"{merge_base.strip()}...HEAD", "--diff-filter=ACMRD"]
        )
        if files is not None:
            return files
    return None


def _changed_files(mode: str) -> list[str] | None:
    if mode == "--staged":
        return _staged_files()
    baseline = _upstream_files()
    if baseline is None:
        baseline = _merge_base_files()
    local = _working_tree_files()
    if baseline is None or local is None:
        return None
    return sorted(set(baseline) | set(local))


def main(argv: Sequence[str]) -> int:
    """Stampa docs-only o full e restituisce sempre 0."""

    mode = next((arg for arg in argv if arg in ("--staged", "--prepush")), None)
    patterns = [re.compile(arg) for arg in argv if not arg.startswith("--")]
    if mode is None or not patterns:
        print("full")
        return 0

    files = _changed_files(mode)
    if not files:
        print("full")
        return 0

    docs_only = all(any(pattern.search(file) for pattern in patterns) for file in files)
    print("docs-only" if docs_only else "full")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
