# ADR-0003 — Validazione runtime con Pydantic

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

Il caso d'uso è semplice, ma le superfici ricevono input non fidati: argomenti CLI, query string HTTP e argomenti di un tool MCP. Le annotazioni Python non validano nulla a runtime e un `cast` non è un parser. Serve una fonte canonica per schemi, messaggi di errore e limiti.

## Decisione

Usiamo Pydantic v2 per i contratti esterni:

- `HelloWorldInput` e `HelloWorldOutput` sono modelli con `extra="forbid"` e `frozen=True`.
- Il nome è un alias `Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]`.
- Il tool MCP riusa l'alias nella firma, così il suo schema non duplica i vincoli.
- La route API valida esplicitamente il modello e mappa l'errore sulla tassonomia condivisa.
- `format_validation_error` produce un messaggio stabile per CLI, API e test.

Il dominio resta indipendente da Pydantic: riceve valori già validati e restituisce value object puri. L'application layer mappa i contratti verso il dominio.

## Conseguenze

- La validazione è reale, non cosmetica: input vuoti, spazi, valori troppo lunghi e campi extra falliscono.
- I messaggi sono coerenti tra superfici e testabili.
- Pydantic è una dipendenza runtime significativa, giustificata da schema, validazione e integrazione con FastAPI e MCP.
- I modelli interni che non attraversano un confine restano dataclass standard; non usiamo Pydantic ovunque.

## Alternative considerate

- **Dataclass con validazione manuale**: più codice, messaggi divergenti e nessuno schema condiviso.
- **msgspec o attrs**: validi, ma meno integrati con FastAPI e con l'SDK MCP.
- **Solo typing statico**: inaccettabile per input esterni; il type checker non è un validatore runtime.
- **`cast()` come parser**: vietato; nasconde il dato invece di verificarlo.
