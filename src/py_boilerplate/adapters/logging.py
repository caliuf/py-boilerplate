"""Adapter di logging basato su structlog e sulla standard library.

La configurazione avviene una sola volta nel composition root di ogni processo.
Il dominio non conosce questo modulo: vede solo la porta `Logger`.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import TextIO

import structlog
from structlog.types import Processor

from py_boilerplate.contracts.logging import Logger, LogLevel

_LOG_LEVEL_TO_STDLIB: dict[LogLevel, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class StructlogLogger:
    """Implementazione della porta `Logger` sopra un `BoundLogger` structlog."""

    def __init__(self, logger: structlog.stdlib.BoundLogger) -> None:
        self._logger = logger

    def debug(self, event: str, /, **context: object) -> None:
        self._logger.debug(event, **context)

    def info(self, event: str, /, **context: object) -> None:
        self._logger.info(event, **context)

    def warning(self, event: str, /, **context: object) -> None:
        self._logger.warning(event, **context)

    def error(self, event: str, /, **context: object) -> None:
        self._logger.error(event, **context)

    def critical(self, event: str, /, **context: object) -> None:
        self._logger.critical(event, **context)


def create_logger(
    *,
    level: LogLevel,
    json_output: bool,
    stream: TextIO | None = None,
) -> Logger:
    """Configura structlog e restituisce la porta `Logger`.

    JSON strutturato per produzione e CI; console renderer per sviluppo.
    I colori ANSI sono disabilitati su stream non-TTY e con `NO_COLOR`.
    """

    output = stream if stream is not None else sys.stderr
    use_colors = not json_output and output.isatty() and "NO_COLOR" not in os.environ

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if json_output
        else structlog.dev.ConsoleRenderer(colors=use_colors)
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    handler = logging.StreamHandler(output)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(_LOG_LEVEL_TO_STDLIB[level])

    return StructlogLogger(structlog.stdlib.get_logger("py_boilerplate"))
