"""Alza le soglie di coverage al valore corrente (cricchetto, solo salita).

Eseguire `just coverage` prima: lo script legge `coverage/coverage.json`.
Non abbassa mai una soglia, nemmeno se il valore corrente è inferiore.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

THRESHOLDS_PATH = Path("coverage-thresholds.json")
COVERAGE_PATH = Path("coverage/coverage.json")


def _load_object(path: Path) -> dict[str, object]:
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return raw


def _object(data: dict[str, object], key: str, path: Path) -> dict[str, object]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: missing object '{key}'")
    return value


def _number(data: dict[str, object], key: str, path: Path) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SystemExit(f"{path}: missing numeric field '{key}'")
    return float(value)


def main() -> int:
    """Aggiorna le soglie e stampa la differenza."""

    thresholds = _load_object(THRESHOLDS_PATH)
    coverage = _load_object(COVERAGE_PATH)
    totals = _object(coverage, "totals", COVERAGE_PATH)

    current_lines = _number(totals, "percent_statements_covered", COVERAGE_PATH)
    current_branches = _number(totals, "percent_branches_covered", COVERAGE_PATH)

    old_lines = int(_number(thresholds, "lines", THRESHOLDS_PATH))
    old_branches = int(_number(thresholds, "branches", THRESHOLDS_PATH))
    new_lines = max(old_lines, math.floor(current_lines))
    new_branches = max(old_branches, math.floor(current_branches))

    updated = {
        "lines": new_lines,
        "branches": new_branches,
    }
    raised = new_lines > old_lines or new_branches > old_branches

    print(f"lines:    {old_lines} -> {new_lines} (current {current_lines:.2f}%)")
    print(f"branches: {old_branches} -> {new_branches} (current {current_branches:.2f}%)")

    if not raised:
        print("Nothing to raise.")
        return 0

    THRESHOLDS_PATH.write_text(
        json.dumps(updated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Thresholds raised. Commit coverage-thresholds.json with the change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
