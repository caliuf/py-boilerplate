"""Contratto CLI agent-first sui processi reali.

Verifica help, JSON, exit code, separazione degli stream e comportamento
non-TTY per ogni comando registrato.
"""

import json

import pytest
from tests.support.process import run_cli

from py_boilerplate.entrypoints.cli.registry import COMMANDS

COMMAND_NAMES = [command.name for command in COMMANDS]


@pytest.mark.parametrize("command_name", COMMAND_NAMES)
def test_command_help_is_complete(command_name: str) -> None:
    result = run_cli([command_name, "--help"])

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "Examples:" in result.stdout


def test_root_help_is_complete() -> None:
    result = run_cli(["--help"])

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "hello-world" in result.stdout


@pytest.mark.parametrize("command_name", COMMAND_NAMES)
def test_non_tty_output_defaults_to_json(command_name: str) -> None:
    result = run_cli([command_name])

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert "message" in payload


@pytest.mark.parametrize("command_name", COMMAND_NAMES)
def test_json_flag_keeps_stdout_as_data(command_name: str) -> None:
    result = run_cli([command_name, "--json"])

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {"message": "Hello, world!"}


def test_invalid_input_returns_exit_2_and_structured_error() -> None:
    result = run_cli(["hello-world", "--json", "--name", ""])

    assert result.returncode == 2
    assert result.stdout == ""
    payload = json.loads(result.stderr)
    assert payload["error"] == "VALIDATION"


def test_unknown_command_returns_exit_4() -> None:
    result = run_cli(["missing", "--json"])

    assert result.returncode == 4
    assert json.loads(result.stderr)["error"] == "NOT_FOUND"


def test_environment_default_is_used() -> None:
    from tests.support.process import clean_env

    result = run_cli(
        ["hello-world", "--json"],
        env=clean_env({"HELLO_WORLD_NAME": "Ada"}),
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {"message": "Hello, Ada!"}


def test_no_command_returns_exit_2() -> None:
    result = run_cli([])

    assert result.returncode == 2
    assert "usage:" in result.stdout
