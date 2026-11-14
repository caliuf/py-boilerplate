"""Factory dell'applicazione ASGI, testabile senza avviare un server."""

from fastapi import FastAPI

from py_boilerplate import __version__
from py_boilerplate.entrypoints.api.deps import ApiDeps
from py_boilerplate.entrypoints.api.routes.hello_world import create_hello_world_router


def create_app(deps: ApiDeps) -> FastAPI:
    """Costruisce l'app FastAPI con dipendenze esplicite, senza stato globale."""

    app = FastAPI(title="py-boilerplate", version=__version__)
    app.include_router(create_hello_world_router(deps))
    return app
