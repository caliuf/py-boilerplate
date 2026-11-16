# Confini e regole di dipendenza

I confini architetturali non sono una convenzione implicita: sono contratti eseguibili in `.importlinter` e vengono verificati da `just arch` e `just prepush`.

## Direzione delle dipendenze

```text
entrypoints
    ↓
adapters
    ↓
application
    ↓
ports
    ↓
domain
```

`contracts` è una foglia trasversale: può essere importata da application, ports, adapters ed entrypoints; non importa nulla degli altri moduli interni.

## Contratti Import Linter

Il file `.importlinter` definisce quattro contratti:

| Contratto | Regola |
|---|---|
| `Layered architecture` | `entrypoints` sopra `adapters`, sopra `application`, sopra `ports`, sopra `domain`; le import possono andare solo verso il basso |
| `Contracts are a dependency leaf` | `py_boilerplate.contracts` non importa `greetings`, `adapters` o `entrypoints` |
| `Domain is pure` | `greetings.domain` non importa contratti, application, ports, adapter o entrypoint |
| `Entrypoints are independent` | CLI, API e MCP non importano i rispettivi package |

L'ordine degli strati è deliberato: l'application layer dipende dalle porte, non viceversa. Un adapter implementa una porta e può essere importato solo dal composition root dell'entrypoint.

## Tabella delle import consentite

| Modulo sorgente | Può importare | Non può importare |
|---|---|---|
| `greetings.domain` | standard library | tutto il resto del progetto |
| `greetings.ports` | `contracts` | domain, application, adapters, entrypoints |
| `greetings.application` | domain, ports, contracts | adapters, entrypoints, framework |
| `contracts` | standard library e Pydantic | qualsiasi modulo interno |
| `adapters` | contracts, porte | entrypoints, application |
| `entrypoints.cli` | application, ports, contracts, adapters, CLI internals | API, MCP |
| `entrypoints.api` | application, ports, contracts, adapters, API internals | CLI, MCP |
| `entrypoints.mcp` | application, ports, contracts, adapters, MCP internals | CLI, API |

Le regole sono più restrittive della tabella dove Import Linter lo consente: per esempio il dominio non può importare nemmeno `contracts`, anche se in teoria sarebbe un tipo condiviso.

## Confine della UI web

`apps/web` è un'app Node/React separata e non fa parte del root package Python. Le regole non sono verificate da Import Linter ma dai gate della UI.

La direzione delle dipendenze dentro la UI è:

```text
app → features → design-system
  ↘ config, contracts
```

- `app/` compone la shell, i provider e le feature; non contiene logica di caso d'uso.
- `features/<nome>/` contiene pagina, hook di stato server, client API e test; non crea primitive interattive.
- `design-system/` non importa `app/` o `features/`; espone token, primitive e pattern.
- `config/` valida l'ambiente; `contracts.ts` è il mirror Zod dei contratti canonici.
- Le primitive possono importare `design-system/lib/utils` e altre primitive, non le feature.

| Regola | Verifica |
|---|---|
| La UI non importa `src/py_boilerplate` né codice Python | Code review, struttura del workspace, assenza di path Python in `apps/web` |
| La UI parla all'API solo via HTTP (`${VITE_API_BASE_URL}/api`) | `hello-world-api.ts`, `config/env.ts`, Playwright E2E |
| Le risposte esterne sono validate a runtime con Zod | `contracts.ts`, Vitest, `test_web_contract.py` |
| Le feature compongono il design system | struttura `features/greeting` + `design-system`; Oxlint |
| I componenti usano token semantici e classi statiche | Biome CSS, Oxlint, code review |
| La UI non duplica il dominio | il caso d'uso vive solo in `greetings/application` |
| TypeScript strict, lint e test | `just web-check` |
| Build di produzione e budget | `just build` |
| Flussi browser reali e accessibilità | Playwright E2E con axe |

`apps/web/src/contracts.ts` è un mirror client-side, non una seconda fonte canonica. La fonte canonica resta Pydantic/OpenAPI; il contract test Python verifica che i vincoli condivisi non divergano.

## Regole non automate ma obbligatorie

- Nessun `sys.path` hack, nessun import relativo al working directory, nessun import shadowing.
- Nessun side effect all'import: niente logging, connessioni, lettura di file o avvio di worker a livello di modulo.
- Nessuno stato globale mutabile: le dipendenze si passano esplicitamente.
- Nessun service locator o container DI: il wiring è nei composition root.
- Nessun import di `tests` da `src`.
- Nessun `print()` in `src`: Ruff `T20` lo vieta.
- Nessun framework nel dominio o nell'application layer.

## Aggiungere un bounded context

1. Crea `src/py_boilerplate/<context>/` con `domain/`, `application/` e `ports/`.
2. Aggiungi i contratti condivisi in `contracts/` solo se servono a più bounded context.
3. Aggiungi un contratto Import Linter per il nuovo contesto se introduce una direzione non coperta da quelli esistenti.
4. Aggiungi test unit e integration attraverso le API pubbliche.
5. Aggiorna `docs/architecture/OVERVIEW.md` e, se cambia il prodotto, la PDR pertinente.

## Aggiungere una superficie

1. Crea `src/py_boilerplate/entrypoints/<surface>/` con un composition root e adapter sottili.
2. Riusa il caso d'uso e i contratti; non duplicare la logica.
3. Aggiungi il contratto Import Linter per impedire import incrociati tra entrypoint.
4. Aggiungi il contract test che verifica la stessa tassonomia errori delle altre superfici.
5. Aggiorna la mappa delle superfici in `docs/PROJECT.md`.
6. Registra una ADR se la superficie introduce un deployable, un framework o un modello di esecuzione nuovo.
7. Se la superficie è una UI web, parti dal design system esistente, aggiungi la validazione Zod delle risposte, il typecheck, i test component e l'E2E Playwright con axe; aggiorna il contract test web.

## Verifica

```bash
just arch
```

Il comando esegue `lint-imports` e fallisce se un contratto è violato. Un ciclo o un import vietato non si aggira con un ignore: si corregge il design o si aggiorna la decisione con una ADR.
