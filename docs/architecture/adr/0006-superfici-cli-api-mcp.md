# ADR-0006 — Superfici CLI, API e MCP senza UI browser

- Stato: Superata da ADR-0009 (limitatamente all'assenza di UI browser)
- Data: 2026-11-14
- Supersede: nessuna

> Aggiornamento 2026-11-14: la richiesta esplicita di parità con `ts-boilerplate` ha aggiunto una UI web React/Vite. La decisione sulle altre superfici resta valida; vedi [ADR-0009](0009-ui-web.md).

## Contesto

`ts-boilerplate` espone il caso d'uso su CLI, API, MCP e web. Per un boilerplate Python, una UI browser aggiungerebbe un runtime Node, un tool di build frontend e Playwright a un progetto che vuole restare Python-first. Il Vademecum raccomanda di non creare una UI se non esiste un bisogno reale e di non installare Playwright solo per avere un E2E.

## Decisione

Esponiamo il caso d'uso su tre superfici:

- CLI agent-first, con JSON di default in non-TTY e exit code stabili.
- API HTTP FastAPI, con Problem Details RFC 9457.
- MCP stdio, con un tool read-only e idempotente.

Non includiamo una UI browser, Playwright, React, Vite o un server statico separato. `just test-e2e` resta un E2E di processo: avvia CLI, API HTTP e MCP stdio reali, senza mock del processo.

## Conseguenze

- Il toolchain resta Python + strumenti CLI, senza runtime Node obbligatorio.
- L'E2E è veloce e verifica i confini reali delle tre superfici.
- Se in futuro nasce una UI, serve una nuova PDR con i flussi utente e una nuova ADR con il modello di deploy e la strategia E2E.
- Il boilerplate non dimostra la parte browser del modello 3G; la dimostra per CLI, API e MCP.

## Alternative considerate

- **HTML statico servito da FastAPI + Playwright**: aggiunge browser, flakiness e dipendenze per un caso d'uso che non ha bisogno di UI.
- **React/Vite separato**: replicherebbe `apps/web` del progetto TypeScript, ma introdurrebbe un secondo ecosistema in un boilerplate Python.
- **Solo CLI e API**: perde la superficie MCP, che è parte del valore agent-first del boilerplate.
