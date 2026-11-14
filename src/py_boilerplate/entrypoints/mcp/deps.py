"""Dipendenze esplicite del composition root MCP."""

from dataclasses import dataclass

from py_boilerplate.contracts.logging import Logger


@dataclass(frozen=True, slots=True)
class McpDeps:
    """Adapter già costruiti e iniettati nei tool."""

    logger: Logger
