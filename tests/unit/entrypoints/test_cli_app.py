"""Composition root CLI: parsing, dispatch, stream e exit code."""

import io
import json
from collections.abc import Mapping

import pytest
from tests.support.logging import MemoryLogger

from py_boilerplate.contracts.logging import Logger, LogLevel
from py_boilerplate.entrypoints.cli.app import run


class LoggerCapture:
    """LoggerFactory che registra i logger creati e le loro entry."""

    def __init__(self) -> None:
        self.loggers: list[MemoryLogger] = []

    def __call__(self, *, level: LogLevel, json_output: bool) -> Logger:
        logger = MemoryLogger()
        self.loggers.append(logger)
        return logger


def _run(
    argv: list[str],
    *,
    env: Mapping[str, str] | None = None,
    is_tty: bool = False,
) -> tuple[int, str, str, LoggerCapture]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    capture = LoggerCapture()
    code = run(
        argv,
        stdout=stdout,
        stderr=stderr,
        env={} if env is None else env,
        is_tty=is_tty,
        logger_factory=capture,
    )
    return code, stdout.getvalue(), stderr.getvalue(), capture


def test_no_arguments_prints_help_and_returns_2() -> None:
    code, stdout, stderr, capture = _run([])

    assert code == 2
    assert "usage:" in stdout
    assert stderr == ""
    assert capture.loggers == []


def test_help_returns_0(capsys: pytest.CaptureFixture[str]) -> None:
    code, _stdout, stderr, _capture = _run(["--help"])

    captured = capsys.readouterr()
    assert code == 0
    assert "usage:" in captured.out
    assert stderr == ""


def test_unknown_command_returns_4_as_json() -> None:
    code, stdout, stderr, _capture = _run(["nope", "--json"])

    assert code == 4
    assert stdout == ""
    payload = json.loads(stderr)
    assert payload == {"error": "NOT_FOUND", "message": "unknown command: nope"}


def test_unknown_command_returns_4_as_text() -> None:
    code, _stdout, stderr, _capture = _run(["nope"], is_tty=True)

    assert code == 4
    assert stderr == "Error [NOT_FOUND]: unknown command: nope\n"


def test_invalid_name_returns_2_and_structured_error() -> None:
    code, stdout, stderr, _capture = _run(["hello-world", "--json", "--name", ""])

    assert code == 2
    assert stdout == ""
    payload = json.loads(stderr)
    assert payload["error"] == "VALIDATION"
    assert payload["message"].startswith("name: ")


def test_success_as_json_writes_only_data_to_stdout() -> None:
    code, stdout, stderr, capture = _run(["hello-world", "--json"])

    assert code == 0
    assert json.loads(stdout) == {"message": "Hello, world!"}
    assert stderr == ""
    assert capture.loggers[0].events() == ["saying hello"]


def test_success_as_text() -> None:
    code, stdout, stderr, _capture = _run(["hello-world"], is_tty=True)

    assert code == 0
    assert stdout == "Hello, world!\n"
    assert stderr == ""


def test_non_tty_defaults_to_json() -> None:
    code, stdout, _stderr, _capture = _run(["hello-world"], is_tty=False)

    assert code == 0
    assert json.loads(stdout) == {"message": "Hello, world!"}


def test_json_flag_before_command() -> None:
    code, stdout, _stderr, _capture = _run(["--json", "hello-world"])

    assert code == 0
    assert json.loads(stdout) == {"message": "Hello, world!"}


def test_environment_name_is_used_when_the_flag_is_absent() -> None:
    code, stdout, _stderr, _capture = _run(
        ["hello-world", "--json"], env={"HELLO_WORLD_NAME": "Ada"}
    )

    assert code == 0
    assert json.loads(stdout) == {"message": "Hello, Ada!"}


def test_flag_overrides_the_environment() -> None:
    code, stdout, _stderr, _capture = _run(
        ["hello-world", "--json", "--name", "Bob"],
        env={"HELLO_WORLD_NAME": "Ada"},
    )

    assert code == 0
    assert json.loads(stdout) == {"message": "Hello, Bob!"}


def test_empty_environment_name_is_ignored() -> None:
    code, stdout, _stderr, _capture = _run(
        ["hello-world", "--json"], env={"HELLO_WORLD_NAME": "   "}
    )

    assert code == 0
    assert json.loads(stdout) == {"message": "Hello, world!"}


def test_unknown_flag_returns_2() -> None:
    code, stdout, stderr, _capture = _run(["hello-world", "--json", "--nope"])

    assert code == 2
    assert stdout == ""
    assert json.loads(stderr)["error"] == "VALIDATION"


def test_json_without_command_returns_2() -> None:
    code, stdout, _stderr, _capture = _run(["--json"])

    assert code == 2
    assert "usage:" in stdout
