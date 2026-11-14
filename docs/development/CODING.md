# Coding

## Layout

Il package importabile sta in `src/py_boilerplate/`. I test stanno in `tests/` e non sono importabili da `src/`. Non usare flat layout, `sys.path` hack o import relativi alla working directory.

Un modulo nuovo deve avere un confine chiaro:

- dominio puro in `greetings/domain/`;
- orchestrazione in `greetings/application/`;
- porte in `greetings/ports/`;
- adapter in `adapters/`;
- superfici e composition root in `entrypoints/`.

## Dipendenze

La direzione è `entrypoints → adapters → application → ports → domain`, con `contracts` come foglia. Le regole sono in [`docs/architecture/BOUNDARIES.md`](../architecture/BOUNDARIES.md) e verificate da `just arch`.

- Nessun import di FastAPI, MCP, argparse o structlog da dominio e application.
- Nessun import incrociato tra CLI, API e MCP.
- Nessun service locator, container DI o registry magico.
- Nessuno stato globale mutabile.

## Typing

mypy è l'autorità. Gira in strict su `src`, `tests` e `tools`.

- Annota i confini pubblici e i ritorni; lascia che mypy inferisca i locali ovvi.
- Preferisci `Protocol` per le porte e i tipi strutturali.
- Usa `type` alias per i tipi composti ricorrenti.
- Non introdurre `Any`, `cast()` o `# type: ignore` senza necessità e senza un motivo scritto nello stesso punto.
- Non usare `cast()` per convertire dati esterni: non è validazione.
- Non usare `assert` per validare input di produzione.

## Validazione

I dati esterni si validano a runtime ai confini:

- CLI: `HelloWorldInput.model_validate`.
- API: stesso modello nella route.
- MCP: schema generato dalla firma del tool, con l'alias condiviso.

I modelli esterni usano `extra="forbid"` e `frozen=True`. I limiti vivono in un solo alias; non duplicare `min_length`, `max_length` o il trim in più punti.

I dati interni che non attraversano un confine possono usare dataclass standard. Non usare Pydantic ovunque per abitudine.

## Errori

- Usa `ErrorCode` e `AppError` per gli errori applicativi.
- Solleva `ApplicationError` nell'application layer.
- Mappa l'errore al confine: exit code nella CLI, Problem Details nell'API, tool error nel MCP.
- Non importare `HTTPException`, `ToolError` o `SystemExit` nel dominio o nell'application layer.
- Non esporre stack trace, path interni o dettagli di implementazione al client.

## Logging

- Usa la porta `Logger`, non `print()` e non `logging` direttamente nei moduli di dominio o application.
- L'evento è una stringa stabile, in minuscolo e greppabile.
- Il contesto è strutturato e non contiene segreti o dati personali.
- La configurazione di structlog avviene una sola volta nel composition root.
- In JSON mode i log vanno su stderr; stdout resta riservato ai dati della CLI.
- Rispetta `NO_COLOR` e non emettere ANSI su stream non-TTY.

## Configurazione

- Leggi l'environment solo nei composition root, con `RuntimeSettings` o `ApiSettings`.
- Valida i valori all'avvio; non ignorare un valore invalido.
- Passa le dipendenze già costruite ai moduli interni.
- Non leggere file `.env` dentro le librerie.

## Async e I/O

- Il caso d'uso attuale è sincrono e veloce.
- La route FastAPI è `def`, quindi non blocca l'event loop.
- Il server MCP usa il trasporto stdio dell'SDK, che gestisce l'event loop.
- Non creare task `asyncio` fire-and-forget. Se nasce un job asincrono, servono ownership, timeout, cancellazione e test dedicati.

## Stile

- Ruff gestisce formattazione, import e lint. Non aggiungere Black, isort o Flake8.
- Line length 100 per il codice; la prosa non ha hard wrap.
- Identificatori e nomi di API in inglese; docstring e documentazione in italiano.
- Le docstring spiegano responsabilità e invarianti, non ripetono il nome della funzione.
- I commenti spiegano il perché, non il cosa. Non lasciare codice commentato.
- Non aggiungere commenti di rumore o banner decorativi.

## Dipendenze e package

- Aggiungi una dipendenza solo con una necessità misurata e, se significativa, una ADR.
- Non usare una dipendenza transitiva direttamente: deptry lo rileva.
- Non aggiungere un secondo type checker o un secondo linter equivalente.
- Gli entry point sono dichiarati in `[project.scripts]`; il wheel è verificato da `just package-check`.
- Non modificare `uv.lock` a mano.

## Checklist prima del commit

- Il codice è tipizzato e validato ai confini.
- I test coprono il comportamento nuovo e i casi limite.
- Non ci sono `print()`, debug, ignore o suppression senza motivo.
- Non ci sono import vietati o cicli.
- La documentazione e le decisioni sono aggiornate.
- `just precommit` è verde.
