# Workflows

Il progetto usa il modello 3G: guide corte, gate deterministici, guard report-only. Il workflow è progettato per un agente che deve produrre un diff piccolo e verificabile.

## Ciclo di un task

1. **Baseline**: `just prepush` deve essere verde prima di iniziare. Se è rosso, ripristina la salute o segnala il blocco.
2. **Contesto**: leggi `AGENTS.md`, `docs/PROJECT.md`, la memory bank e le ADR/PDR pertinenti.
3. **Branch**: crea `feat/<scope>`, `fix/<scope>` o `refactor/<scope>`. Non lavorare su `main`.
4. **Piano**: il task deve stare in una sessione. Se è troppo grande, spezzalo.
5. **Red**: scrivi il test e guardalo fallire.
6. **Green**: implementa il minimo.
7. **Refactor**: migliora senza cambiare comportamento.
8. **Documentazione**: aggiorna docs, ADR e PDR nello stesso commit.
9. **Gate**: `just precommit` durante, `just prepush` prima della consegna.
10. **PR**: usa `tools/scripts/finish-task.sh` o `gh pr create`; allega il report.

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
| `just precommit` | Hook di commit | Formattazione, lint, shellcheck, docs, secret staged, unit |
| `just prepush` | Hook di push | Analisi statica completa, sicurezza, suite principali, coverage |
| `just ci` | Locale o CI | Tutto, inclusi E2E, package check e compatibilità Python |

Non usare `--no-verify`, `SKIP` o `git commit -n`. Se un hook fallisce, correggi il problema.

## Commit

Formato:

```text
<prefisso>: <sintesi in italiano>

- dettaglio del diff
- test aggiunti o modificati
- decisioni o documentazione aggiornate
```

Prefissi ammessi: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `revert`.

Mantieni `tmp/commit-message.md` aggiornato durante il lavoro. Azzeralo quando parti da `git status` pulito; integralo altrimenti. `tmp/` è gitignored.

## Pull request

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
- `just prepush` passa;
- il report finale cita l'output reale;
- il messaggio in `tmp/commit-message.md` descrive l'intero diff;
- rischi e test non eseguiti sono dichiarati;
- il diff non contiene modifiche estranee.

## Rilascio e rollback

Il progetto non pubblica wheel né immagini e non esegue deploy. Il "rilascio" è il merge su `main`. Un rollback si fa con un revert esplicito e una PR, non con force-push o riscrittura della storia.

## Retrospettiva

Periodicamente, e comunque dopo un ciclo intenso, esegui una retrospettiva sui fallimenti del processo: gate ignorati, istruzioni inefficaci, test fragili, API allucinate, context rot. Le conclusioni diventano modifiche a `AGENTS.md`, alle guide o ai guard, tramite PR. Il sistema migliora per evidenza, non per accumulo di regole.
