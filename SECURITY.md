# Security Policy

## Versioni supportate

Il progetto supporta Python 3.14. La versione pinnata in `.python-version` è quella usata da sviluppo e CI principale. Le versioni fuori dal range dichiarato in `pyproject.toml` non ricevono fix di sicurezza.

## Segnalare una vulnerabilità

Non aprire una issue pubblica per una vulnerabilità. Usa il private vulnerability reporting del repository GitHub: **Security → Report a vulnerability**. Se il canale non è disponibile, contatta il maintainer indicato in `CODEOWNERS`.

Includi:

- versione o commit interessato;
- superficie coinvolta (CLI, API, MCP, packaging o dipendenze);
- passi di riproduzione;
- impatto stimato;
- eventuale proof of concept, senza dati reali o segreti.

## Ambito

Sono in ambito:

- esecuzione di codice o injection attraverso input CLI, API o MCP;
- esposizione di segreti, dati personali o stack trace;
- vulnerabilità sfruttabili nelle dipendenze runtime Python o web;
- rottura dei confini architetturali con impatto di sicurezza;
- supply chain del wheel e degli entry point.

Non sono in ambito:

- attacchi che richiedono accesso fisico alla macchina;
- denial of service su un server di sviluppo locale;
- configurazioni deliberatamente insicure documentate come tali.

## Pratiche del repository

- Nessun segreto nei file versionati. `.env` e `.envrc.local` sono gitignored.
- Gitleaks scansiona lo staged diff in pre-commit e la storia in CI.
- Bandit, pip-audit e `npm audit --omit=dev --audit-level=high` girano nel gate di sicurezza.
- La UI valida le risposte API con Zod e non importa codice Python.
- CodeQL e il full-history secrets scan girano nella slow lane settimanale.
- Le GitHub Actions sono pinnate a commit SHA completi e hanno permission minime.
- Gli aggiornamenti delle dipendenze passano da PR Dependabot, non da modifiche dirette a `main`.
- Le suppression di sicurezza (`# nosec`) richiedono motivo e scope ristretto.
- I token CodeScene e le configurazioni OAuth restano fuori dal repository.
- L'API ascolta su `127.0.0.1` per default e non espone stack trace ai client.

## Divulgazione

Il maintainer conferma la ricezione, valuta l'impatto e coordina il fix e la disclosure. Non pubblicare dettagli prima dell'accordo.
