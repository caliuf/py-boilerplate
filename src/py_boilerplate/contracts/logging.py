"""Porta di logging condivisa.

I tipi `Logger` e `LogLevel` fanno parte del linguaggio condiviso del progetto:
adapter concreti (structlog, in-memory nei test) implementano il `Protocol`,
mentre dominio e application conoscono solo questa porta.
"""

from typing import Literal, Protocol, runtime_checkable

type LogLevel = Literal["debug", "info", "warning", "error", "critical"]

LOG_LEVELS: tuple[LogLevel, ...] = ("debug", "info", "warning", "error", "critical")


@runtime_checkable
class Logger(Protocol):
    """Porta di logging strutturato.

    L'evento è una stringa stabile e greppabile; il contesto viaggia come
    keyword argument e non deve contenere segreti o dati personali.
    """

    def debug(self, event: str, /, **context: object) -> None: ...

    def info(self, event: str, /, **context: object) -> None: ...

    def warning(self, event: str, /, **context: object) -> None: ...

    def error(self, event: str, /, **context: object) -> None: ...

    def critical(self, event: str, /, **context: object) -> None: ...
