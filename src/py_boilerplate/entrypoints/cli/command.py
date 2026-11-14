"""Tipi condivisi dagli entrypoint CLI."""

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, TextIO

from py_boilerplate.contracts.logging import Logger, LogLevel


@dataclass(frozen=True, slots=True)
class CommandOutput:
    """Risultato di un comando: dati machine-readable e resa umana."""

    data: Mapping[str, object]
    human: str


@dataclass(frozen=True, slots=True)
class CommandContext:
    """Dipendenze esplicite passate a un comando."""

    logger: Logger
    json_mode: bool
    stdout: TextIO
    stderr: TextIO
    env: Mapping[str, str]
    is_tty: bool


class LoggerFactory(Protocol):
    """Factory iniettabile per isolare i test dal logger reale."""

    def __call__(self, *, level: LogLevel, json_output: bool) -> Logger: ...


class Command(Protocol):
    """Contratto di un subcommand: dichiarativo e testabile."""

    @property
    def name(self) -> str: ...

    @property
    def summary(self) -> str: ...

    @property
    def usage(self) -> str: ...

    @property
    def examples(self) -> tuple[str, ...]: ...

    def add_arguments(self, parser: argparse.ArgumentParser) -> None: ...

    def run(self, args: argparse.Namespace, ctx: CommandContext) -> CommandOutput: ...
