# Web

L'interfaccia web è un'app React + Vite separata dal backend Python. Consuma l'API HTTP e non importa codice Python.

## Struttura

- `src/design-system/` — componenti primitivi: `Page`, `TextInput`, `Button`, `Message` e CSS.
- `src/features/greeting/` — feature `hello-world`: pagina, hook di stato server e client API.
- `src/contracts.ts` — mirror TypeScript dei contratti, con schemi Zod per validare le risposte esterne.
- `src/contracts.test.ts` — test unit dei vincoli di input.

## Regole

- I componenti di feature usano solo il design system; non creano `<button>`, `<input>` o `<main>` grezzi.
- Il client valida sempre le risposte con Zod: i dati esterni non vengono mai `cast`ati.
- La fonte canonica dei contratti è Pydantic/OpenAPI. `contracts.ts` è il mirror client-side; il contract test Python verifica che i vincoli condivisi restino coerenti.
- La UI è keyboard-first: Enter nell'input invia, il bottone è raggiungibile da tastiera e ha focus visibile.
- Non aggiungere logica di dominio o chiamate dirette al database: la UI parla solo all'API.

## Comandi

```bash
npm run web:dev        # Vite su http://localhost:5100, proxy /api su 8100
npm run web:test       # Vitest sui contratti client
npm run web:typecheck  # TypeScript strict
npm run web:build      # build di produzione
npm run web:check      # formattazione, typecheck, test e build
```

L'E2E Playwright è nella root:

```bash
npm run test:e2e
```
