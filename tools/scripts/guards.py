"""`just guards` — procedure di fallback report-only.

I guard non modificano mai il codice e non fanno auto-fix: producono un report
che `scheduled.yml` trasforma in issue. Exit code sempre 0.
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from py_boilerplate.entrypoints.cli.registry import COMMANDS

ROOT = Path(__file__).resolve().parents[2]
TEST_BUDGET_SECONDS = 10 * 60
_RECIPE_RE = re.compile(r"^([a-z][a-z0-9-]*)(?:\s[^:]*)?:")
_CITED_RECIPE_RE = re.compile(r"`just ([a-z][a-z0-9-]*)`")
_LINK_RE = re.compile(r"\]\(([^)]+\.md)\)")
_SUPPRESSION_RE = re.compile(
    r"#\s*(?:type:\s*ignore(?:\[[^\]]*\])?|noqa(?:\[[^\]]*\])?|nosec|pragma:\s*no\s+cover)\b",
)
_SKIP_PARTS = {".venv", "tmp", "coverage", "dist", "build", "node_modules"}


@dataclass(frozen=True, slots=True)
class Finding:
    """Problema rilevato da un guard."""

    guard: str
    message: str


findings: list[Finding] = []
notes: list[str] = []


def _markdown_files() -> list[Path]:
    files: list[Path] = []
    docs = ROOT / "docs"
    if docs.is_dir():
        for path in docs.rglob("*.md"):
            if "init" in path.parts or _SKIP_PARTS & set(path.parts):
                continue
            files.append(path)
    for name in ("README.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md"):
        path = ROOT / name
        if path.is_file():
            files.append(path)
    return files


def _justfile_recipes() -> set[str]:
    path = ROOT / "justfile"
    if not path.is_file():
        findings.append(Finding("docs", "justfile is missing"))
        return set()
    recipes: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _RECIPE_RE.match(line)
        if match is not None:
            recipes.add(match.group(1))
    return recipes


def _docs_guard() -> None:
    recipes = _justfile_recipes()
    cited: set[str] = set()
    for path in _markdown_files():
        text = path.read_text(encoding="utf-8")
        for recipe in _CITED_RECIPE_RE.findall(text):
            cited.add(recipe)
            if recipe not in recipes:
                relative = path.relative_to(ROOT)
                findings.append(
                    Finding(
                        "docs",
                        f"`{relative}` cites `just {recipe}`, missing from the justfile",
                    )
                )
    notes.append(f"docs guard: checked {len(cited)} cited recipes against the justfile")

    project = ROOT / "docs/PROJECT.md"
    if not project.is_file():
        findings.append(Finding("docs", "docs/PROJECT.md is missing"))
    else:
        project_text = project.read_text(encoding="utf-8")
        for command in COMMANDS:
            if command.name not in project_text:
                findings.append(
                    Finding(
                        "docs",
                        f"CLI command `{command.name}` is missing from the surface map "
                        "in docs/PROJECT.md",
                    )
                )

    _check_decision_index(
        ROOT / "docs/architecture/adr/README.md",
        ROOT / "docs/architecture/adr",
        "ADR",
    )
    _check_decision_index(
        ROOT / "docs/product/pdr/README.md",
        ROOT / "docs/product/pdr",
        "PDR",
    )


def _check_decision_index(index: Path, directory: Path, kind: str) -> None:
    if not index.is_file() or not directory.is_dir():
        findings.append(Finding("docs", f"{kind} index or directory is missing"))
        return
    indexed = {
        link for link in _LINK_RE.findall(index.read_text(encoding="utf-8")) if link != "README.md"
    }
    for link in indexed:
        if not (directory / link).is_file():
            findings.append(Finding("docs", f"{kind} index points to missing record {link}"))
    for record in sorted(directory.glob("*.md")):
        if record.name != "README.md" and record.name not in indexed:
            findings.append(
                Finding("docs", f"{kind} record {record.name} is missing from its index")
            )


def _testing_guard() -> None:
    started = time.monotonic()
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=TEST_BUDGET_SECONDS + 60,
        check=False,
    )
    elapsed = time.monotonic() - started
    notes.append(f"testing guard: suite completed in {elapsed:.0f}s")
    if completed.returncode != 0:
        findings.append(Finding("testing", "the test suite is RED — restore health first"))
    if elapsed > TEST_BUDGET_SECONDS:
        findings.append(
            Finding("testing", f"test suite took {elapsed:.0f}s, over the 10 minute budget")
        )


def _web_guard() -> None:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            ["npm", "run", "web:check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        findings.append(Finding("web", f"could not run web:check: {exc}"))
        return
    elapsed = time.monotonic() - started
    notes.append(f"web guard: web:check completed in {elapsed:.0f}s")
    if completed.returncode != 0:
        findings.append(Finding("web", "web:check is RED — restore the web app health"))


def _type_health_guard() -> None:
    source = ROOT / "src"
    any_count = 0
    cast_count = 0
    suppressions = 0
    for path in source.rglob("*.py"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            any_count += len(re.findall(r"\bAny\b", line))
            cast_count += line.count("cast(")
            match = _SUPPRESSION_RE.search(line)
            if match is None:
                continue
            suppressions += 1
            if not line[match.end() :].strip():
                relative = path.relative_to(ROOT)
                findings.append(
                    Finding(
                        "type-health",
                        f"{relative}:{number} has a suppression without a reason",
                    )
                )
    notes.append(
        "type-health guard: "
        f"{any_count} `Any`, {cast_count} `cast(`, {suppressions} reasoned suppressions"
    )


def _placeholder_guards() -> None:
    notes.append("performance guard: not applicable yet (no probes in the codebase)")
    notes.append("localization guard: not applicable yet (no i18n)")
    notes.append("telemetry guard: not applicable yet (no product analytics)")
    notes.append("concurrency guard: not applicable yet (no background tasks or queues)")
    notes.append("package guard: uv.lock coherence is a blocking gate, not a report-only guard")


def main() -> int:
    """Esegue i guard e stampa un report Markdown."""

    _docs_guard()
    _testing_guard()
    _web_guard()
    _type_health_guard()
    _placeholder_guards()

    print("# Guards report\n")
    print(f"Date: {datetime.now(UTC).isoformat()}\n")
    if findings:
        print("## Findings\n")
        for finding in findings:
            print(f"- ❌ [{finding.guard}] {finding.message}")
        print()
    else:
        print("No findings. ✅\n")
    print("## Notes\n")
    for note in notes:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
