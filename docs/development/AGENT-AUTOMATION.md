# Agent automation

Il repository è progettato per ridurre i round-trip di un agente e per rendere verificabile ciò che dichiara. Le automazioni sono locali, versionate e non modificano il codice al posto dell'agente.

## Inizio sessione

```bash
tools/scripts/agent-briefing.sh
```

Il briefing stampa in un'unica chiamata:

- identità del repository e dell'eventuale worktree;
- branch, stato e ultimi commit;
- presenza dei tool di gate;
- contenuto di `docs/memory/project.md`, `environment.md` e `corrections.md`;
- bozza del messaggio di commit in `tmp/commit-message.md`;
- PR e issue aperte, se `gh` è disponibile.

È read-only. Se un tool obbligatorio manca, il briefing lo segnala: non ignorare l'avviso.

## Memoria

La memory bank è in `docs/memory/`. All'inizio di un task leggi `project.md` e `environment.md`. Quando scopri un vincolo o una correzione, aggiorna il file appropriato nello stesso commit del codice o in un commit docs dedicato. Le decisioni formali vanno in ADR/PDR; la memory bank rimanda a esse.

## Bozza del messaggio di commit

Mantieni `tmp/commit-message.md` con il messaggio che intendi proporre. Il file è gitignored.

- Se parti da `git status` pulito, azzeralo.
- Se integri lavoro già presente, aggiornalo o correggilo.
- Il messaggio deve descrivere l'intero diff, non solo l'ultima modifica.

`tools/scripts/finish-task.sh` legge questo file se non riceve `-m`.

## Chiusura del task

```bash
tools/scripts/finish-task.sh
```

Lo script:

1. verifica di non essere su `main`;
2. verifica che gli hook versionati siano attivi;
3. committa i file staged, lasciando che l'hook esegua `just precommit`;
4. pusha, lasciando che l'hook esegua `just prepush`;
5. apre una PR se non ne esiste già una per il branch.

Non duplicare i gate a mano prima dello script: gli hook li eseguono già. Se un gate fallisce, lo script si ferma.

## PR e issue

```bash
tools/scripts/gh-prs.sh
tools/scripts/gh-prs.sh view <numero>
```

`gh-prs.sh` è read-only e mostra stato, autori, branch, file e check. Per creare, commentare o chiudere una PR usa `gh` direttamente, seguendo [`GITHUB-CLI.md`](GITHUB-CLI.md).

## Diagnostica memoria Kilo

```bash
tools/scripts/kilo-memory-diagnose.sh
```

Lo script verifica se il progetto è associato alla memoria Kilo, se l'auto-inject è attivo e se la memory bank del repository è presente. È diagnostico: non modifica la configurazione.

## Delega ai sub-agent

Se il modello dell'agente principale non è già low-cost, applica la politica `sub-agent-first` del contratto globale: delega ricerca, analisi, modifiche e validazioni a pochi sub-agent ben raggruppati. L'agente principale conserva perimetro, decisioni, conflitti, approvazioni e report finale.

Non impostare modelli alternativi nei task se non richiesto. Ogni sub-agent deve restituire evidenze concise: file e simboli, modifiche, comandi, esito e rischi.

## Report finale

Il report deve essere evidence-based:

1. cosa è cambiato;
2. test aggiunti o modificati;
3. comandi eseguiti e output verbatim;
4. delta di coverage e qualità;
5. risultati di sicurezza e analisi statica;
6. ADR/PDR e documentazione aggiornate;
7. versione Python e modifiche al lockfile;
8. rischi residui e domande aperte.

Non dichiarare "i test passano" se non li hai eseguiti. La CI rieseguirà e farà fede.
