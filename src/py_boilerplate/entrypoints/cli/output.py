"""Renderer dell'output CLI: stdout dati, stderr diagnostica, exit code stabili."""

import json
from collections.abc import Sequence

from py_boilerplate.contracts.errors import AppError
from py_boilerplate.entrypoints.cli.command import CommandOutput


def wants_json(argv: Sequence[str], *, is_tty: bool) -> bool:
    """JSON esplicito con `--json`, oppure default in contesto non-TTY."""

    return not is_tty or "--json" in argv


def render_success(output: CommandOutput, *, json_mode: bool) -> str:
    """Rende un successo sul canale stdout."""

    if json_mode:
        return json.dumps(output.data, indent=2, ensure_ascii=False)
    return output.human


def render_error(error: AppError, *, json_mode: bool) -> str:
    """Rende un errore sul canale stderr con codice stabile."""

    if json_mode:
        return json.dumps(
            {"error": error.code.value, "message": error.message},
            indent=2,
            ensure_ascii=False,
        )
    return f"Error [{error.code.value}]: {error.message}"
