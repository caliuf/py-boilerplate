"""Registry dichiarativo dei subcommand disponibili."""

from collections.abc import Sequence

from py_boilerplate.entrypoints.cli.command import Command
from py_boilerplate.entrypoints.cli.commands.hello_world import HelloWorldCommand

COMMANDS: Sequence[Command] = (HelloWorldCommand(),)
