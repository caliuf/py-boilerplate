"""Logger in-memory: fake della porta `Logger` per test deterministici."""

from collections.abc import Mapping
from dataclasses import dataclass

from py_boilerplate.contracts.logging import LogLevel


@dataclass(frozen=True, slots=True)
class LogEntry:
    """Una riga di log catturata, con contesto strutturato."""

    level: LogLevel
    event: str
    context: Mapping[str, object]


class MemoryLogger:
    """Implementazione della porta `Logger` che accumula le entry in memoria."""

    def __init__(self) -> None:
        self.entries: list[LogEntry] = []

    def _record(self, level: LogLevel, event: str, context: Mapping[str, object]) -> None:
        self.entries.append(LogEntry(level=level, event=event, context=dict(context)))

    def debug(self, event: str, /, **context: object) -> None:
        self._record("debug", event, context)

    def info(self, event: str, /, **context: object) -> None:
        self._record("info", event, context)

    def warning(self, event: str, /, **context: object) -> None:
        self._record("warning", event, context)

    def error(self, event: str, /, **context: object) -> None:
        self._record("error", event, context)

    def critical(self, event: str, /, **context: object) -> None:
        self._record("critical", event, context)

    def events(self) -> list[str]:
        """Eventi registrati, nell'ordine di emissione."""

        return [entry.event for entry in self.entries]
