# Workflows

Il progetto usa il modello 3G: guide corte, gate deterministici, guard report-only. Il workflow è progettato per un agente che deve produrre un diff piccolo e verificabile.

## Ciclo di un task

1. **Baseline**: `just prepush` deve essere verde prima di iniziare. Se è rosso, ripristina la salute o segnala il blocco.
2. **Contesto**: leggi `AGENTS.md`, `docs/PROJECT.md`, la memory bank e le ADR/PDR pertinenti.
3. **Branch**: nel flusso strutturato crea un branch dedicato con il naming della sezione § Branching, PR e worktree. Nel checkout principale, quando l'utente non chiede branch o PR, lavora sul working tree corrente e lascia il commit all'utente.
4. **Piano**: il task deve stare in una sessione. Se è troppo grande, spezzalo.
5. **Red**: scrivi il test e guardalo fallire.
6. **Green**: implementa il minimo.
7. **Refactor**: migliora senza cambiare comportamento.
8. **Documentazione**: aggiorna docs, ADR e PDR nello stesso commit.
9. **Gate**: `just precommit` durante, `just prepush` prima della consegna.
10. **PR**: solo dopo consenso esplicito a commit, push e PR, usa `tools/scripts/finish-task.sh` o `gh pr create`; allega il report.

## Branching, PR e worktree

Il modello strutturato è **un task = un branch = una PR**. Il lavoro isolato o parallelo vive in un branch o in un worktree dedicato.

Il naming è:

```text
<tipo>/<issue>-<slug>     feat/42-rate-limiting
<tipo>/<slug>             fix/typo-readme          (solo task troppo piccoli per un'issue)
```

I tipi sono quelli dei conventional commit: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`. Il numero dell'issue GitHub è il progressivo univoco e dà tracciabilità issue → branch → PR.

### Workspace di sviluppo principale

Quando `realpath $(pwd)` corrisponde a `/home/dati/workspace/py-boilerplate` e l'utente non richiede esplicitamente un branch/PR, il flusso di default non è il modello branch + PR, ma l'applicazione diretta delle modifiche sul working tree corrente — in genere `main` — con il commit lasciato all'utente. L'agente non crea branch autonomi né apre PR. Se serve un task isolato, l'utente lo richiede esplicitamente o si usa un worktree.

Il modello un task = un branch = una PR resta valido per lavoro strutturato, autonomo o in parallelo. `tools/scripts/finish-task.sh` rifiuta di girare su `main`: è coerente con questa eccezione, perché nel checkout principale il commit resta all'utente.

### Review e merge

Il ruleset di `main` richiede una PR con review CODEOWNERS. Il maintainer ha il bypass `always` per le emergenze: l'uso va dichiarato nel report e non serve a chiudere PR rosse. Non fare force-push su un branch con review aperta salvo necessità e accordo.

## Fast path docs-only

`just precommit` e `just prepush` calcolano lo scope del diff con `tools/scripts/diff_scope.py`. Se tutti i file modificati corrispondono ai pattern in `DOCS_ONLY_PATTERNS` del justfile, eseguono solo i gate documentali e di sicurezza.

I pattern sono:

```text
docs/
*.md
.github/workflows/
.githooks/
```

Qualsiasi dubbio risolve in `full`: nessun git, nessun upstream, diff vuoto o pattern assenti non attivano il fast path. La lista è protetta da CODEOWNERS e non va estesa per far passare un diff misto.

## Gate

| Gate | Quando | Contenuto |
|---|---|---|
| `just precommit` | Hook di commit | Formattazione, lint, shellcheck, docs, web check, CodeScene safeguard, secret staged, unit |
| `just prepush` | Hook di push | Analisi statica completa, web check, CodeScene changeset, sicurezza, suite principali, coverage |
| `just ci` | Locale o CI | Tutto, inclusi E2E Python, Playwright, package check e compatibilità Python |

Non usare `--no-verify`, `SKIP` o `git commit -n`. Se un hook fallisce, correggi il problema.

Gli hook versionati eseguono già `just precommit` al commit e `just prepush` al push: non rilanciarli a mano subito prima di commit/push. `tools/scripts/finish-task.sh` non li duplica.

## Commit

Formato:

```text
<prefisso>: <sintesi in italiano>

- dettaglio del diff
- test aggiunti o modificati
- decisioni o documentazione aggiornate
```

Prefissi ammessi: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `revert`.

Mantieni `tmp/commit-message.md` aggiornato durante il lavoro. Azzeralo quando parti da `git status` pulito; integralo o correggilo altrimenti. `tmp/` è gitignored. Il messaggio deve descrivere l'intero diff, non solo l'ultima modifica, e non usa hard wrap.

Il commit non è automatico a fine iterazione. L'agente prepara la bozza e crea commit, push e PR solo quando l'utente lo richiede esplicitamente; nel checkout principale il commit resta all'utente. Quando autorizzato, usa `tools/scripts/finish-task.sh` su un branch dedicato.

## Pull request

- Apri una PR solo dopo consenso esplicito a commit, push e PR.
- Una PR per task; niente refactor non correlati.
- Descrivi cosa cambia, perché, i test eseguiti e i rischi residui.
- Includi l'output verbatim dei comandi di gate.
- Se la PR è prodotta da un agente, richiedi review umana esplicita.
- Non fare force-push su un branch con review aperta salvo necessità e accordo.

## Definition of Done

Un task è completo solo se:

- i criteri di accettazione sono soddisfatti;
- il comportamento è coperto da test appropriati;
- ogni bug fix ha un regression test;
- ogni nuovo test è stato visto fallire prima dell'implementazione;
- happy path, errori e boundary case sono coperti;
- la coverage non è diminuita e nessuna soglia è stata abbassata;
- nessun gate è stato aggirato e il diff non contiene modifiche ingiustificate a justfile, hook, `pyproject.toml`, `.importlinter` o soglie;
- non esistono nuovi warning o suppression ingiustificate;
- il typing passa mypy strict;
- i dati esterni sono validati a runtime;
- non ci sono dipendenze mancanti, inutilizzate o nel gruppo errato;
- le regole architetturali passano e non ci sono cicli;
- non ci sono import side effect o stato globale non intenzionale;
- ogni nuovo caso d'uso è esposto sulle superfici decise e la mappa in `docs/PROJECT.md` è aggiornata;
- documentazione, ADR e PDR sono aggiornate nello stesso commit;
- `just web-check` passa (Biome, Oxlint, TypeScript, Vitest) e `just build` passa;
- i flussi UI nuovi hanno un test Playwright o una motivazione esplicita;
- il Code Health dei file toccati non è degradato (`just codescene-safeguard` / `just codescene-changeset`);
- nessun token CodeScene o configurazione OAuth è finito nel repository;
- `npm audit --omit=dev --audit-level=high` è verde;
- `just prepush` passa;
- il report finale cita l'output reale;
- il messaggio in `tmp/commit-message.md` descrive l'intero diff;
- rischi e test non eseguiti sono dichiarati;
- il diff non contiene modifiche estranee.

## Rilascio e rollback

Il progetto non pubblica wheel né immagini e non esegue deploy. Il "rilascio" è il merge su `main`. Un rollback si fa con un revert esplicito e una PR, non con force-push o riscrittura della storia.

## Retrospettiva

Periodicamente, e comunque dopo un ciclo intenso, esegui una retrospettiva sui fallimenti del processo: gate ignorati, istruzioni inefficaci, test fragili, API allucinate, context rot. Le conclusioni diventano modifiche a `AGENTS.md`, alle guide o ai guard, tramite PR. Il sistema migliora per evidenza, non per accumulo di regole.

## CodeScene e UI

`just precommit` esegue `just codescene-safeguard` sui file staged/modificati; `just prepush` esegue `just codescene-changeset` sul branch. Se l'MCP CodeScene non è autenticato, il gate fallisce chiuso: autentica o riporta il blocker. Non abbassare `.codescene-thresholds`.

La UI ha un ciclo separato: `just web-check` per formattazione, lint, typecheck e test Vitest; `just build` per la build di produzione; `just test-e2e` per i flussi Playwright con audit axe. In CI il job `e2e` installa Chromium e avvia API e Vite tramite `playwright.config.ts` su porte dedicate.
