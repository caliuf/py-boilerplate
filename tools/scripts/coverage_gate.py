"""Gate di coverage a cricchetto.

Legge `coverage/coverage.json` (prodotto da `coverage json`) e confronta le
percentuali di statement e branch con `coverage-thresholds.json`.
"""

from __future__ import annotations

import json
import sys
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
    """Restituisce 0 se tutte le soglie sono rispettate, 1 altrimenti."""

    thresholds = _load_object(THRESHOLDS_PATH)
    coverage = _load_object(COVERAGE_PATH)
    totals = _object(coverage, "totals", COVERAGE_PATH)

    lines = _number(totals, "percent_statements_covered", COVERAGE_PATH)
    branches = _number(totals, "percent_branches_covered", COVERAGE_PATH)
    required_lines = _number(thresholds, "lines", THRESHOLDS_PATH)
    required_branches = _number(thresholds, "branches", THRESHOLDS_PATH)

    failures: list[str] = []
    if lines < required_lines:
        failures.append(f"lines {lines:.2f}% < {required_lines:.2f}%")
    if branches < required_branches:
        failures.append(f"branches {branches:.2f}% < {required_branches:.2f}%")

    print(
        f"coverage gate: lines {lines:.2f}% (min {required_lines:.2f}%), "
        f"branches {branches:.2f}% (min {required_branches:.2f}%)"
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        print("Never lower thresholds: restore coverage or raise the baseline explicitly.")
        return 1
    print("coverage gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
