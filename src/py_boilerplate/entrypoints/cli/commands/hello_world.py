"""Comando `hello-world`: adapter sottile sul caso d'uso `sayHello`."""

import argparse
from dataclasses import dataclass

from pydantic import ValidationError

from py_boilerplate.contracts.errors import AppError, ApplicationError, ErrorCode
from py_boilerplate.contracts.hello_world import (
    HelloWorldInput,
    format_validation_error,
)
from py_boilerplate.entrypoints.cli.command import CommandContext, CommandOutput
from py_boilerplate.greetings.application.say_hello import SayHelloDeps, say_hello


@dataclass(frozen=True, slots=True)
class HelloWorldCommand:
    """Un modulo per subcommand; il path rispecchia il comando."""

    name: str = "hello-world"
    summary: str = "Stampa un saluto per un nome."
    usage: str = "py-boilerplate hello-world [--name <name>] [--json]"
    examples: tuple[str, ...] = (
        "py-boilerplate hello-world",
        "py-boilerplate hello-world --name Ada --json",
    )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="Nome da salutare (1-100 caratteri; default: HELLO_WORLD_NAME o 'world').",
        )

    def run(self, args: argparse.Namespace, ctx: CommandContext) -> CommandOutput:
        raw_name = getattr(args, "name", None)
        env_name = ctx.env.get("HELLO_WORLD_NAME")
        candidate: str | None
        if isinstance(raw_name, str):
            candidate = raw_name
        elif env_name is not None and env_name.strip() != "":
            candidate = env_name
        else:
            candidate = None

        payload: dict[str, str] = {} if candidate is None else {"name": candidate}
        try:
            input_ = HelloWorldInput.model_validate(payload)
        except ValidationError as exc:
            raise ApplicationError(
                AppError(ErrorCode.VALIDATION, format_validation_error(exc))
            ) from exc

        output = say_hello(SayHelloDeps(logger=ctx.logger), input_)
        return CommandOutput(data=output.model_dump(mode="json"), human=output.message)
