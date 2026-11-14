set shell := ["bash", "-euo", "pipefail", "-c"]

# Regex autorevole del fast path docs-only (protetta da CODEOWNERS).
DOCS_ONLY_PATTERNS := '^(docs/|.*\.md$|\.github/workflows/|\.githooks/)'

# Lista dei comandi pubblici
default:
    @just --list

# ---------------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------------

# Installa i pacchetti di sistema e il toolchain pinnato in .mise.toml
install:
    sudo apt-get update
    sudo apt-get install -y bash ca-certificates curl git jq make parallel build-essential libssl-dev libffi-dev zlib1g-dev
    mise install
    npm ci
    uv python install

# Prima installazione o riallineamento completo
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    just install
    uv sync --locked
    git config core.hooksPath .githooks
    if [ ! -f .env ]; then cp .env.example .env; fi
    direnv allow
    if command -v codegraph >/dev/null 2>&1; then
      codegraph init >/dev/null 2>&1 || true
      codegraph index >/dev/null 2>&1 || true
    fi
    echo "Setup complete. Run: just doctor"

# Riallinea toolchain, dipendenze e indice CodeGraph dopo un pull
pull:
    #!/usr/bin/env bash
    set -euo pipefail
    git pull --rebase --autostash
    mise install
    npm ci
    uv sync --locked
    git config core.hooksPath .githooks
    if command -v codegraph >/dev/null 2>&1; then codegraph index >/dev/null 2>&1 || true; fi
    just doctor

# Verifica runtime, tool e configurazione
doctor:
    uv run python tools/scripts/doctor.py

# Avvia l'API in sviluppo con reload
dev:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run uvicorn py_boilerplate.entrypoints.api.main:build_app --factory --reload --host "${API_HOST:-127.0.0.1}" --port "${API_PORT:-8100}"

# Python del progetto
python:
    uv run python

# ---------------------------------------------------------------------------------
# Static analysis
# ---------------------------------------------------------------------------------

# Auto-fix di formattazione e lint
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Formattazione (read-only)
format-check:
    uv run ruff format --check .

# Lint
lint:
    uv run ruff check .

# Type checking autorevole (mypy strict)
typecheck:
    uv run mypy src tests tools

# Dipendenze inutilizzate e lockfile coerente
dead-code:
    uv run deptry .
    uv lock --check

# Regole architetturali e cicli (Import Linter)
arch:
    uv run lint-imports

# Markdown lint, spelling e link locali
docs-check:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run pymarkdown --config .pymarkdown.json scan -r --respect-gitignore -e "docs/init/**" docs src/py_boilerplate README.md AGENTS.md CONTRIBUTING.md SECURITY.md
    if command -v npx >/dev/null 2>&1 && [ -d node_modules ]; then
      npx --no-install cspell lint --no-progress
    else
      if [ "${CI:-}" = "true" ]; then
        echo "❌ cspell not installed in CI — run npm ci" >&2
        exit 1
      fi
      echo "⚠️  cspell not installed — skipping spelling check (blocking in CI; run npm ci)"
    fi
    if command -v lychee >/dev/null 2>&1; then
      lychee --offline --no-progress --include-fragments .
    else
      if [ "${CI:-}" = "true" ]; then
        echo "❌ lychee not found in CI — install the pinned toolchain with mise" >&2
        exit 1
      fi
      echo "⚠️  lychee not found — skipping local link check (blocking in CI; run \`mise install\`)"
    fi

# Sintassi e sicurezza dei workflow GitHub Actions
workflows-check:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v actionlint >/dev/null 2>&1; then
      actionlint
    else
      if [ "${CI:-}" = "true" ]; then
        echo "❌ actionlint not found in CI — install the pinned toolchain with mise" >&2
        exit 1
      fi
      echo "⚠️  actionlint not found — skipping (blocking in CI; run \`mise install\`)"
    fi
    if command -v zizmor >/dev/null 2>&1; then
      zizmor .
    else
      if [ "${CI:-}" = "true" ]; then
        echo "❌ zizmor not found in CI — install the pinned toolchain with mise" >&2
        exit 1
      fi
      echo "⚠️  zizmor not found — skipping (blocking in CI; run \`mise install\`)"
    fi

# Scansione segreti del working tree
secrets:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v gitleaks >/dev/null 2>&1; then
      gitleaks dir --redact --no-banner .
    else
      if [ "${CI:-}" = "true" ]; then
        echo "❌ gitleaks not found in CI — install the pinned toolchain with mise" >&2
        exit 1
      fi
      echo "⚠️  gitleaks not found — skipping secrets scan (blocking in CI; run \`mise install\`)"
    fi

# Scansione segreti del solo staged diff (pre-commit)
secrets-staged:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v gitleaks >/dev/null 2>&1; then
      gitleaks git --staged --redact --no-banner .
    else
      if [ "${CI:-}" = "true" ]; then
        echo "❌ gitleaks not found in CI — install the pinned toolchain with mise" >&2
        exit 1
      fi
      echo "⚠️  gitleaks not found — skipping staged secrets scan (blocking in CI; run \`mise install\`)"
    fi

# Lint degli script shell (bloccante in CI)
shell-check:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v shellcheck >/dev/null 2>&1; then
      shellcheck -e SC2329 -x bin/* tools/scripts/*.sh
    else
      if [ "${CI:-}" = "true" ]; then
        echo "❌ shellcheck not found in CI — install the pinned toolchain with mise" >&2
        exit 1
      fi
      echo "⚠️  shellcheck not found — skipping shell lint (blocking in CI; run \`mise install\`)"
    fi

# Vulnerabilità delle dipendenze e analisi statica di sicurezza
security:
    uv run pip-audit
    uv run bandit -q -r src

# ---------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------

# Suite unit
test-unit:
    uv run pytest tests/unit -q

# Suite integration e contract
test-integration:
    uv run pytest tests/integration tests/contract -q

# Contratto CLI e contratto condiviso tra superfici
test-contract:
    uv run pytest tests/contract -q

# Test collegati ai file Python staged (fallback conservativo: suite unit)
test-related:
    #!/usr/bin/env bash
    set -euo pipefail
    if git diff --cached --name-only | grep -qE '\.py$'; then
      uv run pytest tests/unit -q
    else
      echo "No staged Python changes — unit suite skipped."
    fi

# E2E su processi reali: CLI, API HTTP e MCP stdio
test-e2e:
    uv run pytest tests/e2e -m e2e -q

# Coverage con branch, poi gate a cricchetto
coverage:
    uv run pytest --cov=py_boilerplate --cov-report=term-missing --cov-report=json:coverage/coverage.json -q
    uv run python tools/scripts/coverage_gate.py

# Alza le soglie di coverage ai valori correnti (solo salita)
coverage-raise:
    uv run python tools/scripts/coverage_raise.py

# Smoke test del percorso pubblico più importante (≤ 20s)
smoke:
    uv run pytest tests/integration/test_smoke.py -q

# Compatibilità con tutte le versioni Python supportate
test-compat:
    #!/usr/bin/env bash
    set -euo pipefail
    uv python install 3.13 3.14
    for version in 3.13 3.14; do
      echo "==> Python ${version}"
      UV_PROJECT_ENVIRONMENT=".venv-${version}" uv run --python "${version}" pytest tests/unit tests/integration tests/contract -q
    done

# Build e installazione del wheel in un virtualenv pulito
package-check:
    bash tools/scripts/package-check.sh

# Guard report-only (docs, testing, type health, placeholder)
guards:
    uv run python tools/scripts/guards.py

# ---------------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------------

# Check rapidi su staged/related (pre-commit hook)
precommit:
    #!/usr/bin/env bash
    set -euo pipefail
    scope=$(uv run python tools/scripts/diff_scope.py --staged '{{ DOCS_ONLY_PATTERNS }}')
    if [ "$scope" = "docs-only" ]; then
      tools/scripts/run-checks.sh "just docs-check" "just workflows-check" "just secrets-staged"
      exit 0
    fi
    tools/scripts/run-checks.sh \
      "just format-check" \
      "just lint" \
      "just shell-check" \
      "just docs-check" \
      "just secrets-staged" \
      "just test-related"

# Analisi statica e suite principali (pre-push hook)
prepush:
    #!/usr/bin/env bash
    set -euo pipefail
    scope=$(uv run python tools/scripts/diff_scope.py --prepush '{{ DOCS_ONLY_PATTERNS }}')
    if [ "$scope" = "docs-only" ]; then
      tools/scripts/run-checks.sh "just docs-check" "just workflows-check" "just secrets"
      exit 0
    fi
    rc=0
    tools/scripts/run-checks.sh \
      "just format-check" \
      "just lint" \
      "just shell-check" \
      "just typecheck" \
      "just dead-code" \
      "just arch" \
      "just docs-check" \
      "just workflows-check" \
      "just secrets" \
      "just security" || rc=1
    tools/scripts/run-checks.sh \
      "just test-unit" \
      "just test-integration" \
      "just smoke" \
      "just coverage" || rc=1
    exit "$rc"

# Replica locale esatta della pipeline CI
ci: format-check lint shell-check typecheck dead-code arch docs-check workflows-check secrets security
    just test-unit
    just test-integration
    just test-contract
    just coverage
    just smoke
    just test-e2e
    just package-check
    just test-compat
