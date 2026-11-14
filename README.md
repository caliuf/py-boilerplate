# py-boilerplate

Boilerplate Python per progetti sviluppati interamente tramite agenti AI. Il repository dimostra un caso d'uso minimo, `hello-world`, esposto su tre superfici coordinate: CLI, API HTTP e tool MCP. Il codice è tipizzato, validato a runtime ai confini, testato con TDD e protetto da gate locali e in CI.

Il progetto è derivato da [`ts-boilerplate`](https://github.com/caliuf/ts-boilerplate) e applica il [`Vademecum Python`](docs/init/Vademecum%20Python.md) conservato in `docs/init/`. Il Vademecum è il blueprint congelato: non si modifica durante lo sviluppo ordinario.

## Quick start

```bash
git clone https://github.com/caliuf/py-boilerplate.git
cd py-boilerplate
just setup
just doctor
```

`just setup` installa il toolchain pinnato, sincronizza `uv.lock`, attiva gli hook versionati e autorizza `.envrc`. Se `mise` non è disponibile, installalo seguendo [`docs/development/GETTING-STARTED.md`](docs/development/GETTING-STARTED.md).

Avvia l'API in sviluppo:

```bash
just dev
```

Esegui il caso d'uso dalla CLI:

```bash
uv run py-boilerplate hello-world --name Ada --json
```

Oppure dal wrapper che carica l'environment del chiamante:

```bash
bin/py-boilerplate-hello-world --name Ada --json
```

## Comandi principali

| Comando | Cosa fa |
|---|---|
| `just setup` | Prima installazione o riallineamento completo |
| `just doctor` | Verifica runtime, tool, lockfile, hook e `.envrc` |
| `just dev` | Avvia l'API con reload |
| `just precommit` | Gate rapidi su staged/related (hook di commit) |
| `just prepush` | Analisi statica e suite principali (hook di push) |
| `just ci` | Replica locale della pipeline CI |
| `just coverage` | Coverage con branch e gate a cricchetto |
| `just guards` | Guard report-only: docs, testing, type health |
| `just package-check` | Build e installazione del wheel in un venv pulito |

La mappa completa delle recipe e delle superfici è in [`docs/PROJECT.md`](docs/PROJECT.md).

## Architettura in breve

Il progetto è un modular monolith in una singola distribuzione Python:

- `src/py_boilerplate/contracts/` è la foglia condivisa: DTO Pydantic, tassonomia errori, porta `Logger`.
- `src/py_boilerplate/greetings/` contiene il bounded context `greetings`, diviso in dominio puro, application layer e porte.
- `src/py_boilerplate/adapters/` implementa le porte verso tecnologie esterne, oggi structlog.
- `src/py_boilerplate/entrypoints/` contiene i composition root e gli adapter driving: CLI, API FastAPI e server MCP.
- `tests/` contiene unit, integration, contract ed E2E; `tests/support/` ospita i test double, mai importabili da `src/`.

La direzione delle dipendenze è verificata da Import Linter: `entrypoints → adapters → application → ports → domain`, con `contracts` come foglia. I dettagli sono in [`docs/architecture/OVERVIEW.md`](docs/architecture/OVERVIEW.md) e [`docs/architecture/BOUNDARIES.md`](docs/architecture/BOUNDARIES.md).

## Qualità e sicurezza

Il progetto adotta il modello 3G del Vademecum:

- **Guide**: [`AGENTS.md`](AGENTS.md), [`docs/PROJECT.md`](docs/PROJECT.md), ADR e PDR.
- **Gate**: Ruff, mypy strict, pytest con coverage, Import Linter, deptry, pymarkdown, cspell, lychee, actionlint, zizmor, gitleaks, bandit, pip-audit.
- **Guard**: `just guards` produce un report che la CI schedulata trasforma in issue, senza auto-fix.

Le soglie di coverage vivono in [`coverage-thresholds.json`](coverage-thresholds.json) e possono solo salire. I file che definiscono i gate sono protetti da [`CODEOWNERS`](.github/CODEOWNERS).

## Documentazione

| Documento | Contenuto |
|---|---|
| [`docs/INDEX.md`](docs/INDEX.md) | Indice gerarchico e ordine di lettura |
| [`docs/PROJECT.md`](docs/PROJECT.md) | Obiettivi, non-obiettivi, superfici, vincoli e comandi |
| [`docs/architecture/OVERVIEW.md`](docs/architecture/OVERVIEW.md) | Architettura e modello di dipendenze |
| [`docs/architecture/BOUNDARIES.md`](docs/architecture/BOUNDARIES.md) | Contratti Import Linter e regole di confine |
| [`docs/development/GETTING-STARTED.md`](docs/development/GETTING-STARTED.md) | Bootstrap, primo task e troubleshooting |
| [`docs/development/CODING.md`](docs/development/CODING.md) | Convenzioni Python, typing, validazione, logging |
| [`docs/development/TESTING.md`](docs/development/TESTING.md) | Strategia di test, coverage e contratti |
| [`docs/development/WORKFLOWS.md`](docs/development/WORKFLOWS.md) | Ciclo di lavoro, gate, PR e Definition of Done |
| [`docs/memory/project.md`](docs/memory/project.md) | Memoria operativa portabile del progetto |

## Adozione come nuovo progetto

`py-boilerplate` contiene placeholder deliberati: il nome del package, il comando `hello-world`, il prefisso degli errori e il maintainer in `CODEOWNERS`. La checklist di adozione è in [`docs/development/NEW-PROJECT.md`](docs/development/NEW-PROJECT.md).

## Licenza

Il repository non include ancora una licenza. Prima di riutilizzare il codice in un progetto pubblico o commerciale, aggiungi la licenza scelta dal maintainer.
