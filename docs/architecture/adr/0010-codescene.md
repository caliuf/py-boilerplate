# ADR-0010 — CodeScene Code Health come gate locale

- Stato: Accettata
- Data: 2026-11-14
- Supersede: nessuna

## Contesto

Il repository adotta il modello 3G e il principio della Boy Scout Rule misurata. Lint, typing e coverage non misurano complessità, hotspot e debito tecnico. Il maintainer ha creato il progetto CodeScene Cloud `87780` (job `8428088`), che analizza il repository. Serve un controllo locale che usi dati freschi sul working tree e un ratchet di progetto che non scenda mai.

## Decisione

Integriamo CodeScene in due livelli:

- **MCP locale** in `.kilo/kilo.jsonc`, pinnato a `CS_DEFAULT_PROJECT_ID=87780`, tramite `npx -y @codescene/codehealth-mcp`.
- **Gate di working tree** in `.kilo/scripts/codescene_gate.py`:
  - `just codescene-safeguard` esegue `pre_commit_code_health_safeguard` sui file staged/modificati ed è incluso in `just precommit`.
  - `just codescene-changeset` esegue `analyze_change_set` sul branch rispetto a `origin/main` ed è incluso in `just prepush`.
  - Il gate fallisce chiuso con exit 2 se il progetto o l'MCP non sono disponibili.
- **Ratchet di progetto** in `tools/scripts/codescene-ratchet.sh`: confronta Hotspot e Average Code Health del progetto Cloud con `.codescene-thresholds` e alza i floor quando il punteggio migliora. Le soglie possono solo salire.
- La baseline iniziale, misurata il 2026-11-14, è Hotspot `9.10` e Average `9.76`.
- `.codesceneignore` esclude il blueprint congelato, gli artefatti generati e il tooling agentico `.kilo/`.
- Il gate MCP non gira in CI perché richiede la sessione OAuth locale. Il ratchet può girare in CI solo con un `CODESCENE_API_TOKEN` esplicito e un job dedicato.

## Conseguenze

- Un commit o un push che degrada il Code Health dei file toccati viene bloccato localmente.
- Sviluppo e push richiedono una sessione CodeScene autenticata; se manca, il gate fallisce chiuso e lo dichiara.
- Il progetto Cloud resta la fonte per hotspot e punteggi aggregati; il gate locale non usa la scansione Cloud, che è in ritardo rispetto ai commit.
- La soglia di progetto non può essere abbassata per far passare un diff: si rifattorizza.
- I token non vengono mai committati. Il project id non è un segreto.

## Alternative considerate

- **Solo CodeScene Cloud**: la scansione è in ritardo e non blocca il commit.
- **Solo ratchet REST**: misura il progetto, non il singolo diff.
- **Codacy o SonarQube**: aggiungono un secondo modello di qualità senza il feedback locale già disponibile.
- **Nessun gate CodeScene**: lascia scoperte complessità e hotspot che lint e coverage non vedono.
