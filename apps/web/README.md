# Web

L'interfaccia web è un'app React + Vite separata dal backend Python. Consuma l'API HTTP e non importa codice Python.

## Stack

- React 19 + TypeScript 7 con Vite 8.
- Tailwind CSS 4 tramite `@tailwindcss/vite`, con CSS nativo o CSS Modules per i casi in cui sono più leggibili.
- shadcn/ui con Base UI come primitive interattive, Lucide React come unico set di icone, CVA per le varianti e `cn` centralizzato.
- Sonner per i toast non bloccanti.
- Token semantici in CSS custom properties, light/dark e `@theme inline`.
- Vitest con un progetto Node e un progetto jsdom, Playwright e `@axe-core/playwright` per i flussi reali.
- Oxlint type-aware con `jsx-a11y`, Biome per formattazione e lint CSS, `tsc` per il typecheck.

Le decisioni sono registrate in [`ADR-0011`](../../docs/architecture/adr/0011-design-system-frontend.md) e [`PDR-0003`](../../docs/product/pdr/0003-tema-ui-web.md).

## Struttura

```text
apps/web/
├── components.json                 # alias e preset del CLI shadcn
├── index.html                      # bootstrap del tema prima del primo paint
└── src/
    ├── app/                        # shell, provider del tema, toggle
    ├── design-system/
    │   ├── lib/utils.ts            # re-export unico di `cn`
    │   ├── patterns/               # composizioni riutilizzabili fra feature
    │   ├── primitives/             # componenti shadcn/Base UI del repository
    │   └── theme/                  # tokens.css e global.css
    ├── features/greeting/          # pagina, hook di stato server, client API e test
    ├── contracts.ts                # mirror Zod dei contratti Pydantic/OpenAPI
    └── test/setup.ts               # setup Vitest del progetto DOM
```

## Regole

- I componenti di feature compongono il design system; non ricostruiscono pulsanti, input, dialog, menu o altri controlli interattivi.
- HTML semantico nativo (`main`, `header`, `section`, `form`, heading, liste) è corretto per la struttura del documento. I controlli interattivi passano dal design system.
- I token semantici vivono solo in `design-system/theme/tokens.css`; palette, radius, tipografia e durate si cambiano in un punto.
- I componenti usano `bg-primary`, `text-muted-foreground` e gli altri token semantici, non colori di palette come `blue-600`.
- Le classi Tailwind sono stringhe statiche e complete: niente `bg-${color}-500`.
- Le feature non importano `@base-ui/react` direttamente: usano le primitive esposte dal design system.
- Il client valida sempre le risposte con Zod: i dati esterni non vengono mai `cast`ati.
- La fonte canonica dei contratti è Pydantic/OpenAPI. `contracts.ts` è il mirror client-side; il contract test Python verifica che i vincoli condivisi restino coerenti.
- La UI è keyboard-first: Enter invia, il focus è visibile, skip link e controlli hanno nomi accessibili.
- Non aggiungere DaisyUI, un secondo design system, un secondo set di icone o CSS-in-JS runtime senza una nuova ADR.

## Design system e shadcn

`components.json` usa gli alias del repository:

- `ui` → `src/design-system/primitives`
- `utils` → `src/design-system/lib/utils`
- `components` → `src/design-system`
- `hooks` → `src/design-system/hooks`

Per aggiungere un componente usare il CLI dalla directory `apps/web`:

```bash
npx shadcn@latest add <component>
```

Dopo l'aggiunta controllare i file generati, le dipendenze, gli import di `cn`, il typecheck, il lint, i test e la build. Non copiare snippet incompleti da fonti terze e non generare l'intero catalogo: aggiungere i componenti quando servono.

Le primitive presenti sono il set di partenza per le app derivate: form, overlay, menu, tab, feedback, skeleton, empty state e toast. Le composizioni condivise fra più feature vanno in `design-system/patterns/`; una composizione usata da una sola feature resta nella feature.

## Tema

- Il tema iniziale segue `prefers-color-scheme`; l'utente può scegliere chiaro o scuro dal controllo nell'header.
- La preferenza è persistita in `localStorage` e sincronizzata tra tab.
- `index.html` applica il tema prima del primo paint; `ThemeProvider` mantiene coerenti stato React, DOM e preferenza di sistema.
- I componenti non duplicano CSS per tema: usano gli stessi token semantici, ridefiniti in `.dark`.
- Il rispetto di `prefers-reduced-motion` è centralizzato nei token e nelle regole globali.
- Non introdurre uno script inline di bootstrap senza considerare la CSP: in presenza di CSP serve un nonce o un hash, non `unsafe-inline`.

## Configurazione

`src/config/env.ts` valida la configurazione a runtime con Zod. `VITE_API_BASE_URL` è vuota per usare la stessa origine e il proxy Vite; in deploy può puntare a un'API assoluta `http(s)://`. Un valore invalido blocca l'avvio invece di produrre richieste silenziosamente sbagliate. Le variabili web sono lette solo dal client e non contengono segreti.

## Contratti e API

Il client chiama `${VITE_API_BASE_URL}/api/hello-world` tramite il proxy Vite verso l'API Python. Le risposte sono validate a runtime con Zod e gli errori Problem Details sono mappati sulla tassonomia condivisa. La UI non parla direttamente con database o servizi esterni e non contiene logica di dominio.

## Test

- `apps/web/src/**/*.test.ts` gira nel progetto Vitest Node: contratti, schemi e hook puri.
- `apps/web/src/**/*.test.tsx` gira nel progetto Vitest jsdom con Testing Library: componenti, stati e interazioni.
- `tests/e2e/*.spec.ts` gira in Playwright su processi reali: flusso keyboard-first, bottone, tema, accessibilità axe e viewport stretto.
- I test dei componenti usano le API pubbliche e i ruoli accessibili; non verificano classi CSS interne.
- Playwright usa porte E2E dedicate (`15100` web, `18100` API) e non riusa server di altre checkout.

## Comandi

```bash
npm run web:dev        # Vite su http://localhost:5100, proxy /api su 127.0.0.1:8100
npm run web:test       # Vitest: contratti, hook e componenti
npm run web:typecheck  # TypeScript strict
npm run web:build      # build di produzione
npm run web:check      # Biome, Oxlint, typecheck e Vitest
```

Le recipe root-level sono la fonte autorevole:

```bash
just web-dev           # richiede l'API attiva; per API + UI usa `just dev`
just web-test
just web-typecheck
just web-check
just build
just test-e2e
```

`just web-check` non esegue la build; `just build` è la recipe pubblica della build di produzione, inclusa in `just prepush` e `just ci`.

## Budget di build

`just build` esegue Vite e poi controlla il budget gzip in `apps/web/budget.json`: CSS, JavaScript e totale. Il budget è un ratchet: può solo migliorare o essere aggiornato con una decisione esplicita quando cresce lo scope del prodotto. Il controllo è deterministico e non sostituisce la review del bundle quando una feature aggiunge molte dipendenze.
