# Ambiente

## Python

- `requires-python = ">=3.13"` in `pyproject.toml`.
- `.python-version` pinna `3.14.5`, la versione usata da sviluppo e CI principale.
- La CI testa 3.13 e 3.14. Un test locale su una sola versione non sostituisce la matrix.
- `uv` gestisce l'installazione di Python, l'environment e il lockfile. Non creare un secondo environment con `venv`, `virtualenv` o `conda`.
- Node 24 e npm gestiscono la UI web, Playwright, Biome e cspell. Il workspace npm contiene `apps/web`.

## Web

- `apps/web/` è un workspace npm privato, costruito con Vite.
- `npm ci` installa root, UI e tooling documentale da `package-lock.json`.
- I browser Playwright vivono nella cache utente (`~/.cache/ms-playwright`), non nel repository.
- `npm audit --omit=dev --audit-level=high` è parte di `just security`.
- In produzione la UI è un bundle statico: serve lo stesso origin dell'API o un reverse proxy per `/api`.

## Toolchain pinnato

`.mise.toml` pinna:

| Tool | Uso |
|---|---|
| `node` e `npm` | UI web, Playwright, Biome, cspell e dizionario italiano |
| `uv` | Python, environment, dipendenze, lockfile, build |
| `just` | Unica interfaccia operativa |
| `direnv` | Stratificazione environment per directory |
| `gitleaks` | Secret scanning |
| `actionlint` | Sintassi e semantica dei workflow |
| `zizmor` | Sicurezza dei workflow |
| `lychee` | Link check |
| `shellcheck` | Lint degli script shell |

Node non è un runtime del backend: serve alla UI, a Playwright e al tooling documentale. CodeGraph, GNU parallel e `gh` sono opzionali. Se mancano, le recipe degradano con un warning locale; in CI i gate obbligatori restano bloccanti.

## Dipendenze

Le dipendenze runtime Python sono in `[project].dependencies`; quelle di sviluppo nel gruppo `dev`. Le dipendenze web sono nel workspace npm `apps/web` e in `package-lock.json`. `uv.lock` e `package-lock.json` sono versionati e non si modificano a mano.

Comandi corretti:

```bash
uv add <package>
uv add --dev <package>
uv remove <package>
uv lock
uv sync --locked
```

Non introdurre `requirements.txt`, Poetry, PDM, pip-tools o un secondo lockfile per lo stesso progetto. Una dipendenza significativa richiede una ADR.

## Stratificazione environment

L'environment si compone in quest'ordine:

1. `.env.default`: floor committato, senza segreti.
2. `.env`: override locale, gitignored.
3. `.envrc.local`: override locale caricato da `.envrc`, gitignored.

`.envrc` usa `dotenv` di direnv. L'applicazione non legge questi file: legge solo variabili già presenti nell'environment, validate nel composition root.

## Variabili

| Variabile | Valori | Default | Effetto |
|---|---|---|---|
| `LOG_LEVEL` | `debug`, `info`, `warning`, `error`, `critical` | `info` | Livello minimo dei log; accetta anche la forma maiuscola |
| `APP_ENV` | `development`, `test`, `production` | `production` | `development` usa il renderer console; gli altri JSON |
| `API_HOST` | indirizzo | `127.0.0.1` | Bind dell'API |
| `API_PORT` | 1-65535 | `8100` | Porta dell'API |
| `WEB_PORT` | 1-65535 | `5100` | Porta del dev server Vite |
| `HELLO_WORLD_NAME` | stringa | assente | Nome usato dalla CLI se `--name` non è presente |

`LOG_LEVEL` e `APP_ENV` sono validati all'avvio. Un valore invalido fa fallire il processo con un errore leggibile, non viene ignorato.

CodeScene usa variabili proprie, documentate in [`CODESCENE.md`](CODESCENE.md): `CS_DEFAULT_PROJECT_ID` per l'MCP, `CODESCENE_PROJECT_ID` e `CODESCENE_API_TOKEN` per il ratchet. Non committare token.

## Ambiente di sviluppo e CI

- La CI usa Ubuntu, `uv sync --locked` e lo stesso `justfile`.
- La CI non modifica il lockfile e non installa dipendenze fuori dal lock.
- La matrix Python usa `UV_PYTHON` per forzare la versione del job.
- Il job E2E avvia processi reali e installa Chromium per Playwright; non usa mock del processo.
- Il job `quality` esegue `npm ci`, `just web-check` e `just security` (incluso npm audit).
- La slow lane settimanale esegue CodeQL, gitleaks sulla storia e link check esterni.

## Rete

A runtime il progetto non chiama servizi esterni. Le uniche connessioni avvengono in sviluppo e CI per installare dipendenze, scaricare Python e contattare GitHub. I test non usano rete, salvo il link check settimanale che è esplicitamente escluso dalla suite.

## Limiti noti

- Il flusso dei wrapper `bin/`, Playwright e la UI sono supportati su Linux e WSL; Windows nativo non è un obiettivo.
- `direnv allow` è richiesto per ogni directory; un `.envrc` non autorizzato blocca il wrapper con un messaggio esplicito.
- I test E2E usano una porta libera effimera; firewall o proxy locali possono interferire.
- Non esiste un ambiente di staging o produzione: il progetto non viene deployato.
