# ADR-0009 — UI web React/Vite e Playwright

- Stato: Accettata
- Data: 2026-11-14
- Supersede: ADR-0006 (limitatamente all'assenza di UI browser)

## Contesto

Il progetto derivato da `ts-boilerplate` deve offrire la stessa esperienza a quattro superfici: CLI, API HTTP, MCP e UI web. La UI deve essere keyboard-first, usare un design system riutilizzabile e verificare il percorso reale attraverso il browser. Il backend resta Python; la UI non deve importare codice Python né duplicare la logica del caso d'uso.

Il Vademecum Python raccomanda React/Vite come app separata quando esiste una UI, e Playwright per pochi flussi E2E di alto valore. Node è già presente per cspell; la UI aggiunge dipendenze solo di sviluppo/build, non un runtime del backend.

## Decisione

Aggiungiamo `apps/web` come app React 19 + Vite 8 + TypeScript 7:

- npm workspace alla radice; `apps/web/package.json` dichiara React, ReactDOM, Zod, Vite, Vitest e i tipi.
- `apps/web/src/design-system/` contiene `Page`, `TextInput`, `Button`, `Message` e lo stile.
- `apps/web/src/features/greeting/` contiene la pagina, lo stato server e il client API.
- Il client chiama `/api/hello-world` tramite il proxy Vite verso `API_PORT` (default 8100).
- Le risposte sono validate a runtime con Zod; `contracts.ts` è il mirror client-side dei contratti Pydantic/OpenAPI, verificato dal contract test Python.
- `just dev` avvia API e web; `just web-check` esegue Biome, TypeScript, Vitest e build; `just test-e2e` esegue Playwright oltre agli E2E Python.
- La UI è un deployable statico: in produzione va servita dallo stesso origin dell'API o dietro un reverse proxy che espone `/api`.

## Conseguenze

- Node 24 diventa necessario per sviluppo, test e build della UI (era già necessario per cspell).
- La suite CI `e2e` installa Chromium e verifica il flusso keyboard-first e il percorso del bottone.
- La coverage Python non misura il codice DOM; la UI è coperta da Playwright e dai test Vitest dei contratti client.
- La UI non ha SSR, autenticazione, routing o stato globale: sono fuori scope finché non esiste una PDR che li richieda.
- Il design system evita markup grezzo nelle feature, così stile e accessibilità restano centralizzati.

## Alternative considerate

- **Nessuna UI**: era la decisione precedente, superata dalla richiesta esplicita di parità con `ts-boilerplate`.
- **UI servita da FastAPI con HTML statico**: più semplice da deployare, ma non replica la struttura React/Vite e renderebbe l'E2E browser più fragile.
- **Next.js o SSR**: aggiunge un server Node e un modello di deploy non necessario per un caso d'uso read-only.
- **Test solo HTTP senza browser**: non verifica tastiera, focus, rendering e integrazione del client.
