"""Composition root della CLI: parsing, dispatch e mapping degli exit code."""

import argparse
from collections.abc import Mapping, Sequence
from typing import NoReturn, TextIO

from py_boilerplate.adapters.logging import create_logger
from py_boilerplate.contracts.errors import (
    ERROR_CODE_TO_EXIT_CODE,
    AppError,
    ApplicationError,
    ErrorCode,
)
from py_boilerplate.contracts.logging import Logger
from py_boilerplate.entrypoints.cli.command import (
    Command,
    CommandContext,
    LoggerFactory,
)
from py_boilerplate.entrypoints.cli.output import (
    render_error,
    render_success,
    wants_json,
)
from py_boilerplate.entrypoints.cli.registry import COMMANDS

_ROOT_DESCRIPTION = (
    "Boilerplate Python agent-first: un caso d'uso, molte superfici. "
    "stdout porta solo dati; log e diagnosi vanno su stderr."
)
_ROOT_EPILOG = """Examples:
  py-boilerplate hello-world
  py-boilerplate hello-world --name Ada --json
"""


class CliUsageError(Exception):
    """Errore di parsing: input non valido, mappato su exit code 2."""


class CliArgumentParser(argparse.ArgumentParser):
    """Parser che non termina il processo sugli errori di input."""

    def error(self, message: str) -> NoReturn:
        raise CliUsageError(message)


def build_parser(*, commands: Sequence[Command]) -> argparse.ArgumentParser:
    """Costruisce l'albero dei subcommand dal registry."""

    parser = CliArgumentParser(
        prog="py-boilerplate",
        description=_ROOT_DESCRIPTION,
        usage="py-boilerplate <command> [options]",
        epilog=_ROOT_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="Emette JSON su stdout.")
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    for command in commands:
        subparser = subparsers.add_parser(
            command.name,
            help=command.summary,
            description=command.summary,
            usage=command.usage,
            epilog="Examples:\n" + "\n".join(f"  {example}" for example in command.examples),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        subparser.add_argument(
            "--json",
            action="store_true",
            default=argparse.SUPPRESS,
            help="Emette JSON su stdout.",
        )
        command.add_arguments(subparser)

    return parser


def run(
    argv: Sequence[str],
    *,
    stdout: TextIO,
    stderr: TextIO,
    env: Mapping[str, str],
    is_tty: bool,
    logger_factory: LoggerFactory = create_logger,
) -> int:
    """Esegue la CLI e restituisce l'exit code, senza terminare il processo."""

    commands = COMMANDS
    json_hint = wants_json(argv, is_tty=is_tty)
    json_mode = json_hint
    parser = build_parser(commands=commands)

    try:
        if not argv:
            stdout.write(parser.format_help())
            return 2

        first = argv[0]
        if not first.startswith("-") and first not in {command.name for command in commands}:
            raise ApplicationError(AppError(ErrorCode.NOT_FOUND, f"unknown command: {first}"))

        args = parser.parse_args(list(argv))
        json_mode = bool(getattr(args, "json", False)) or not is_tty
        command_name = getattr(args, "command", None)
        if not isinstance(command_name, str):
            stdout.write(parser.format_help())
            return 2

        logger: Logger = logger_factory(
            level="error" if json_mode else ("debug" if is_tty else "info"),
            json_output=json_mode,
        )
        ctx = CommandContext(
            logger=logger,
            json_mode=json_mode,
            stdout=stdout,
            stderr=stderr,
            env=env,
            is_tty=is_tty,
        )
        command = next(command for command in commands if command.name == command_name)
        output = command.run(args, ctx)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    except CliUsageError as exc:
        error = AppError(ErrorCode.VALIDATION, str(exc))
        stderr.write(render_error(error, json_mode=json_hint) + "\n")
        return ERROR_CODE_TO_EXIT_CODE[error.code]
    except ApplicationError as exc:
        stderr.write(render_error(exc.error, json_mode=json_hint) + "\n")
        return ERROR_CODE_TO_EXIT_CODE[exc.error.code]

    stdout.write(render_success(output, json_mode=json_mode) + "\n")
    return 0
