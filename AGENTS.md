# AGENTS.md

Contratto canonico di sviluppo per agenti e umani. Le istruzioni specifiche di un client devono rimandare a questo file, non duplicarne le regole. `CLAUDE.md` e `GEMINI.md` sono bridge verso questo documento.

## Contesto

Questo è un boilerplate Python con un solo caso d'uso, `hello-world`, esposto su CLI, API HTTP, MCP e UI web. Il codice è un modular monolith in `src/py_boilerplate/`. La documentazione operativa parte da [`docs/PROJECT.md`](docs/PROJECT.md) e [`docs/INDEX.md`](docs/INDEX.md).

I file in [`docs/init/`](docs/init/) sono il blueprint congelato del boilerplate. Non modificarli durante lo sviluppo ordinario: le modifiche al blueprint richiedono una decisione esplicita e un commit dedicato.

## Start here

1. Esegui `tools/scripts/agent-briefing.sh` per il dump di contesto a inizio task; `--no-prs` salta la parte GitHub. È read-only.
2. Leggi `docs/PROJECT.md` e `docs/INDEX.md`.
3. Leggi il README del bounded context o dell'entrypoint che modificherai; per la UI leggi `apps/web/README.md`.
4. Leggi le ADR e le PDR attive pertinenti.
5. Leggi `docs/memory/project.md` e `docs/memory/environment.md`; per task su tooling, workflow o adozione leggi anche `docs/memory/corrections.md`.
6. Usa solo le recipe root-level di `just` per costruire, testare e validare.

## Working rules

- Il modello strutturato è un task = un branch = una PR. Nel checkout principale, quando `realpath $(pwd)` è `/home/dati/workspace/py-boilerplate` e l'utente non chiede esplicitamente un branch o una PR, lavora sul working tree corrente (di norma `main`), non creare branch autonomi e lascia il commit all'utente. Per lavoro isolato o parallelo usa un worktree. Dettagli: `docs/development/WORKFLOWS.md` § Branching, PR e worktree.
- Prima di iniziare, verifica che i gate siano verdi: `just prepush`. Non iniziare lavoro nuovo su un codebase sotto soglia.
- Lavora test-first: red → green → refactor. Per un bug, il primo commit è un regression test che fallisce.
- Lascia il codice che tocchi migliore di come l'hai trovato, misurato dai gate. Non fare refactor o upgrade non correlati.
- Non aggiungere dipendenze senza necessità. Una dipendenza significativa richiede una ADR.
- Mantieni le API pubbliche esistenti salvo che il task le cambi esplicitamente.
- Dominio e application layer restano indipendenti da framework e runtime. Nessun import di FastAPI, MCP, argparse o structlog da `greetings/domain` e `greetings/application`.
- La UI non importa codice Python e non duplica il dominio: consuma l'API via HTTP/OpenAPI. I componenti di feature usano solo il design system; le risposte esterne sono validate con Zod.
- Valida tutti i dati esterni a runtime. Le annotazioni e i `cast` non sono validazione: usa i modelli Pydantic ai confini.
- Mantieni il codice tipizzato. Non introdurre `Any`, `cast()` o ignore comment senza necessità e senza motivo scritto.
- Quando diagnostichi un comportamento runtime, riproduci il flusso con `LOG_LEVEL=debug` e cita i log rilevanti. Non lasciare `print()` o debug temporanei.
- Non usare `# type: ignore`, `# noqa`, `# pragma: no cover` o `# nosec` senza scope ristretto, motivo e, quando applicabile, codice errore.
- Non modificare a mano `uv.lock`, `coverage-thresholds.json` o altri file generati.
- Il package manager web è npm: non usare `pnpm`, `yarn` o `bun`. Il hook `preinstall` (`tools/scripts/require-npm.mjs`) blocca gli altri manager; non committare lockfile o workspace file diversi da `package-lock.json`.
- Prima di usare un'API di libreria, verifica che esista nella versione installata leggendo sorgenti, stub o documentazione. Non fidarti della memoria.
- Non introdurre una decisione di prodotto senza PDR, né una decisione architetturale senza ADR, nello stesso commit del codice.
- Mantieni `tmp/commit-message.md` con il messaggio proposto per il lavoro in corso. Azzeralo quando parti da `git status` pulito; integralo o correggilo altrimenti. `tmp/` è gitignored. Il messaggio segue il formato di `docs/development/WORKFLOWS.md` § Commit: prefisso conventional, una riga riassuntiva in italiano, riga vuota, lista puntata con il dettaglio del diff. Non creare commit, non fare push e non aprire PR senza richiesta esplicita dell'utente.

## CodeScene

Quando l'MCP `codescene` è connesso, Code Health è l'autorità per la maintainability. Non indovinare punteggi o verdetti: usa i tool MCP o le recipe `just codescene-safeguard`, `just codescene-changeset` e `just codescene-ratchet`. Il progetto Cloud è `87780`; la configurazione e i limiti sono in [`docs/development/CODESCENE.md`](docs/development/CODESCENE.md).

- Non abbassare `.codescene-thresholds` per far passare un diff: rifattorizza o ripristina il comportamento.
- Non committare token CodeScene, contenuto di `~/.codescene/token` o configurazioni OAuth.
- Se un file toccato degrada il Code Health, rifattorizza prima di chiudere il task.

## Gate circumvention — vietato

- Non usare `--no-verify`, `SKIP`, `git commit -n` o altri modi per saltare hook e gate.
- Non abbassare soglie di coverage o qualità: possono solo salire.
- Non estendere ignore-list, esclusioni o suppression per far passare un gate.
- Non modificare `justfile`, hook, `pyproject.toml`, `.importlinter`, `coverage-thresholds.json`, `.codescene-thresholds` o `.kilo/` per aggirare un fallimento.
- Se un gate fallisce e non trovi il rimedio, fermati e riporta il fallimento esatto. Non aggirarlo.

## Testing

- Preferisci test di integrazione attraverso le API pubbliche. Usa unit test dove sono più chiari.
- Usa mock solo per confini esterni o non deterministici.
- I test devono essere isolati, deterministici, veloci e comportamentali.
- Non chiamare servizi esterni o LLM reali salvo richiesta esplicita.
- Copri happy path, errori, boundary case e permessi rilevanti. Per timeout, retry, idempotenza e cancellazione, aggiungi test dedicati quando pertinenti.
- Un test che non hai visto fallire è sospetto: verifica il ciclo red → green.
- La suite E2E avvia processi reali per CLI, API e MCP. Non sostituirla con mock del processo.

## Validation

- Durante lo sviluppo esegui `just precommit`.
- Prima della consegna esegui `just prepush`.
- Per la pipeline completa esegui `just ci`.
- Non rilanciare `just precommit` o `just prepush` subito prima di `git commit` o `git push`: gli hook versionati li eseguono già. Se hai il consenso esplicito a commit, push e PR, usa `tools/scripts/finish-task.sh` su un branch dedicato; altrimenti fermati al report e lascia le modifiche nel working tree.
- Se un comando richiesto non può girare, riporta il motivo esatto e l'output.
- Non dichiarare che un check è passato senza averlo eseguito. Nel report finale cita l'output effettivo.

## Documentazione

- Scrivi in italiano; mantieni identificatori, comandi e nomi di API in inglese.
- Non fare hard wrap della prosa a 80 caratteri o a qualsiasi altra lunghezza. Un paragrafo per riga, editabile e leggibile.
- Aggiorna documentazione, ADR e PDR nello stesso commit del codice che le implementa.
- Non creare documenti che duplicano `AGENTS.md` o il Vademecum. Rimanda alle fonti canoniche.
- Il file `docs/init/Vademecum Python.md` è il blueprint congelato: non riscriverlo.
- La mappa delle superfici in `docs/PROJECT.md` va aggiornata quando aggiungi un comando CLI, una route o un tool MCP.

## Git e GitHub

- Usa `git --no-pager` per ogni comando Git: un pager interattivo blocca la shell dell'agente.
- Non usare comandi Git distruttivi. Non riscrivere commit o fare force-push senza richiesta esplicita.
- Non cancellare file non correlati o untracked.
- Sposta o rinomina i file con `git mv`, mai cancellando e ricreando il file, così Git registra la rinomina e la cronologia resta leggibile con `git log --follow` e `git blame`. Quando possibile tieni un movimento puro in un commit dedicato, separato dalle modifiche di contenuto.
- Messaggi di commit in italiano, con prefisso convenzionale (`feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`, `ci`, `revert`), una riga riassuntiva, riga vuota e una lista puntata con il dettaglio del diff. Il messaggio proposto vive in `tmp/commit-message.md`; niente hard wrap.
- Non creare commit, non fare push e non aprire PR, remote o modifiche alle impostazioni GitHub senza richiesta esplicita dell'utente. Quando autorizzato, usa `tools/scripts/finish-task.sh` solo su un branch dedicato.
- Un bug fix porta un regression test. Una feature porta test e documentazione.
- Apri PR piccole; non mescolare refactor non correlati.
- Usa `gh` per PR, issue e check. Per i comandi di sola lettura vedi [`docs/development/GITHUB-CLI.md`](docs/development/GITHUB-CLI.md).

## Final report

Riporta:

1. cosa è cambiato;
2. test aggiunti o modificati;
3. comandi eseguiti, con risultati verbatim;
4. delta di coverage e qualità;
5. risultati di sicurezza, analisi statica, web check, Playwright e CodeScene;
6. ADR/PDR e documentazione aggiornate;
7. versione Python e modifiche a dipendenze/lockfile;
8. rischi residui o domande aperte;
9. messaggio di commit proposto in `tmp/commit-message.md`, in un code block.
