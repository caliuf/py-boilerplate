# Memoria dell'ambiente

## Macchina di sviluppo di riferimento

- Linux, shell bash.
- Python 3.14.5 gestito da `uv` (installato da mise o da uv stesso).
- Toolchain pinnato in `.mise.toml`: node, uv, just, direnv, gitleaks, actionlint, zizmor, lychee, shellcheck.
- `gh` per GitHub, `codegraph` opzionale, GNU parallel opzionale.
- CodeScene Cloud `87780`; MCP configurato in `.kilo/kilo.jsonc`; baseline Hotspot 9.10 e Average 9.76.
- Editor e client agent possono variare; le regole canoniche restano in `AGENTS.md`.

## Versioni

| Componente | Versione |
|---|---|
| Python | 3.14.5 (pinnata); minimo 3.13 |
| Node | 24.19.0 (UI, Playwright e tooling documentale) |
| cspell | 10.5.0 (npm, con dizionario italiano 3.1.7) |
| Playwright | 1.65.1 (Chromium in cache utente) |
| React / Vite / TypeScript | 19.3.1 / 8.3.6 / 7.0.2 |
| Tailwind CSS / @tailwindcss/vite | 4.3.5 / 4.3.5 |
| shadcn / Base UI / Lucide / Sonner | 4.23.0 / 1.9.0 / 1.73.0 / 2.0.8 |
| Biome / Oxlint / Vitest | 2.6.7 / 1.94.0 / 5.1.0 |
| Testing Library / jsdom / axe-core Playwright | 16.3.3 / 31.0.1 / 4.14.0 |
| uv | 0.11.26 |
| just | 1.58.0 |
| direnv | 2.37.1 |
| gitleaks | 8.30.1 |
| actionlint | 1.7.12 |
| zizmor | 1.30.0 |
| lychee | 0.24.2 |
| shellcheck | 0.11.0 |

Le versioni delle dipendenze Python sono risolte in `uv.lock`, non in questa tabella. Per il valore esatto usa `uv tree` o leggi il lock.

## Setup

```bash
just setup
just doctor
```

`just setup` installa i pacchetti di sistema, il toolchain mise, sincronizza il lock, attiva gli hook, crea `.env` e autorizza `.envrc`. `just doctor` verifica lo stato.

## Limiti e peculiarità

- Il flusso `bin/` richiede `uv` e `direnv`; è supportato su Linux e WSL.
- La UI richiede Node 24, `npm ci` e Chromium Playwright; Vite parte su 5100 e, se occupata, cerca la porta libera successiva. Gli E2E impostano `WEB_STRICT_PORT=true` e usano porte dedicate (15100 web, 18100 API) senza riusare server di altre checkout.
- `direnv allow` è necessario per directory; un `.envrc` bloccato blocca il wrapper.
- Gli E2E Python usano una porta effimera; Playwright usa 15100 e 18100; firewall o proxy locali possono interferire.
- `uv sync --locked` non modifica il lockfile: un lock non coerente è un errore, non un auto-fix.
- La CI non ha accesso a segreti di produzione; non esistono deploy.
- Alcune API di GitHub richiedono scope o piani specifici; un 403 non significa che il controllo sia attivo.

## Diagnostica

- `just doctor` per runtime e configurazione.
- `tools/scripts/agent-briefing.sh` per il contesto di sessione.
- `uv run python -c "import py_boilerplate; print(py_boilerplate.__version__)"` per verificare l'import.
- `LOG_LEVEL=debug` per riprodurre un flusso con log dettagliati.
- `just codescene-safeguard` per verificare il Code Health dei file staged; `just web-check` per la UI e `just build` per la build di produzione.
