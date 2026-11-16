# ADR-0011 — Baseline frontend: Tailwind CSS, shadcn/ui e Base UI

- Stato: Accettata
- Data: 2026-11-16
- Supersede: ADR-0009 limitatamente al design system, allo styling e ai gate UI; React, Vite e Playwright restano validi.

## Contesto

La UI minima introdotta con ADR-0009 usava CSS nativo e quattro componenti artigianali. Era sufficiente per il caso d'uso `hello-world`, ma non era una baseline per le app che erediteranno il boilerplate: ogni progetto avrebbe dovuto reinventare componenti interattivi, token, temi, controlli accessibili e gate UI.

Il Vademecum CSS definisce uno stack predefinito per i nuovi frontend: Tailwind CSS v4 con `@tailwindcss/vite`, shadcn/ui con codice sorgente nel repository, Base UI come base delle primitive, Lucide React, CVA, `cn`, token semantici, light/dark e gate automatici. Lo stesso vademecum chiarisce che la migrazione di un design system esistente è una decisione architetturale, non l'esecuzione cieca del CLI. Questa ADR registra quella decisione.

## Decisione

**Adottiamo lo stack frontend del Vademecum CSS come baseline del boilerplate, migrando la UI esistente e mantenendo intatti caso d'uso e contratti.**

- **Styling**: Tailwind CSS 4 tramite `@tailwindcss/vite`; CSS nativo e CSS Modules restano ammessi per i casi in cui sono più leggibili. Niente SCSS, CSS-in-JS runtime o una seconda pipeline CSS.
- **Componenti**: shadcn/ui con Base UI (`base-nova`, `neutral`) e file sorgente nel repository. Le primitive stanno in `apps/web/src/design-system/primitives/`, le composizioni riutilizzabili in `patterns/`, i token e il CSS globale in `theme/`.
- **Dipendenze UI**: Lucide React come unico set di icone, CVA per le varianti reali, `cn` centralizzato in `design-system/lib/utils.ts`, Sonner per i toast. Niente DaisyUI o un secondo design system.
- **Token**: custom properties semantiche in `tokens.css`, mappatura `@theme inline` in `global.css`, palette light/dark in OKLCH, `--success`, `--warning`, `--info`, radius e durate di motion. I componenti usano token semantici, non colori di palette.
- **Tema**: `ThemeProvider` applicativo con preferenza `light`, `dark` o `system`, persistenza in `localStorage`, sincronizzazione tra tab e bootstrap inline prima del primo paint.
- **Configurazione**: `VITE_API_BASE_URL` è tipizzata e validata con Zod all'avvio; vuota significa stessa origine tramite il proxy Vite. Le variabili web non contengono segreti.
- **Gate**: `just web-check` esegue formattazione Biome, lint CSS Biome con direttive Tailwind, Oxlint type-aware con `jsx-a11y`, typecheck e test Vitest su progetti Node e jsdom. `just build` produce la build di produzione ed è incluso in `just prepush` e `just ci`. Playwright usa porte E2E dedicate e `@axe-core/playwright` sui flussi critici.
- **Fuori scope**: SSR, Next.js, routing applicativo, stato globale, Storybook, TanStack Table e Motion restano decisioni separate da adottare solo con un'esigenza concreta e una nuova ADR.

## Conseguenze

- Le app derivate partono con un design system accessibile, tokens modificabili in un punto e una pipeline UI già verificata.
- Il repository possiede i file shadcn: gli aggiornamenti vanno confrontati e revisionati, non sovrascritti automaticamente.
- Aumentano le dipendenze di build e runtime della UI. Il bundle iniziale include React, Base UI, Sonner e le primitive importate; il CSS di produzione va misurato a ogni crescita significativa.
- I componenti nuovi si aggiungono con il CLI shadcn usando gli alias di `components.json`, non copiando snippet incompleti.
- La migrazione non cambia i contratti né le altre superfici: CLI, API e MCP restano invariati.
- `just web-check` non esegue più la build; la build è una recipe pubblica separata (`just build`) e resta obbligatoria nei gate che la richiedono.

## Enforcement

- `just web-check`: Biome format-check, lint CSS, Oxlint type-aware, typecheck e Vitest.
- `just build`: build Vite di produzione, inclusa in `just prepush` e `just ci`.
- `just test-e2e`: Playwright con audit axe, tema chiaro/scuro, tastiera e viewport stretto.
- `components.json` e gli alias impediscono percorsi divergenti per le primitive.
- `just build` esegue Vite e il budget gzip in `apps/web/budget.json`; una crescita oltre soglia richiede una decisione esplicita.
- Icone, varianti e token sono verificati da lint e review; niente classi Tailwind costruite dinamicamente.

## Alternative considerate

- **Mantenere CSS nativo e componenti artigianali**: più leggero per una singola schermata, ma non è una baseline per app derivate e lascerebbe a ogni progetto primitive, temi e accessibilità.
- **DaisyUI**: aggiunge un secondo vocabolario di classi senza fornire primitive React accessibili; il Vademecum CSS la esclude dallo stack standard.
- **CSS-in-JS runtime**: aggiunge un secondo modello di styling e costi runtime senza un'esigenza misurata.
- **Next.js o SSR**: non servono al caso d'uso e cambierebbero modello di deploy e runtime.
- **Storybook, TanStack Table, Motion subito**: sono MAY del vademecum e vanno adottati quando esiste un bisogno reale, non per completare un catalogo.
