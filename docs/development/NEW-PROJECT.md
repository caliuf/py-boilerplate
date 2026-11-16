# Adottare il boilerplate

Questa checklist trasforma `py-boilerplate` in un progetto reale. Non saltare i passi che riguardano decisioni: il boilerplate è un punto di partenza, non una scelta di prodotto già fatta.

## 1. Decisioni iniziali

- Scegli la licenza e aggiungi il file `LICENSE`.
- Definisci il nome del progetto, il package Python e il prefisso degli errori.
- Decidi le superfici reali: CLI, API, MCP, job, UI. Rimuovi quelle che non servono.
- Scrivi la prima PDR sul prodotto e la prima ADR sull'architettura.
- Sostituisci il contenuto di `docs/PROJECT.md`.

## 2. Rinominare i placeholder

Cerca e sostituisci in modo controllato:

| Placeholder | Nuovo valore |
|---|---|
| `py-boilerplate` | nome del progetto o del comando |
| `py_boilerplate` | nome del package Python |
| `py-boilerplate-api` | entry point API, se resta |
| `py-boilerplate-mcp` | entry point MCP, se resta |
| `@py-boilerplate/web` | nome del workspace web |
| `py-boilerplate` in `apps/web/index.html` e `GreetingPage` | titolo della UI |
| `87780` in `.kilo/kilo.jsonc`, `CODESCENE.md` e memoria | project id CodeScene del nuovo progetto |
| `hello-world` | nome del primo caso d'uso reale |
| `HelloWorldInput`, `HelloWorldOutput` | DTO reali |
| `urn:py-boilerplate:error:` | URN del progetto |
| `@caliuf` in `CODEOWNERS` | maintainer o team reale |
| `caliuf/py-boilerplate` nei link | URL del nuovo repository |

Aggiorna anche `docs/INDEX.md`, `README.md`, `SECURITY.md`, `conventions.conf` e i test che citano i placeholder.

## 3. Rimuovere il blueprint

Quando il progetto non è più un boilerplate:

- rimuovi `docs/init/` e il riferimento nell'indice;
- rimuovi `docs/development/NEW-PROJECT.md` o sostituiscilo con la guida del progetto;
- rimuovi le ADR/PDR dimostrative se non descrivono più il progetto reale;
- se non hai una UI, rimuovi `apps/web/`, Playwright, `playwright.config.ts`, i test `.spec.ts` e le recipe web;
- mantieni la memory bank e aggiornala.

## 4. Configurare GitHub

- Crea il repository pubblico o privato e aggiorna il remote.
- Configura il ruleset con i check reali del nuovo progetto.
- Abilita Dependabot, dependency graph, secret scanning e push protection quando disponibili.
- Verifica che `CODEOWNERS` protegga i file di gate.
- Aggiorna il workflow CI se cambi job o nomi dei check.

## 5. Configurare la qualità

- Mantieni Ruff, mypy strict, pytest, coverage, Import Linter e deptry.
- Mantieni Biome, Oxlint con `jsx-a11y`, TypeScript strict, Vitest con progetto jsdom, Playwright e axe se adotti la UI.
- Se cambi il design system, aggiorna `apps/web/components.json`, i token e l’ADR pertinente; non aggiungere un secondo design system.
- Aggiorna il mirror Zod `apps/web/src/contracts.ts` e il contract test web quando cambi i contratti.
- Aggiorna i contratti Import Linter quando cambi i bounded context.
- Imposta la baseline di coverage sul valore reale del nuovo progetto, senza abbassare le soglie esistenti.
- Aggiorna `.python-version`, la matrix CI e `package.json` solo dopo aver verificato dipendenze e wheel.
- Aggiungi una ADR per ogni dipendenza significativa.
- Imposta `.codescene-thresholds` sulla baseline reale del nuovo progetto; non riusare i valori del boilerplate.

## 6. Configurare l'ambiente

- Aggiorna `.env.default` e `.env.example` con le variabili reali.
- Non committare segreti.
- Aggiorna `bin/` con il nome del comando reale.
- Aggiorna `WEB_PORT` e le porte del `playwright.config.ts` se cambi la UI.
- Verifica `just setup` e `just doctor` su una clone pulita.

## 7. CodeScene (se adottato)

Se mantieni CodeScene:

1. Crea un progetto Cloud nuovo che punta al remote del nuovo repository; non riusare `87780`.
2. Aggiorna `CS_DEFAULT_PROJECT_ID` in `.kilo/kilo.jsonc`, `CODESCENE.md`, `AGENTS.md` e la memoria.
3. Autentica l'MCP: `npx -y @codescene/codehealth-mcp auth`.
4. Crea un REST API token e salvalo in `~/.codescene/token` o `CODESCENE_API_TOKEN` (fuori dal git).
5. Misura la baseline reale e aggiorna `.codescene-thresholds`; poi esegui `just codescene-ratchet`.
6. Se non adotti CodeScene, rimuovi `.kilo/`, le recipe `codescene-*`, i riferimenti in hook, AGENTS, ADR, docs e memoria.

## 8. Prima esecuzione completa

```bash
just setup
just doctor
just ci
```

`just ci` deve passare su una clone pulita, senza modifiche non committate e senza tool mancanti. Include Playwright: assicurati che il browser Chromium sia installato e che le porte E2E 15100 e 18100 siano libere. La suite non riusa server di altre checkout.

## 8. Primo ciclo agentico reale

Esegui almeno un task completo con un agente:

1. briefing;
2. lettura delle guide;
3. TDD;
4. `just precommit`;
5. `just prepush`;
6. PR e review umana;
7. report finale con output verbatim.

Correggi le parti del processo che risultano ambigue. Il boilerplate è vivo solo se il ciclo funziona davvero.
