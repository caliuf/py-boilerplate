"""Contratti condivisi: DTO, schemi di validazione e tassonomia degli errori.

Questo package è una foglia del grafo delle dipendenze: non importa altri moduli
interni del progetto (gate Import Linter `contracts-is-a-leaf`).
"""

from py_boilerplate.contracts.errors import (
    ERROR_CODE_TO_EXIT_CODE,
    ERROR_CODE_TO_HTTP_STATUS,
    ERROR_CODE_TO_PROBLEM,
    AppError,
    ApplicationError,
    ErrorCode,
    HttpErrorStatus,
    ProblemInfo,
)
from py_boilerplate.contracts.hello_world import (
    HelloWorldInput,
    HelloWorldName,
    HelloWorldOutput,
    format_validation_error,
)
from py_boilerplate.contracts.logging import LOG_LEVELS, Logger, LogLevel
from py_boilerplate.contracts.problem_details import ProblemDetails

__all__ = [
    "ERROR_CODE_TO_EXIT_CODE",
    "ERROR_CODE_TO_HTTP_STATUS",
    "ERROR_CODE_TO_PROBLEM",
    "LOG_LEVELS",
    "AppError",
    "ApplicationError",
    "ErrorCode",
    "HelloWorldInput",
    "HelloWorldName",
    "HelloWorldOutput",
    "HttpErrorStatus",
    "LogLevel",
    "Logger",
    "ProblemDetails",
    "ProblemInfo",
    "format_validation_error",
]
