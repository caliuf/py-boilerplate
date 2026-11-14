# Progetto

`py-boilerplate` è un boilerplate Python agent-first. Dimostra un caso d'uso minimo, `hello-world`, esposto su tre superfici coordinate e protetto da un sistema di guide, gate e guard. Serve come punto di partenza verificato per nuovi progetti, non come framework generico.

## Obiettivo

Fornire una base Python che un agente possa estendere senza degradare il repository: architettura esplicita, validazione ai confini, typing rigoroso, test comportamentali, packaging riproducibile e gate che impediscono scorciatoie.

## Non-obiettivi

- Non è un framework applicativo né una libreria pubblica.
- Non include un database, una coda, un worker o un frontend browser.
- Non integra servizi esterni o LLM a runtime.
- Non pubblica wheel o immagini: il package check è locale e in CI.
- Non sostituisce le decisioni di prodotto o architettura di un progetto derivato.

## Superfici

| Superficie | Tipo | Input | Output | Note |
|---|---|---|---|---|
| CLI | adapter driving | `py-boilerplate hello-world [--name <name>] [--json]` | JSON o testo su stdout; errori su stderr | JSON di default in non-TTY; exit code stabili |
| API HTTP | adapter driving | `GET /api/hello-world?name=<name>` | JSON `{"message": "..."}` oppure `application/problem+json` | FastAPI, sync handler, nessuno stato globale |
| MCP | adapter driving | tool `hello_world` con `name: string` | structured content `{"message": "..."}` | stdio, tool read-only e idempotente |

Il comando CLI è registrato in `src/py_boilerplate/entrypoints/cli/registry.py`. La route è in `src/py_boilerplate/entrypoints/api/routes/hello_world.py`. Il tool è in `src/py_boilerplate/entrypoints/mcp/tools/hello_world.py`.

## Bounded context

Il progetto ha un solo bounded context, `greetings`:

- `domain/` contiene il value object `Greeting` e la funzione pura `greet`.
- `application/` contiene il caso d'uso `say_hello`, con dipendenze esplicite.
- `ports/` espone la porta `Logger`.
- `adapters/` implementa le porte verso structlog.
- `contracts/` è la foglia condivisa: `HelloWorldInput`, `HelloWorldOutput`, `ErrorCode`, `ProblemDetails` e il `Logger` Protocol.

Il dettaglio è in [`docs/architecture/OVERVIEW.md`](architecture/OVERVIEW.md) e [`docs/architecture/BOUNDARIES.md`](architecture/BOUNDARIES.md).

## Deployable

La distribuzione è una sola, `py-boilerplate`, con tre entry point:

- `py-boilerplate` — CLI.
- `py-boilerplate-api` — API HTTP.
- `py-boilerplate-mcp` — server MCP stdio.

Non esistono servizi separati, code, database o job schedulati. Le tre superfici condividono lo stesso wheel e lo stesso caso d'uso.

## Versioni e dipendenze

- `requires-python = ">=3.13"`.
- Versione pinnata in `.python-version`: `3.14.5`.
- CI: matrix Python 3.13 e 3.14.
- Gestione dipendenze: `uv` con `uv.lock` versionato; nessun `requirements.txt` manuale.
- Dipendenze runtime: FastAPI, MCP Python SDK, Pydantic, pydantic-settings, structlog, Uvicorn.
- Dipendenze di sviluppo: pytest, coverage, mypy, Ruff, Import Linter, deptry, Bandit, pip-audit, pymarkdown, cspell (tool Node per la documentazione), httpx.

## Dati e confini esterni

- Non esiste un data store.
- Non esistono chiamate a servizi esterni a runtime.
- L'unico input esterno è quello delle superfici: argomenti CLI, query string HTTP e argomenti del tool MCP.
- Tutti gli input sono validati a runtime con Pydantic o con lo schema del tool MCP prima di raggiungere il caso d'uso.
- I log non contengono segreti né dati personali. L'evento `saying hello` registra solo il nome validato.

## Flussi critici

1. **CLI felice**: parsing → validazione `HelloWorldInput` → `say_hello` → log su stderr → JSON o testo su stdout → exit 0.
2. **CLI invalida**: nome vuoto, troppo lungo o flag sconosciuto → errore `VALIDATION` su stderr → exit 2.
3. **API felice**: query string → validazione → `say_hello` → 200 JSON.
4. **API invalida**: nome vuoto o troppo lungo → 400 `application/problem+json` con codice `VALIDATION`.
5. **MCP felice**: schema del tool → `say_hello` → structured content.
6. **MCP invalido**: schema del tool rifiuta l'input → tool error con `isError: true`.
7. **Package**: build del wheel → installazione in venv pulito → import fuori dal repository → entry point CLI funzionante.

## Mappa dei comandi

| Comando | Scopo |
|---|---|
| `just setup` | Installa toolchain, sincronizza il lock, attiva hook e `.envrc` |
| `just doctor` | Verifica runtime, tool, lockfile, hook e `.envrc` |
| `just dev` | Avvia l'API con reload |
| `just precommit` | Gate rapidi su staged/related |
| `just prepush` | Analisi statica e suite principali |
| `just ci` | Replica locale della pipeline CI |
| `just test-unit` | Suite unit |
| `just test-integration` | Suite integration e contract |
| `just test-contract` | Contratto CLI e contratto cross-surface |
| `just test-e2e` | Processi reali per CLI, API e MCP |
| `just coverage` | Coverage con branch e gate a cricchetto |
| `just coverage-raise` | Alza le soglie ai valori correnti |
| `just smoke` | Smoke test del percorso pubblico |
| `just package-check` | Build e installazione del wheel |
| `just guards` | Guard report-only |
| `just docs-check` | Markdown, spelling e link locali |
| `just workflows-check` | actionlint e zizmor |
| `just secrets` | Gitleaks sul working tree |
| `just security` | pip-audit e Bandit |

## Budget dei gate

| Gate | Budget | Note |
|---|---|---|
| `just precommit` | 10 secondi | Solo check rapidi e unit test |
| `just prepush` | 60 secondi | Analisi statica e suite principali |
| `just ci` | 10 minuti | Include E2E, package check e compatibilità Python |
| Suite completa | 10 minuti | Guard di testing |
| Coverage | 95% linee, 90% branch | Baseline iniziale; può solo salire |

Il tempo effettivo della suite locale è di pochi secondi; i budget sono un tetto, non un obiettivo.

## Stato delle feature

| Feature | Stato | Evidenza |
|---|---|---|
| Dominio e caso d'uso `hello-world` | Stabile | Unit e integration test |
| CLI agent-first | Stabile | Contract test su processo reale |
| API HTTP con Problem Details | Stabile | Integration test |
| Tool MCP read-only | Stabile | Integration in-memory ed E2E stdio |
| Package e entry point | Stabile | `just package-check` |
| Memory bank | Stabile | `docs/memory/` |
| Guard report-only | Stabile | `just guards` e `scheduled.yml` |
| UI browser | Assente per decisione | ADR-0006 |
| Data store, code, worker | Assenti per decisione | Non-obiettivi |

## Decisioni aperte

- Licenza del repository: non ancora scelta dal maintainer.
- Progetto CodeScene: non configurato per questo repository; l'integrazione è opzionale e non è un gate.
- Pubblicazione del package: non prevista; il package check resta obbligatorio.

Le decisioni chiuse sono nelle ADR e nelle PDR. Ogni nuova decisione significativa va registrata prima o insieme al codice che la implementa.
