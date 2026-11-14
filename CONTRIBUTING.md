# Contributing

Grazie per contribuire a `py-boilerplate`. Il progetto è ottimizzato per un flusso agent-first: poche guide canoniche, gate deterministici e review umana sulle decisioni.

## Prima di iniziare

1. Leggi [`AGENTS.md`](AGENTS.md), [`docs/PROJECT.md`](docs/PROJECT.md) e [`docs/INDEX.md`](docs/INDEX.md).
2. Installa il toolchain con `just setup` e verifica con `just doctor`.
3. Controlla che la baseline sia verde con `just prepush`.

## Flusso di lavoro

- Apri un branch dedicato per ogni task. Non lavorare su `main`.
- Scrivi prima il test che descrive il comportamento e guardalo fallire.
- Implementa il minimo che rende il test verde, poi rifattorizza.
- Esegui `just precommit` durante il lavoro e `just prepush` prima della consegna.
- Aggiorna ADR, PDR e documentazione nello stesso commit del codice.
- Apri una PR piccola, con il report dei comandi eseguiti.

La procedura completa, inclusi fast path docs-only, Definition of Done e gestione delle PR, è in [`docs/development/WORKFLOWS.md`](docs/development/WORKFLOWS.md).

## Stile

- Python tipizzato con mypy strict; niente `Any`, `cast()` o ignore comment senza motivo.
- Validazione runtime ai confini con Pydantic; il typing non è validazione.
- Nessun `print()` in `src`; usa la porta `Logger`.
- Dominio e application layer non importano framework o adapter.
- Test comportamentali, isolati e deterministici.
- Prosa in italiano senza hard wrap; identificatori e comandi in inglese.

Le convenzioni dettagliate sono in [`docs/development/CODING.md`](docs/development/CODING.md) e [`docs/development/TESTING.md`](docs/development/TESTING.md).

## Commit

Usa un prefisso convenzionale e una lista puntata con il dettaglio:

```text
feat: aggiunge il caso d'uso hello-world alla superficie MCP

- registra il tool read-only con descrizione orientata al modello
- riusa il caso d'uso e la tassonomia errori condivisa
- aggiunge integration test in-memory e contract test cross-surface
```

Mantieni il messaggio proposto in `tmp/commit-message.md` durante il lavoro.

## Review

La review umana verifica:

- correttezza e sicurezza;
- aderenza a PDR e ADR;
- copertura dei casi limite;
- assenza di modifiche estranee;
- assenza di gate aggirati o soglie abbassate.

Non commentare formattazione o stile già gestiti dai tool.
