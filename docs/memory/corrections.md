# Correzioni

Registro delle correzioni e dei vincoli scoperti durante il lavoro. Una correzione che stabilizza e merita una traccia formale va in ADR o PDR; qui resta la sintesi operativa.

## 2026-11-14 — Bootstrap

- Il package richiede `README.md` per Hatchling: senza il file, `uv sync` fallisce con `Readme file does not exist`.
- `LOG_LEVEL` è accettato in minuscolo e in maiuscolo; la normalizzazione avviene in `RuntimeSettings`.
- I test E2E devono impostare `LOG_LEVEL` in minuscolo o affidarsi alla normalizzazione; un valore invalido fa fallire il processo.
- `mcpserver` configura il proprio logging quando viene istanziato: il composition root crea il logger prima del server e il server usa `log_level="ERROR"` per non duplicare il rumore.
- `MCPServer` e `Client` del SDK MCP v2 accettano il server in-memory direttamente; il test di integrazione non richiede un subprocess.
- I test dei wrapper devono risolvere il repository root da `tests/support/process.py` con `parents[2]`, non `parents[1]`.
- Pymarkdown non deve scansionare `docs/init/`: il Vademecum è un blueprint congelato e non segue le regole della documentazione viva.
- Il test dei wrapper deve isolare `uv run` con `UV_PROJECT_ENVIRONMENT` e `UV_PYTHON`: altrimenti può ricreare `.venv` mentre pytest usa l'ambiente corrente, causando `ModuleNotFoundError` per le dipendenze lazy importate (osservato con `jsonschema` e il client MCP su Python 3.13).
