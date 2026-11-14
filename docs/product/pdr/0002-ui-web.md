# PDR-0002 — UI web del caso d'uso `hello-world`

- Stato: Accettata
- Data: 2026-11-14
- Supersede: PDR-0001 limitatamente all'assenza di UI browser

## Contesto

`ts-boilerplate` offre una UI web minimale per lo stesso caso d'uso. Il progetto Python deve raggiungere la parità di esperienza: un utente deve poter inserire un nome, inviare con tastiera o bottone e vedere il saluto o l'errore, usando la stessa API delle altre superfici.

## Decisione

Aggiungiamo una UI web React/Vite servita in sviluppo su `http://localhost:5100`, con proxy `/api` verso l'API Python su `http://127.0.0.1:8100`.

Comportamento:

- campo "Name" con placeholder `world`;
- Invio nell'input invia la richiesta;
- bottone "Greet" invia la richiesta ed è raggiungibile da tastiera;
- successo: messaggio `Hello, <nome>!`;
- input vuoto: messaggio di errore dal Problem Details dell'API;
- caricamento: stato "Loading…".
- Il default senza nome è `Hello, world!`.

## Criteri di accettazione

- Il percorso keyboard-first funziona in un browser reale.
- Il percorso del bottone mostra il saluto di default.
- La UI usa solo i componenti del design system per markup, input, bottoni e messaggi.
- Le risposte API sono validate a runtime con Zod prima di essere mostrate.
- Il contratto client-side resta coerente con Pydantic/OpenAPI tramite un contract test.
- `just test-e2e` esegue sia gli E2E Python sia Playwright.
- La UI non importa codice Python e non contiene logica di dominio.

## Conseguenze

- Node, Vite, React, TypeScript, Playwright, Vitest e Biome entrano nel toolchain di sviluppo.
- La UI è un deployable statico separato; in produzione serve lo stesso origin o un reverse proxy per `/api`.
- Non ci sono SSR, autenticazione, routing o stato globale finché non servono.
- La coverage Python non misura il DOM; la UI è coperta da Playwright e dai test dei contratti client.

## Alternative considerate

- **Nessuna UI**: non raggiunge la parità richiesta con `ts-boilerplate`.
- **HTML statico servito da FastAPI**: più semplice, ma non replica la struttura React/Vite e l'esperienza di sviluppo.
- **Next.js/SSR**: aggiunge un server Node e un deploy non necessari.
- **Test solo HTTP**: non verifica tastiera, focus, rendering e integrazione del client.
