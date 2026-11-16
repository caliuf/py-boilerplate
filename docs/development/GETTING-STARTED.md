# Getting started

Questa guida porta da una macchina pulita a un primo task validato. Il percorso è testato su Linux e WSL con una shell bash.

## Prerequisiti

Servono:

- Git e una shell bash.
- [`mise`](https://mise.jdx.dev/) per installare il toolchain pinnato.
- `uv` e `just`; `just install` li installa via mise.
- `direnv` per il caricamento dell'environment.
- `gh` per le operazioni GitHub.
- Node 24 e npm per la UI web e cspell.
- Su Debian/Ubuntu, i pacchetti di build elencati nella recipe `install`.

Se `mise` non è installato, segui la documentazione ufficiale e riapri la shell. `just` può essere installato anche con il package manager della distribuzione, ma la versione autorevole è quella in `.mise.toml`.

## Bootstrap

```bash
git clone https://github.com/caliuf/py-boilerplate.git
cd py-boilerplate
just setup
just doctor
```

`just setup` esegue, nell'ordine:

1. installazione dei pacchetti di sistema e del toolchain pinnato;
2. `npm ci` per il workspace web e il tooling documentale;
3. installazione del browser Chromium per Playwright;
4. `uv sync --locked` sull'ambiente Python;
5. attivazione degli hook versionati in `.githooks/`;
6. creazione di `.env` da `.env.example` se assente;
7. `direnv allow` sul repository;
8. inizializzazione e indicizzazione CodeGraph, se il tool è presente.

`just doctor` deve terminare con exit 0. Se un tool esterno manca, il doctor lo segnala; in CI quel tool è bloccante.

## Primo giro

CLI:

```bash
uv run py-boilerplate hello-world --json
```

API e UI:

```bash
just dev
```

La UI è su <http://localhost:5100>; il proxy Vite inoltra `/api` all'API su <http://127.0.0.1:8100>. In un'altra shell:

```bash
curl -s "http://127.0.0.1:8100/api/hello-world?name=Ada"
```

MCP:

```bash
uv run py-boilerplate-mcp
```

Il server MCP parla JSON-RPC su stdio. Per un test automatico usa la suite in-memory o E2E; non avviarlo manualmente se non stai collegando un client MCP.

Wrapper:

```bash
bin/py-boilerplate-hello-world --name Ada --json
```

Il wrapper carica `.env.default`, poi l'eventuale `.env` del chiamante tramite direnv, e delega a `uv run --project`.

## Primo task

1. Crea un branch: `git switch -c feat/<scope>`.
2. Leggi [`docs/memory/project.md`](../memory/project.md), [`docs/memory/environment.md`](../memory/environment.md) e le ADR/PDR pertinenti.
3. Scrivi il test che descrive il comportamento e guardalo fallire.
4. Implementa il minimo per il verde, poi rifattorizza.
5. Esegui `just precommit`.
6. Aggiorna documentazione, ADR e PDR nello stesso commit.
7. Esegui `just prepush`.
8. Apri la PR con il report dei comandi.

La procedura completa è in [`WORKFLOWS.md`](WORKFLOWS.md).

## Comandi utili

| Comando | Uso |
|---|---|
| `just test-unit` | Feedback rapido sul dominio e sui contratti |
| `just test-integration` | API e MCP in-memory |
| `just test-contract` | Processo CLI e coerenza cross-surface |
| `just test-e2e` | Processi reali per CLI, API, MCP e browser Playwright |
| `just web-check` | Biome, Oxlint, TypeScript e Vitest della UI |
| `just web-test` | Test di contratti, hook e componenti della UI |
| `just build` | Build di produzione della UI |
| `just coverage` | Coverage e gate a cricchetto |
| `just ci` | Pipeline completa locale |
| `just fix` | Auto-fix Ruff |
| `just docs-check` | Markdown, spelling e link |
| `just guards` | Report dei guard |

## Troubleshooting

### `just: command not found`

Installa il toolchain con `mise install` e assicurati che gli shim di mise siano nel `PATH`. Riapri la shell dopo l'installazione.

### `uv sync --locked` fallisce

Il lockfile non è coerente con `pyproject.toml`. Non modificare `uv.lock` a mano: esegui `uv lock`, verifica il diff e committa il lock aggiornato insieme al manifest.

### `direnv: error ... is blocked`

Esegui `direnv allow` nella directory del repository o nel chiamante. Il wrapper controlla l'autorizzazione prima di delegare a `uv`.

### Gli hook non partono

Verifica `git config --get core.hooksPath`: deve essere `.githooks`. Se non lo è, esegui `just setup`.

### La versione Python non corrisponde

`.python-version` pinna la patch. `uv python install` scarica la versione richiesta; `just doctor` segnala un mismatch di major/minor come errore e un mismatch di patch come warning.

### La coverage gate fallisce

Non abbassare la soglia. Aggiungi test comportamentali per il codice nuovo o ripristina il comportamento rotto. Se il calo è deliberato, la decisione richiede una modifica esplicita della baseline e una review dedicata.

### Un gate esterno è assente

In locale la recipe stampa un warning e salta il controllo; in CI lo stesso gate è bloccante. Installa il tool con `mise install` e riprova. Non estendere ignore-list per farlo passare.

### Il browser Playwright non è installato

Esegui `npx playwright install chromium`. In CI il browser viene installato con le dipendenze di sistema. Se manca solo il browser, `just web-check` funziona ma `just test-e2e` no.

### La porta 5100 è occupata

Vite usa `strictPort` e fallisce invece di cambiare porta. Ferma il processo che occupa 5100 o imposta `WEB_PORT` a una porta libera. La suite Playwright usa 5100 e 8100: assicurati che siano libere.

### CodeScene non è autenticato

`just precommit` e `just prepush` eseguono i gate CodeScene. Se l'MCP non è autenticato, esegui `npx -y @codescene/codehealth-mcp auth` o chiama il tool MCP `login`. Se il gate non può girare, fermati e riporta il blocker: non aggirarlo.

### Un test E2E resta appeso

Controlla che la porta API sia libera e che il processo figlio termini. La suite E2E usa un timeout e termina il processo nel `finally`; se il problema persiste, riproduci il flusso con `LOG_LEVEL=debug` e cita i log.
