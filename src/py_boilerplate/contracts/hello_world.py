"""DTO e schemi di validazione del caso d'uso `hello-world`.

Tipi e schemi runtime derivano da una sola definizione: il modello Pydantic è
la fonte canonica per CLI, API, MCP e client.
"""

from collections.abc import Sequence
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, ValidationError

# Il nome è una stringa con trim applicato, non vuota, lunga al massimo 100 caratteri.
# L'alias è riusato dalle firme dei tool MCP, così i vincoli non vengono duplicati.
type HelloWorldName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]


class HelloWorldInput(BaseModel):
    """Input validato del caso d'uso `sayHello`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: HelloWorldName = "world"


class HelloWorldOutput(BaseModel):
    """Output del caso d'uso `sayHello`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    message: str


def format_validation_error(error: ValidationError) -> str:
    """Rende un errore Pydantic una stringa stabile per ogni superficie.

    Il formato è `campo: messaggio`, con i campi uniti da `; `: è lo stesso
    testo che finisce su stderr nella CLI, nel `detail` del Problem Details e
    nel tool error MCP.
    """

    parts: list[str] = []
    for issue in error.errors():
        location: Sequence[object] = issue["loc"]
        field = ".".join(str(part) for part in location) if location else "input"
        parts.append(f"{field}: {issue['msg']}")
    return "; ".join(parts)
