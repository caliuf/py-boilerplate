"""Bootstrap della superficie HTTP (composition root, escluso da coverage)."""

import uvicorn
from fastapi import FastAPI

from py_boilerplate.adapters.logging import create_logger
from py_boilerplate.entrypoints.api.app import create_app
from py_boilerplate.entrypoints.api.deps import ApiDeps
from py_boilerplate.entrypoints.settings import ApiSettings


def build_app() -> FastAPI:
    """Factory usata da `just dev` con `uvicorn --reload --factory`."""

    settings = ApiSettings()
    logger = create_logger(level=settings.log_level, json_output=settings.json_logs)
    return create_app(ApiDeps(logger=logger))


def main() -> None:
    """Entry point del console script `py-boilerplate-api`."""

    settings = ApiSettings()
    app = build_app()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    main()
