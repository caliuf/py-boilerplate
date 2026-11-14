# Glossario

Il glossario fissa il linguaggio ubiquo. Se un termine cambia significato, aggiorna questo file e la PDR o ADR pertinente.

## Termini di prodotto

- **Caso d'uso**: comportamento osservabile che il prodotto offre, indipendente dalla superficie. Oggi l'unico caso d'uso è `sayHello`, esposto come `hello-world`.
- **Superficie**: canale di ingresso a un caso d'uso. Oggi CLI, API HTTP e MCP.
- **Hello world**: nome del caso d'uso dimostrativo e del comando CLI. Non è un framework né un modello di dominio.
- **Validazione**: verifica runtime di un dato esterno. Non è typing statico e non è un `cast`.

## Termini architetturali

- **Bounded context**: area con un linguaggio e un modello propri. Oggi `greetings`.
- **Domain**: funzioni pure e value object del bounded context, senza I/O e senza framework.
- **Application layer**: orchestrazione dei casi d'uso attraverso dominio e porte.
- **Port**: `Protocol` che descrive una dipendenza esterna dal punto di vista dell'applicazione.
- **Adapter**: implementazione concreta di una porta o di una superficie di ingresso.
- **Entrypoint**: composition root e adapter driving di una superficie.
- **Composition root**: punto in cui si costruiscono configurazione, logger, adapter e caso d'uso.
- **Contract**: tipo, schema o regola condivisa tra superfici. Nel codice vive in `contracts/`.
- **Problem Details**: payload RFC 9457 usato dalla superficie HTTP per gli errori.

## Termini di processo

- **3G**: modello Guide, Gate, Guard del Vademecum.
- **Guida**: documento canonico che orienta una decisione, per esempio `AGENTS.md` o una ADR.
- **Gate**: controllo deterministico che blocca il merge se fallisce.
- **Guard**: procedura report-only che crea issue, non codice.
- **ADR**: Architectural Decision Record, decisione architetturale duratura.
- **PDR**: Product Decision Record, decisione di prodotto.
- **Docs-only**: diff che tocca soltanto documentazione e file non eseguibili; usa un fast path di gate ridotto.
- **Coverage ratchet**: soglia di coverage che può solo salire.
- **Memory bank**: contesto operativo versionato in `docs/memory/`, complementare alla memoria nativa dell'agente.
- **Floor**: valore minimo committato per un ambiente o una soglia, per esempio `.env.default` o `coverage-thresholds.json`.
- **Recipe**: comando pubblico di `just`, unica interfaccia operativa del repository.

## Termini Python

- **src layout**: layout in cui il package importabile sta in `src/` e i test sono fuori.
- **Wheel**: artefatto di distribuzione Python installabile con `uv pip install`.
- **Entry point**: console script dichiarato in `[project.scripts]`.
- **Lockfile**: `uv.lock`, risoluzione esatta e riproducibile delle dipendenze.
- **Type checker autorevole**: mypy in modalità strict; gli altri non sono gate equivalenti.
- **Import side effect**: effetto collaterale eseguito all'import di un modulo; vietato.
