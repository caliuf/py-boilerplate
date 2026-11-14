# ADR-0004 — Tassonomia errori e mapping sulle superfici

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

CLI, API e MCP hanno canali diversi: exit code, status HTTP, Problem Details e tool error. Senza una tassonomia unica, lo stesso errore assume nomi, codici e semantica diversi, e un client non può ragionare in modo uniforme. Il Vademecum richiede una mappatura esplicita e contratti verificati.

## Decisione

Definiamo in `contracts/errors.py`:

- `ErrorCode` come `StrEnum` con i valori `INTERNAL`, `VALIDATION`, `UNAUTHORIZED`, `NOT_FOUND`, `CONFLICT`.
- `AppError` come value object immutabile con codice e messaggio sicuro.
- `ApplicationError` come eccezione tipizzata che trasporta un `AppError`.
- Mapping immutabili verso exit code CLI, status HTTP e `ProblemInfo` (`type` URN e `title`).
- `ProblemDetails` come modello RFC 9457 con `application/problem+json`.

I mapping sono:

| Codice | Exit CLI | HTTP | URN |
|---|---|---|---|
| `INTERNAL` | 1 | 500 | `urn:py-boilerplate:error:internal` |
| `VALIDATION` | 2 | 400 | `urn:py-boilerplate:error:validation` |
| `UNAUTHORIZED` | 3 | 401 | `urn:py-boilerplate:error:unauthorized` |
| `NOT_FOUND` | 4 | 404 | `urn:py-boilerplate:error:not-found` |
| `CONFLICT` | 5 | 409 | `urn:py-boilerplate:error:conflict` |

Il prefisso URN cambia quando il boilerplate viene adottato. I codici e la semantica restano.

## Conseguenze

- Aggiungere un codice errore richiede di aggiornare tutti i mapping e i test di completezza; il gate fallisce se un mapping manca.
- I client possono trattare il codice applicativo indipendentemente dal canale.
- I messaggi sono sicuri per il client: niente stack trace o dettagli interni.
- L'application layer non importa eccezioni FastAPI o tipi MCP; solleva `ApplicationError` e lascia il mapping al confine.

## Alternative considerate

- **Errori per superficie**: semplici localmente, ma incoerenti e difficili da testare.
- **HTTPException nel caso d'uso**: viola l'indipendenza dal framework.
- **Stringhe libere**: nessun contratto stabile, nessun test possibile.
- **Codici numerici custom**: meno leggibili nei log e nei payload rispetto a uno `StrEnum`.
