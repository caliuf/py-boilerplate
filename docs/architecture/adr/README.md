# Architectural Decision Records

Le ADR registrano decisioni architetturali durature. Una decisione accettata non si riscrive: se cambia, si aggiunge una nuova ADR che supersede la precedente. L'indice deve elencare tutti i record della directory.

## Indice

| ADR | Titolo | Stato |
|---|---|---|
| [0001](0001-stack-python.md) | Stack Python e tooling | Accettata |
| [0002](0002-architettura-single-distribution.md) | Architettura a singola distribuzione | Accettata |
| [0003](0003-validazione-pydantic.md) | Validazione runtime con Pydantic | Accettata |
| [0004](0004-tassonomia-errori.md) | Tassonomia errori e mapping sulle superfici | Accettata |
| [0005](0005-ci-consolidata.md) | CI consolidata e slow lane di sicurezza | Accettata |
| [0006](0006-superfici-cli-api-mcp.md) | Superfici CLI, API e MCP senza UI browser | Superata da ADR-0009 |
| [0007](0007-wrapper-bin-direnv.md) | Wrapper `bin/` e stratificazione environment con direnv | Accettata |
| [0008](0008-memory-bank.md) | Memory bank portabile in `docs/memory/` | Accettata |
| [0009](0009-ui-web.md) | UI web React/Vite e Playwright | Accettata |
| [0010](0010-codescene.md) | CodeScene Code Health come gate locale | Accettata |

## Quando scrivere una ADR

Scrivi una ADR quando la decisione:

- cambia la direzione delle dipendenze o i confini tra moduli;
- introduce o rimuove un deployable, un framework, un protocollo o un data store;
- cambia la strategia di validazione, errori, logging o configurazione;
- cambia la pipeline di build, test o sicurezza in modo non banale;
- richiede un compromesso che un futuro maintainer potrebbe mettere in discussione.

Non scrivere una ADR per una scelta locale e reversibile che non ha impatto sui confini.

## Formato

Ogni record contiene: titolo, stato, data, contesto, decisione, conseguenze e alternative considerate. Le conseguenze includono gli obblighi operativi e i costi accettati.

## Manutenzione

- Aggiorna l'indice nello stesso commit della nuova ADR.
- Collega la ADR dalla documentazione architetturale pertinente.
- Non duplicare la decisione in `docs/memory/decisions.md`: la memory bank rimanda alla ADR.
- Le modifiche a una decisione accettata richiedono una nuova ADR con relazione esplicita di supersession.
