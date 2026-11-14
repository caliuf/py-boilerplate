# Greetings

Il bounded context `greetings` contiene il caso d'uso dimostrativo del boilerplate.

## Struttura

| Directory | Contenuto |
|---|---|
| `domain/` | `Greeting` come dataclass frozen e `greet`, funzione pura |
| `application/` | `say_hello`, con `SayHelloDeps` e la porta `Logger` |
| `ports/` | `Logger`, ri-esportata per il contesto |

## API pubblica

L'entrypoint importa il caso d'uso in modo esplicito:

```python
from py_boilerplate.greetings.application.say_hello import SayHelloDeps, say_hello
```

Non ci sono re-export nell'`__init__.py`: gli import restano espliciti e i confini sono più facili da verificare.

## Regole

- Il dominio non importa contratti, porte, adapter, framework o logging.
- L'application layer conosce dominio, porte e contratti; non conosce FastAPI, MCP, argparse o structlog.
- Il caso d'uso riceve un input già validato e restituisce un output tipizzato.
- Il logging avviene tramite la porta, non tramite `print()` o `logging`.
- Non aggiungere dipendenze dal framework a questo package.

## Test

- `tests/unit/greetings/` copre dominio e application layer.
- Il contract test cross-surface verifica che CLI, API e MCP usino questo stesso caso d'uso.
