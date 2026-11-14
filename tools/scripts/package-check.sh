#!/usr/bin/env bash
# package-check.sh — build e verifica del wheel in un virtualenv pulito.
#
# Verifica che il package sia installabile fuori dal repository, che gli entry
# point funzionino e che non ci sia import shadowing dal working tree.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$root"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

python_version=$(cat .python-version)

echo "==> build sdist + wheel"
uv build --out-dir "$work/dist" >/dev/null
wheel=$(find "$work/dist" -maxdepth 1 -name '*.whl' -print -quit)
if [ -z "$wheel" ]; then
  echo "ERROR: wheel not found in $work/dist" >&2
  exit 1
fi

echo "==> install wheel in a clean venv (Python ${python_version})"
uv venv --python "$python_version" "$work/venv" >/dev/null
uv pip install --python "$work/venv/bin/python" "$wheel" >/dev/null

echo "==> import from outside the repository"
(
  cd "$work"
  installed=$("$work/venv/bin/python" -c 'import py_boilerplate; print(py_boilerplate.__file__)')
  case "$installed" in
    "$work"/venv/*) echo "ok: $installed" ;;
    *) echo "ERROR: imported from unexpected path: $installed" >&2; exit 1 ;;
  esac
)

echo "==> console script"
output=$("$work/venv/bin/py-boilerplate" hello-world --json)
printf '%s\n' "$output"
compact=$(printf '%s' "$output" | tr -d '[:space:]')
if [ "$compact" != '{"message":"Hello,world!"}' ]; then
  echo "ERROR: unexpected CLI output: $compact" >&2
  exit 1
fi

echo "package-check: PASS"
