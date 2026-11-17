# Progetto

`py-boilerplate` è un boilerplate Python agent-first. Dimostra un caso d'uso minimo, `hello-world`, esposto su quattro superfici coordinate — CLI, API HTTP, MCP e UI web — e protetto da un sistema di guide, gate e guard. Serve come punto di partenza verificato per nuovi progetti, non come framework generico.

## Obiettivo

Fornire una base Python che un agente possa estendere senza degradare il repository: architettura esplicita, validazione ai confini, typing rigoroso, test comportamentali, packaging riproducibile e gate che impediscono scorciatoie. La UI web è un deployable separato che consuma l'API, non una seconda implementazione del dominio.

## Non-obiettivi

- Non è un framework applicativo né una libreria pubblica.
- Non include un database, una coda o un worker.
- Non include SSR, autenticazione web, routing o stato globale nella UI.
- Non integra servizi esterni o LLM a runtime.
- Non pubblica wheel, immagini o bundle web: il package check e la build restano locali e in CI.
- Non sostituisce le decisioni di prodotto o architettura di un progetto derivato.

## Superfici

| Superficie | Tipo | Input | Output | Note |
|---|---|---|---|---|
| CLI | adapter driving | `py-boilerplate hello-world [--name <name>] [--json]` | JSON o testo su stdout; errori su stderr | JSON di default in non-TTY; exit code stabili |
| API HTTP | adapter driving | `GET /api/hello-world?name=<name>` | JSON `{"message": "..."}` oppure `application/problem+json` | FastAPI, sync handler, nessuno stato globale |
| MCP | adapter driving | tool `hello_world` con `name: string` | structured content `{"message": "..."}` | stdio, tool read-only e idempotente |
| Web UI | adapter driving browser | campo "Name" + invio o bottone "Greet" | messaggio o errore a schermo, tema chiaro/scuro | React/Vite su 5100 o successiva libera, proxy `/api` su 8100; design system Tailwind + shadcn/Base UI |

Il comando CLI è registrato in `src/py_boilerplate/entrypoints/cli/registry.py`. La route è in `src/py_boilerplate/entrypoints/api/routes/hello_world.py`. Il tool è in `src/py_boilerplate/entrypoints/mcp/tools/hello_world.py`. La UI è in `apps/web/`.

## Bounded context

Il progetto ha un solo bounded context, `greetings`:

- `domain/` contiene il value object `Greeting` e la funzione pura `greet`.
- `application/` contiene il caso d'uso `say_hello`, con dipendenze esplicite.
- `ports/` espone la porta `Logger`.
- `adapters/` implementa le porte verso structlog.
- `contracts/` è la foglia condivisa: `HelloWorldInput`, `HelloWorldOutput`, `ErrorCode`, `ProblemDetails` e il `Logger` Protocol.

Il dettaglio è in [`docs/architecture/OVERVIEW.md`](architecture/OVERVIEW.md) e [`docs/architecture/BOUNDARIES.md`](architecture/BOUNDARIES.md).

## Deployable

Il backend è una distribuzione Python, `py-boilerplate`, con tre entry point:

- `py-boilerplate` — CLI.
- `py-boilerplate-api` — API HTTP.
- `py-boilerplate-mcp` — server MCP stdio.

La UI è un deployable statico separato in `apps/web/`, costruito con Vite. In sviluppo parla all'API tramite il proxy Vite; in produzione va servita dallo stesso origin dell'API o dietro un reverse proxy che espone `/api`.

Non esistono servizi separati, code, database o job schedulati. Le superfici condividono lo stesso caso d'uso; la UI condivide il contratto tramite HTTP e OpenAPI, non tramite import Python.

## Versioni e dipendenze

- `requires-python = ">=3.14"`.
- Versione pinnata in `.python-version`: `3.14.6`.
- CI: Python 3.14.
- Node: `26.13.1` (Active LTS), richiesto per la UI, Playwright e cspell.
- Gestione dipendenze Python: `uv` con `uv.lock` versionato; nessun `requirements.txt` manuale.
- Gestione dipendenze web: npm workspace con `package-lock.json` versionato.
- Dipendenze runtime Python: FastAPI, MCP Python SDK, Pydantic, pydantic-settings, structlog, Uvicorn.
- Dipendenze web: React 19, ReactDOM 19, Zod 4, Tailwind CSS 4, shadcn/ui con Base UI, Lucide React, CVA, `cn`, Sonner.
- Dipendenze di sviluppo web: Vite 8, TypeScript 7, Vitest 5 con jsdom e Testing Library, Playwright con axe-core, Biome, Oxlint type-aware con `jsx-a11y`.
- Dipendenze di sviluppo Python: pytest, coverage, mypy, Ruff, Import Linter, deptry, Bandit, pip-audit, pymarkdown, cspell, httpx.

## Dati e confini esterni

- Non esiste un data store.
- Non esistono chiamate a servizi esterni a runtime.
- Gli input esterni sono: argomenti CLI, query string HTTP, argomenti del tool MCP e campo della UI.
- Tutti gli input sono validati a runtime con Pydantic o con lo schema del tool MCP prima di raggiungere il caso d'uso. La UI valida a sua volta le risposte con Zod.
- I log non contengono segreti né dati personali. L'evento `saying hello` registra solo il nome validato.
- CodeScene è uno strumento di sviluppo: non è raggiunto a runtime dall'applicazione.

## Flussi critici

1. **CLI felice**: parsing → validazione `HelloWorldInput` → `say_hello` → log su stderr → JSON o testo su stdout → exit 0.
2. **CLI invalida**: nome vuoto, troppo lungo o flag sconosciuto → errore `VALIDATION` su stderr → exit 2.
3. **API felice**: query string → validazione → `say_hello` → 200 JSON.
4. **API invalida**: nome vuoto o troppo lungo → 400 `application/problem+json` con codice `VALIDATION`.
5. **MCP felice**: schema del tool → `say_hello` → structured content.
6. **MCP invalido**: schema del tool rifiuta l'input → tool error con `isError: true`.
7. **Web felice**: input o bottone → fetch `/api/hello-world` → validazione Zod → messaggio a schermo con stato di successo accessibile.
8. **Web invalido**: nome vuoto → 400 Problem Details → messaggio di errore a schermo con stato di errore accessibile.
9. **Web tema**: preferenza di sistema o toggle → classe `light`/`dark` prima del primo paint → scelta persistita ai reload.
10. **Package**: build del wheel → installazione in venv pulito → import fuori dal repository → entry point CLI funzionante.
11. **Web build**: Vite build → bundle statico con CSS Tailwind, senza errori TypeScript.
12. **Web quality**: lint CSS/TSX, typecheck, test component, build e audit axe sui flussi critici.

## Mappa dei comandi

| Comando | Scopo |
|---|---|
| `just setup` | Installa toolchain, dipendenze Python/web, browser Playwright, hook e `.envrc` |
| `just doctor` | Verifica runtime, tool, lockfile, hook, browser e `.envrc` |
| `just dev` | Avvia API e web in sviluppo con reload |
| `just precommit` | Gate rapidi su staged/related, incluso CodeScene safeguard |
| `just prepush` | Analisi statica, web check, CodeScene changeset e suite principali |
| `just ci` | Replica locale della pipeline CI |
| `just test-unit` | Suite unit Python |
| `just test-integration` | Suite integration e contract Python |
| `just test-contract` | Contratto CLI, cross-surface e contratto web |
| `just test-e2e` | Processi reali CLI/API/MCP e UI web con Playwright |
| `just web-dev` | Solo dev server Vite; richiede l'API già attiva (usa `just dev` per entrambi) |
| `just web-build` | Build Vite della UI senza budget |
| `just web-typecheck` | TypeScript strict di app e test E2E |
| `just web-test` | Test Vitest di contratti, hook e componenti della UI |
| `just web-check` | Biome, Oxlint, typecheck e Vitest della UI |
| `just build` | Build di produzione della UI; inclusa in prepush e CI |
| `just coverage` | Coverage Python con branch e gate a cricchetto |
| `just coverage-raise` | Alza le soglie Python ai valori correnti |
| `just smoke` | Smoke test del percorso pubblico |
| `just package-check` | Build e installazione del wheel |
| `just codescene-safeguard` | CodeScene sui file staged/modificati |
| `just codescene-changeset` | CodeScene sul change-set del branch |
| `just codescene-ratchet` | Ratchet Hotspot/Average del progetto Cloud |
| `just guards` | Guard report-only |
| `just docs-check` | Markdown, spelling e link locali |
| `just workflows-check` | actionlint e zizmor |
| `just secrets` | Gitleaks sul working tree |
| `just security` | pip-audit, Bandit e npm audit |

## Budget dei gate

| Gate | Budget | Note |
|---|---|---|
| `just precommit` | 10 secondi | Check rapidi, web check, unit test e CodeScene safeguard |
| `just prepush` | 60 secondi | Analisi statica, web check, build, CodeScene changeset e suite principali |
| `just ci` | 10 minuti | Include E2E Python, Playwright, package check e compatibilità Python |
| Suite completa | 10 minuti | Guard di testing e web |
| Coverage Python | 95% linee, 90% branch | Baseline iniziale; può solo salire |
| CodeScene | Hotspot 9.10, Average 9.76 | Baseline 2026-11-14; può solo salire |
| Budget web (gzip) | CSS 20 KB, JavaScript 220 KB, totale 240 KB | Baseline 2026-11-16; può solo migliorare o essere aggiornata con ADR |

I budget sono un tetto, non un obiettivo. CodeScene e Playwright possono richiedere rete o browser e sono misurati a parte.

## Stato delle feature

| Feature | Stato | Evidenza |
|---|---|---|
| Dominio e caso d'uso `hello-world` | Stabile | Unit e integration test |
| CLI agent-first | Stabile | Contract test su processo reale |
| API HTTP con Problem Details | Stabile | Integration test |
| Tool MCP read-only | Stabile | Integration in-memory ed E2E stdio |
| UI web React/Vite con design system | Stabile | Vitest component, Playwright, axe e contract test web |
| Package e entry point | Stabile | `just package-check` |
| CodeScene Code Health | Attivo | `just codescene-safeguard` e `just codescene-changeset` |
| Memory bank | Stabile | `docs/memory/` |
| Guard report-only | Stabile | `just guards` e `scheduled.yml` |
| Data store, code, worker | Assenti per decisione | Non-obiettivi |

## Decisioni aperte

- Licenza del repository: non ancora scelta dal maintainer.
- CodeScene Cloud: progetto `87780` configurato; il ratchet richiede un REST API token, il gate locale richiede OAuth.
- Pubblicazione del package e deploy della UI: non previsti; package check e build restano obbligatori.

Le decisioni chiuse sono nelle ADR e nelle PDR. Ogni nuova decisione significativa va registrata prima o insieme al codice che la implementa.
