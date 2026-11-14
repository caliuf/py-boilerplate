"""Renderer CLI: JSON su stdout, errori strutturati su stderr."""

from py_boilerplate.contracts.errors import AppError, ErrorCode
from py_boilerplate.entrypoints.cli.command import CommandOutput
from py_boilerplate.entrypoints.cli.output import (
    render_error,
    render_success,
    wants_json,
)


def test_wants_json_defaults_to_json_when_not_a_tty() -> None:
    assert wants_json([], is_tty=False) is True


def test_wants_json_requires_flag_on_a_tty() -> None:
    assert wants_json([], is_tty=True) is False
    assert wants_json(["--json"], is_tty=True) is True


def test_render_success_json() -> None:
    output = CommandOutput(data={"message": "Hello!"}, human="Hello!")

    rendered = render_success(output, json_mode=True)

    assert rendered == '{\n  "message": "Hello!"\n}'


def test_render_success_human() -> None:
    output = CommandOutput(data={"message": "Hello!"}, human="Hello!")

    assert render_success(output, json_mode=False) == "Hello!"


def test_render_error_json() -> None:
    error = AppError(ErrorCode.VALIDATION, "bad input")

    rendered = render_error(error, json_mode=True)

    assert '"error": "VALIDATION"' in rendered
    assert '"message": "bad input"' in rendered


def test_render_error_human() -> None:
    error = AppError(ErrorCode.VALIDATION, "bad input")

    assert render_error(error, json_mode=False) == "Error [VALIDATION]: bad input"
