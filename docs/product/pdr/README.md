# Product Decision Records

Le PDR registrano decisioni di prodotto: cosa il sistema deve fare, per chi e con quali criteri di accettazione. Non registrano dettagli implementativi, che appartengono alle ADR.

## Indice

| PDR | Titolo | Stato |
|---|---|---|
| [0001](0001-hello-world.md) | Un caso d'uso `hello-world` su CLI, API e MCP | Accettata |
| [0002](0002-ui-web.md) | UI web del caso d'uso `hello-world` | Accettata |

## Quando scrivere una PDR

Scrivi una PDR quando la decisione:

- cambia il comportamento osservabile del prodotto;
- aggiunge o rimuove una superficie, un flusso o un'attrice;
- introduce una regola di validazione, un limite o una semantica di errore visibile al client;
- richiede un compromesso tra semplicità e capacità futura;
- non può essere dedotta da una ADR o dal codice senza ambiguità.

## Formato

Ogni record contiene: titolo, stato, data, contesto, decisione, comportamento osservabile, criteri di accettazione, conseguenze e alternative considerate.

## Manutenzione

- Aggiorna l'indice nello stesso commit della nuova PDR.
- Collega la PDR dalla documentazione di prodotto pertinente.
- Se una decisione cambia, aggiungi una nuova PDR con relazione di supersession; non riscrivere quella accettata.
- Le PDR non duplicano il glossario: usano i termini definiti lì.
