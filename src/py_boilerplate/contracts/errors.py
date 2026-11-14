"""Tassonomia condivisa degli errori e mapping verso i canali.

Una sola tassonomia per CLI, API HTTP e MCP: i codici non si ridefiniscono per
superficie. I mapping sono fissati da ADR-0004 e non cambiano significato.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Literal


class ErrorCode(StrEnum):
    """Codici errore stabili, condivisi da tutte le superfici."""

    INTERNAL = "INTERNAL"
    VALIDATION = "VALIDATION"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"


type HttpErrorStatus = Literal[400, 401, 404, 409, 500]


@dataclass(frozen=True, slots=True)
class AppError:
    """Errore applicativo come valore: codice stabile e messaggio sicuro."""

    code: ErrorCode
    message: str


class ApplicationError(Exception):
    """Eccezione tipizzata per gli errori applicativi attesi.

    Il dominio e l'application layer non conoscono le eccezioni del framework:
    sollevano questa eccezione e ogni confine la mappa sul proprio canale.
    """

    def __init__(self, error: AppError) -> None:
        super().__init__(error.message)
        self.error = error


# Exit code CLI fissati da ADR-0004:
# 0 ok · 1 internal · 2 invalid input · 3 auth · 4 not found · 5 conflict
ERROR_CODE_TO_EXIT_CODE: Mapping[ErrorCode, int] = MappingProxyType(
    {
        ErrorCode.INTERNAL: 1,
        ErrorCode.VALIDATION: 2,
        ErrorCode.UNAUTHORIZED: 3,
        ErrorCode.NOT_FOUND: 4,
        ErrorCode.CONFLICT: 5,
    }
)

# Status HTTP coerenti con gli exit code della CLI.
ERROR_CODE_TO_HTTP_STATUS: Mapping[ErrorCode, HttpErrorStatus] = MappingProxyType(
    {
        ErrorCode.INTERNAL: 500,
        ErrorCode.VALIDATION: 400,
        ErrorCode.UNAUTHORIZED: 401,
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.CONFLICT: 409,
    }
)


@dataclass(frozen=True, slots=True)
class ProblemInfo:
    """Tipo URN e titolo leggibile di un Problem Details RFC 9457."""

    type: str
    title: str


ERROR_CODE_TO_PROBLEM: Mapping[ErrorCode, ProblemInfo] = MappingProxyType(
    {
        ErrorCode.INTERNAL: ProblemInfo(
            type="urn:py-boilerplate:error:internal",
            title="Internal error",
        ),
        ErrorCode.VALIDATION: ProblemInfo(
            type="urn:py-boilerplate:error:validation",
            title="Invalid input",
        ),
        ErrorCode.UNAUTHORIZED: ProblemInfo(
            type="urn:py-boilerplate:error:unauthorized",
            title="Unauthorized",
        ),
        ErrorCode.NOT_FOUND: ProblemInfo(
            type="urn:py-boilerplate:error:not-found",
            title="Not found",
        ),
        ErrorCode.CONFLICT: ProblemInfo(
            type="urn:py-boilerplate:error:conflict",
            title="Conflict",
        ),
    }
)
