# Sicurezza dello sviluppo

La security policy pubblica è in [`SECURITY.md`](../../SECURITY.md). Questo documento descrive il modello di minaccia e le pratiche operative del repository.

## Modello di minaccia

Le superfici ricevono input non fidati:

- argomenti CLI, inclusi flag sconosciuti e valori vuoti o lunghi;
- query string HTTP;
- argomenti di un tool MCP.

I rischi principali sono:

- injection o interpretazione errata dell'input;
- esposizione di segreti o dati personali nei log e negli errori;
- dipendenze vulnerabili o non dichiarate, Python e web;
- XSS o injection nella UI attraverso risposte API non validate;
- supply chain del wheel e degli entry point;
- workflow GitHub con permission eccessive o action non pinnate;
- uso improprio di MCP con tool troppo potenti o descrizioni fuorvianti.

## Contromisure

- Validazione Pydantic ai confini, con limiti espliciti e `extra="forbid"`.
- Errori sicuri: nessuno stack trace o dettaglio interno al client.
- Log strutturato senza segreti e senza PII.
- Tool MCP read-only, idempotente e con descrizione accurata.
- API in ascolto su `127.0.0.1` per default.
- Gitleaks sullo staged diff e sulla storia.
- Bandit, pip-audit, npm audit, CodeQL e dependency review.
- Validazione Zod delle risposte API nella UI.
- Action pinnate a SHA completi e permission minime.
- Lockfile versionato e `uv sync --locked` in CI.
- CODEOWNERS sui file che definiscono i gate.

## API HTTP

L'API è pensata per sviluppo locale e integrazione interna. Non espone autenticazione, TLS, rate limiting o CORS permissivo. Non pubblicarla su Internet senza una decisione di prodotto e una ADR che aggiungano:

- autenticazione e autorizzazione;
- TLS e reverse proxy;
- rate limiting;
- logging di audit;
- gestione dei segreti;
- test di sicurezza dedicati.

## UI web

- La UI non importa codice Python e non duplica il dominio.
- Le risposte API sono validate con Zod; non usare `as` o `cast` per fidarsi del payload.
- Non usare `dangerouslySetInnerHTML` o HTML non sanificato.
- La UI non gestisce segreti: nessun token nel bundle.
- In produzione servila dallo stesso origin dell'API o dietro un reverse proxy che espone `/api`.
- Playwright e Vite sono tooling di sviluppo; il bundle statico non contiene Node.

## MCP

Il server usa stdio e non apre una porta di rete. I tool sono deliberatamente pochi e read-only. Le descrizioni sono istruzioni per il modello: devono essere accurate, non devono contenere segreti e non devono promettere capacità inesistenti.

Non aggiungere un tool che esegue comandi, legge file arbitrari o chiama servizi esterni senza una PDR, una ADR, validazione rigorosa e test di sicurezza.

## CodeScene

- Il project id `87780` non è un segreto e vive in `.kilo/kilo.jsonc`.
- La sessione OAuth dell'MCP vive fuori dal repository; non committare `~/.config/codehealth-mcp/`.
- Il ratchet usa `CODESCENE_API_TOKEN` o `~/.codescene/token`; non committare nessuno dei due.
- `.codesceneignore` esclude blueprint, artefatti e `.kilo/`; non allargarlo per far passare un file degradato.

## Segreti

- Non committare `.env`, `.envrc.local` o credenziali.
- Usa variabili locali e GitHub Secrets.
- Non stampare token nei log o nei report.
- Se un segreto viene committato, revocalo subito, ruota la credenziale e ripulisci la storia con una procedura concordata. Non limitarti a cancellare il file.

## Suppression

`# nosec`, `# noqa`, `# type: ignore` e `# pragma: no cover` richiedono:

- scope ristretto alla riga o al blocco;
- motivo scritto;
- codice errore quando applicabile;
- review del code owner per i file critici.

Non estendere ignore-list o esclusioni per far passare un gate. Se un alert è un falso positivo, documenta la motivazione e, quando possibile, apri una issue di follow-up.

## Dipendenze

- Aggiungi dipendenze Python con `uv add` o `uv add --dev`.
- Aggiungi dipendenze web con `npm install --workspace @py-boilerplate/web <package>`; non modificare `package-lock.json` a mano.
- `npm audit --omit=dev --audit-level=high` fa parte di `just security`.
- Verifica la versione installata, non la memoria del modello.
- Una dipendenza significativa richiede una ADR.
- Non usare dipendenze transitive direttamente.
- Non aggiornare major in batch automatici.
- Controlla licenza, provenienza, wheel e vulnerabilità prima di accettare un aggiornamento.

## CI e GitHub

- Permission di default `contents: read`.
- Permission elevate solo sul job che ne ha bisogno.
- Nessun `pull_request_target` senza review di sicurezza.
- Nessun segreto esposto a workflow su fork o input non fidati.
- CodeQL e full-history secrets scan nella slow lane settimanale.
- Dependency review sulle PR pubbliche.
- Secret scanning, push protection e private vulnerability reporting sono abilitati sul repository; verifica lo stato con l'API se necessario.

## Segnalazione

Per una vulnerabilità non aprire una issue pubblica: usa il private vulnerability reporting del repository. Vedi [`SECURITY.md`](../../SECURITY.md).
