# PDR-0001 — Un caso d'uso `hello-world` su CLI, API e MCP

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna
- Aggiornamento: [PDR-0002](0002-ui-web.md) aggiunge la UI web; il resto resta valido.

## Contesto

Il boilerplate deve dimostrare un percorso completo, non solo uno scheletro. Il caso d'uso deve essere abbastanza semplice da restare leggibile, ma abbastanza reale da esercitare validazione, logging, errori, superfici multiple, packaging e test end-to-end. Deve inoltre essere un esempio onesto per chi adotta il progetto: nessun servizio esterno, nessun database, nessun segreto.

## Decisione

Esponiamo un unico caso d'uso, `hello-world`, su tre superfici:

- comando CLI `py-boilerplate hello-world`;
- route HTTP `GET /api/hello-world`;
- tool MCP `hello_world`.

Tutte le superfici condividono input, output, validazione e tassonomia errori. Il default è `Hello, world!`; un nome valido produce `Hello, <nome>!` dopo il trim degli spazi. Un nome vuoto o più lungo di 100 caratteri è un errore `VALIDATION`.

## Comportamento osservabile

| Caso | CLI | API | MCP |
|---|---|---|---|
| Nessun nome | JSON `{"message":"Hello, world!"}` | 200 `{"message":"Hello, world!"}` | structured content con lo stesso messaggio |
| Nome valido | JSON o testo con il nome con trim applicato | 200 con il nome con trim applicato | structured content con il nome con trim applicato |
| Nome vuoto o oltre 100 caratteri | errore su stderr, exit 2 | 400 `application/problem+json`, codice `VALIDATION` | tool error, `isError: true` |
| Comando o parametro sconosciuto | errore `VALIDATION` o `NOT_FOUND` | non applicabile | non applicabile |

La CLI usa JSON di default quando stdout non è un TTY, così un agente non deve passare `--json` a ogni invocazione. Il flag `--json` resta esplicito e idempotente.

## Criteri di accettazione

- Il comando, la route e il tool restituiscono lo stesso messaggio per lo stesso input valido.
- Gli errori di validazione sono coerenti tra superfici e verificati da un contract test.
- Il tool MCP dichiara `readOnlyHint` e `idempotentHint`.
- La CLI separa dati su stdout e diagnostica su stderr.
- L'API non espone stack trace e usa Problem Details.
- Il caso d'uso è coperto da unit, integration, contract ed E2E.
- Il package installato in un venv pulito espone i tre entry point.

## Conseguenze

- Il boilerplate dimostra il percorso completo senza dominio fittizio.
- Le superfici condividono il caso d'uso: un cambiamento di semantica si fa una volta.
- La UI browser resta fuori scope; un'eventuale aggiunta richiede una nuova PDR e una nuova ADR.
- Il nome `hello-world` è un placeholder: un progetto derivato lo sostituisce insieme al nome del package.

## Alternative considerate

- **Caso d'uso più ricco (task manager)**: più realistico, ma aggiunge persistenza, stato e decisioni di prodotto che distraggono dal boilerplate.
- **Solo CLI**: non dimostra i confini HTTP e MCP.
- **Solo API**: perde il valore agent-first della CLI e del tool MCP.
- **Caso d'uso diverso per superficie**: duplica logica e rende impossibile il contract test cross-surface.
