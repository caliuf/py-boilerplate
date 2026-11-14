# Adapters

Gli adapter implementano le porte del progetto verso tecnologie esterne. Oggi c'è un solo adapter: il logging basato su structlog.

## Logging

`adapters/logging.py` espone `create_logger` e `StructlogLogger`.

- `create_logger` configura structlog e la standard library una sola volta per processo.
- JSON in produzione e CI; console renderer in sviluppo.
- I colori ANSI sono disabilitati su stream non-TTY e con `NO_COLOR`.
- Il livello è validato dal composition root.
- Il logger scrive su stderr; stdout resta riservato ai dati della CLI.

## Regole

- Un adapter implementa una porta, non introduce logica di dominio.
- La configurazione globale avviene solo nel composition root, mai all'import.
- Nessun adapter importa un entrypoint.
- Nessun adapter contiene segreti o legge file `.env`.
- I test dell'adapter verificano formato, livelli, colori e rispetto di `NO_COLOR`.

## Test

I test stanno in `tests/unit/adapters/test_logging.py` e usano stream in-memory e uno stream TTY simulato.
