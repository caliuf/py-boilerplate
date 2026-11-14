# Sessione 2026-11-14 — UI web e CodeScene

- Obiettivo: aggiungere una UI React/Vite equivalente a `ts-boilerplate` e integrare il progetto CodeScene `87780`.
- Fatto: creati `apps/web` (design system, feature greeting, contratti Zod, Vitest), Playwright E2E, workspace npm, Biome, build Vite; aggiunti `.kilo/kilo.jsonc`, gate CodeScene safeguard/changeset/ratchet e baseline `.codescene-thresholds`.
- Test eseguiti: `just web-check`, `just test-e2e` (3 E2E Python + 2 Playwright), `just codescene-safeguard`, contract test web, suite Python.
- Decisioni: ADR-0009 (UI), ADR-0010 (CodeScene), PDR-0002 (UI). CodeScene locale in precommit/prepush; ratchet Cloud separato con REST token.
- Rischi aperti: il ratchet richiede un REST token; CodeScene MCP richiede OAuth locale; la UI non ha SSR/auth.
- Prossima azione: aggiornare il progetto Cloud dopo il push e verificare che il Code Health resti sopra la baseline.
