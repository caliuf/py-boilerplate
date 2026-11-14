# Memoria dell'ambiente

## Macchina di sviluppo di riferimento

- Linux, shell bash.
- Python 3.14.5 gestito da `uv` (installato da mise o da uv stesso).
- Toolchain pinnato in `.mise.toml`: uv, just, direnv, gitleaks, actionlint, zizmor, lychee, shellcheck.
- `gh` per GitHub, `codegraph` opzionale, GNU parallel opzionale.
- Editor e client agent possono variare; le regole canoniche restano in `AGENTS.md`.

## Versioni

| Componente | Versione |
|---|---|
| Python | 3.14.5 (pinnata); minimo 3.13 |
| Node | 24.19.0 (solo tooling documentale) |
| cspell | 10.5.0 (npm, con dizionario italiano 3.1.7) |
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
- `direnv allow` è necessario per directory; un `.envrc` bloccato blocca il wrapper.
- I test E2E usano una porta effimera; firewall o proxy locali possono interferire.
- `uv sync --locked` non modifica il lockfile: un lock non coerente è un errore, non un auto-fix.
- La CI non ha accesso a segreti di produzione; non esistono deploy.
- Alcune API di GitHub richiedono scope o piani specifici; un 403 non significa che il controllo sia attivo.

## Diagnostica

- `just doctor` per runtime e configurazione.
- `tools/scripts/agent-briefing.sh` per il contesto di sessione.
- `uv run python -c "import py_boilerplate; print(py_boilerplate.__version__)"` per verificare l'import.
- `LOG_LEVEL=debug` per riprodurre un flusso con log dettagliati.
