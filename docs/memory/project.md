# Memoria di progetto

## Identità

- Repository: `caliuf/py-boilerplate`.
- Scopo: boilerplate Python agent-first derivato da `ts-boilerplate`, con il Vademecum Python in `docs/init/`.
- Caso d'uso dimostrativo: `hello-world` su CLI, API HTTP, MCP e UI web.
- Distribuzione: un package Python `py_boilerplate` con tre entry point, più la UI statica `apps/web`.

## Obiettivi stabili

- Architettura a confini verificati: dominio puro, application layer, porte e adapter.
- Validazione runtime ai confini con Pydantic.
- Typing rigoroso con mypy strict.
- TDD e suite comportamentale con contract test cross-surface, Vitest e Playwright.
- Gate locali e CI che impediscono scorciatoie.
- Documentazione gerarchica, memory bank portabile e CodeScene come gate di maintainability.

## Vincoli

- Python minimo 3.14; pin 3.14.6; CI su 3.14.
- `uv` gestisce Python e `uv.lock`; npm gestisce il workspace web e `package-lock.json`.
- UI React/Vite separata con design system Tailwind 4 + shadcn/Base UI, tema chiaro/scuro e gate UI; nessun database, coda o worker.
- Nessuna chiamata a servizi esterni a runtime.
- La prosa non usa hard wrap.
- `docs/init/` è congelato.
- Il maintainer in `CODEOWNERS` è il decisore finale.

## Workflow

- Modello strutturato: un task = un branch = una PR, con naming `<tipo>/<issue>-<slug>` oppure `<tipo>/<slug>` per task molto piccoli; i tipi sono quelli conventional.
- Nel checkout principale `/home/dati/workspace/py-boilerplate`, quando l'utente non chiede branch o PR, si lavora sul working tree corrente (`main`) e il commit resta all'utente; l'agente non crea branch autonomi né PR.
- L'agente mantiene `tmp/commit-message.md` come bozza del messaggio (prefisso conventional, sintesi in italiano, riga vuota, lista puntata, niente hard wrap) e non crea commit, push o PR senza richiesta esplicita.
- Gli hook versionati eseguono `just precommit` al commit e `just prepush` al push; non vanno duplicati a mano. `tools/scripts/finish-task.sh` si usa solo su branch dedicato e con consenso esplicito.

## Stato sintetico

- Dominio, contratti, CLI, API, MCP, UI web, design system, tema e package check sono implementati e verdi.
- La suite locale copre unit, integration, contract, component web ed E2E con audit axe.
- La coverage Python misurata è 100% linee e 100% branch; la baseline è 95/90. La UI usa test Vitest e Playwright, non la coverage Python.
- La CI include quality, integration-and-coverage, python-compatibility, e2e (Playwright) e dependency-review.
- La slow lane include CodeQL, gitleaks storico, guard e link check.
- CodeScene Cloud `87780` è configurato; baseline Hotspot 9.10 e Average 9.76.
- La licenza non è ancora stata scelta.

## Prossimi passi possibili

- Scegliere la licenza.
- Aggiungere un caso d'uso reale in un progetto derivato.
- Aggiornare il progetto CodeScene `87780` dopo i push e mantenere il ratchet sopra la baseline.
- Valutare routing, SSR, Storybook, TanStack Table o Motion solo quando un progetto derivato ne ha un bisogno reale, con una nuova ADR.
- Estendere la UI con una nuova PDR e una nuova ADR se cambia il prodotto.
