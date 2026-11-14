# API

La superficie HTTP è una factory FastAPI testabile senza server. La route valida `HelloWorldInput`, invoca `say_hello` e restituisce JSON oppure `application/problem+json` con `ProblemDetails`. Non usa stato globale e non importa gli altri entrypoint.

La documentazione completa è in [`docs/PROJECT.md`](../../../../docs/PROJECT.md) e [`docs/architecture/OVERVIEW.md`](../../../../docs/architecture/OVERVIEW.md).
