"""Dipendenze esplicite del composition root HTTP."""

from dataclasses import dataclass

from py_boilerplate.contracts.logging import Logger


@dataclass(frozen=True, slots=True)
class ApiDeps:
    """Adapter già costruiti e iniettati nelle route."""

    logger: Logger
