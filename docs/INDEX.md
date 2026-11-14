# Indice della documentazione

Questa è la mappa della documentazione viva. L'ordine consigliato è: contratto di sviluppo, progetto, architettura, prodotto, sviluppo, memoria. Il blueprint congelato è in `docs/init/`.

## Start here

1. [`AGENTS.md`](../AGENTS.md) — contratto canonico per agenti e umani.
2. [`docs/PROJECT.md`](PROJECT.md) — obiettivi, non-obiettivi, superfici e vincoli.
3. [`docs/memory/project.md`](memory/project.md) e [`docs/memory/environment.md`](memory/environment.md) — contesto operativo stabile.

## Architettura

- [`docs/architecture/OVERVIEW.md`](architecture/OVERVIEW.md) — stile architetturale e flusso di una richiesta.
- [`docs/architecture/BOUNDARIES.md`](architecture/BOUNDARIES.md) — regole di dipendenza verificate da Import Linter.
- [`docs/architecture/adr/README.md`](architecture/adr/README.md) — registro delle decisioni architetturali.

## Prodotto

- [`docs/product/OVERVIEW.md`](product/OVERVIEW.md) — intent, utenti e comportamento osservabile.
- [`docs/product/GLOSSARY.md`](product/GLOSSARY.md) — linguaggio ubiquo.
- [`docs/product/pdr/README.md`](product/pdr/README.md) — registro delle decisioni di prodotto.

## Sviluppo

- [`docs/development/GETTING-STARTED.md`](development/GETTING-STARTED.md) — bootstrap e primo task.
- [`docs/development/ENVIRONMENT.md`](development/ENVIRONMENT.md) — Python, uv, toolchain, direnv e variabili.
- [`docs/development/CODING.md`](development/CODING.md) — convenzioni di codice, typing, validazione e logging.
- [`docs/development/TESTING.md`](development/TESTING.md) — piramide dei test, coverage e contratti.
- [`docs/development/WORKFLOWS.md`](development/WORKFLOWS.md) — ciclo di lavoro, gate, PR e Definition of Done.
- [`docs/development/AGENT-AUTOMATION.md`](development/AGENT-AUTOMATION.md) — briefing, memoria e automazioni per agenti.
- [`docs/development/GITHUB-CLI.md`](development/GITHUB-CLI.md) — ruleset, check e comandi `gh` di sola lettura.
- [`docs/development/SECURITY.md`](development/SECURITY.md) — modello di sicurezza e supply chain.
- [`docs/development/NEW-PROJECT.md`](development/NEW-PROJECT.md) — checklist di adozione del boilerplate.

## Memoria operativa

- [`docs/memory/README.md`](memory/README.md) — regole della memory bank.
- [`docs/memory/project.md`](memory/project.md) — fatti stabili, obiettivi e stato sintetico.
- [`docs/memory/environment.md`](memory/environment.md) — tool, versioni, setup e limiti dell'ambiente.
- [`docs/memory/corrections.md`](memory/corrections.md) — correzioni e vincoli scoperti durante il lavoro.
- [`docs/memory/sessions/README.md`](memory/sessions/README.md) — come scrivere un digest di sessione.

## Blueprint congelato

- [`docs/init/Vademecum Python.md`](init/Vademecum%20Python.md) — principi e raccomandazioni Python applicati al progetto.

Il contenuto di `docs/init/` non si modifica durante lo sviluppo ordinario. Un cambiamento al blueprint richiede una decisione esplicita e un commit dedicato, separato dal codice.

## Regole di manutenzione

- Ogni nuova decisione architetturale produce una ADR; ogni nuova regola di prodotto produce una PDR.
- Gli indici ADR e PDR devono elencare tutti i record delle rispettive directory.
- La mappa delle superfici in `docs/PROJECT.md` va aggiornata quando nasce un comando CLI, una route o un tool MCP.
- I documenti non duplicano `AGENTS.md` o il Vademecum: rimandano alla fonte canonica.
- La prosa non usa hard wrap: un paragrafo per riga, così è leggibile e editabile da umani e agenti.
