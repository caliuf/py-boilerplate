# ADR-0002 — Architettura a singola distribuzione

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

`ts-boilerplate` è un monorepo con `apps/` e `packages/`. Per Python la scelta non è automatica: un uv workspace è utile quando esistono versionamento, deploy o responsabilità autonome reali, ma introduce più manifest, più ambienti e più configurazione di tool. Il progetto ha un solo caso d'uso e tre entry point che condividono lo stesso codice.

## Decisione

Adottiamo una singola distribuzione Python con layout `src/` e sottosistemi interni:

- `contracts`, `greetings`, `adapters`, `entrypoints` sono package interni a `py_boilerplate`.
- Il wheel espone tre console script: CLI, API e MCP.
- I confini sono enforced da Import Linter, non da una separazione fisica in distribuzioni.
- Un eventuale uv workspace si introduce solo quando esiste una reale esigenza di versionamento o deploy indipendente, con una nuova ADR.

## Conseguenze

- Un solo `pyproject.toml`, un solo `uv.lock`, un solo environment.
- Mypy, deptry, coverage e Import Linter analizzano un solo progetto, con configurazione più semplice e meno duplicazione.
- I confini restano espliciti e verificati: la vicinanza fisica non autorizza import vietati.
- Estrarre in futuro un package separato è possibile, ma richiede di spostare codice e aggiornare i contratti di import.

## Alternative considerate

- **uv workspace con `apps/*` e `packages/*`**: specchia la struttura TypeScript, ma aggiunge complessità non giustificata per un caso d'uso unico.
- **Distribuzioni separate per CLI, API e MCP**: utile solo con cicli di release indipendenti, che oggi non esistono.
- **Flat layout**: scoraggiato dal Vademecum per il rischio di import shadowing e per la separazione meno netta tra codice e test.
