# Contracts

`py_boilerplate.contracts` è la foglia condivisa del progetto. Contiene:

- `HelloWorldInput` e `HelloWorldOutput`, DTO Pydantic del caso d'uso;
- `HelloWorldName`, alias `Annotated` con trim e limiti, riusato dal tool MCP;
- `format_validation_error`, formattazione stabile degli errori Pydantic;
- `ErrorCode`, `AppError`, `ApplicationError`, `ProblemInfo` e i mapping verso exit code, status HTTP e URN;
- `ProblemDetails`, payload RFC 9457;
- `Logger` e `LogLevel`, porta di logging condivisa.

## Regole

- Il package non importa altri moduli interni. Il contratto Import Linter `Contracts are a dependency leaf` lo verifica.
- I DTO esterni usano `extra="forbid"` e `frozen=True`.
- I limiti di validazione vivono in un solo punto e non vengono duplicati nelle superfici.
- I mapping degli errori devono coprire ogni `ErrorCode`; i test di completezza falliscono se manca una voce.
- Non aggiungere logica di dominio o I/O: i contratti descrivono forma e semantica, non orchestrano.

## Test

I test stanno in `tests/unit/contracts/`. Coprono default, trim, limiti, campi extra, immutabilità, formattazione degli errori e completezza dei mapping.
