# Sessione 2026-11-16 — Baseline frontend avanzata

- Obiettivo: allineare `apps/web` allo stack del Vademecum CSS e del Vademecum TypeScript, così che le app derivate partano con design system, temi, build e gate UI già pronti.
- Fatto: migrata la UI a Tailwind CSS 4 + shadcn/ui con Base UI; aggiunti token semantici light/dark, `ThemeProvider`, toggle del tema, shell applicativa, primitive (form, overlay, menu, tab, feedback, skeleton, empty, toast), pattern `Page`; riscritta la feature `greeting` con stati idle/loading/success/error; aggiunti `VITE_API_BASE_URL` validata con Zod, Oxlint type-aware con `jsx-a11y`, Biome CSS, Vitest jsdom con Testing Library, Playwright con axe, porte E2E dedicate, recipe `just build` e budget gzip.
- Test eseguiti: `just web-check` (Biome, Oxlint, typecheck, 20 test Vitest), `just build` con budget, `just test-e2e` (3 E2E Python + 5 Playwright con axe), `just docs-check`, `just prepush` e `just ci` completi.
- Decisioni: ADR-0011 (design system e gate UI), PDR-0003 (tema e shell). ADR-0009 e PDR-0002 restano valide per React/Vite/Playwright e per il comportamento del caso d'uso.
- Rischi aperti: bundle JS iniziale da monitorare quando crescono feature e primitive; l’audit dev segnala vulnerabilità moderate in tooling shadcn, mentre l’audit di produzione è pulito; routing, SSR, Storybook, TanStack Table e Motion restano decisioni separate.
- Prossima azione: misurare il budget CSS/JS dopo la prima feature reale e valutare il ratchet UI.
