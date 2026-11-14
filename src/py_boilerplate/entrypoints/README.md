# Entrypoints

Gli entrypoint sono adapter driving. Ognuno ha la stessa anatomia:

1. parsing o ricezione dell'input;
2. validazione runtime al confine;
3. invocazione del caso d'uso;
4. mapping del risultato sul canale;
5. logging solo tramite la porta.

## Superfici

| Directory | Entry point | Canale |
|---|---|---|
| `cli/` | `py-boilerplate` | stdout dati, stderr diagnostica, exit code |
| `api/` | `py-boilerplate-api` | HTTP JSON e `application/problem+json` |
| `mcp/` | `py-boilerplate-mcp` | JSON-RPC su stdio |

## Regole

- Nessun entrypoint importa un altro entrypoint. Il contratto Import Linter `Entrypoints are independent` lo verifica.
- Ogni entrypoint ha un composition root sottile; la logica vive nell'application layer.
- `main.py` e `server.py` sono bootstrap di processo, esclusi da coverage e coperti dai test E2E.
- I nomi dei casi d'uso sono paralleli tra superfici: `hello-world` per CLI, `/api/hello-world` per API, `hello_world` per MCP.
- Le descrizioni dei tool MCP sono scritte per il modello e dichiarano read-only e idempotenza.
- La mappa delle superfici in `docs/PROJECT.md` va aggiornata a ogni nuova route, comando o tool.

## Test

- API: `tests/integration/test_api.py`.
- MCP: `tests/integration/test_mcp.py`.
- CLI: `tests/contract/test_cli_contract.py`.
- Coerenza tra superfici: `tests/contract/test_surface_contract.py`.
- Processi reali: `tests/e2e/test_full_stack.py`.
