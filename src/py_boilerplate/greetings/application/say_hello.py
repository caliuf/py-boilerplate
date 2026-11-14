"""Caso d'uso `sayHello`, unico per tutte le superfici di ingresso."""

from dataclasses import dataclass

from py_boilerplate.contracts.hello_world import HelloWorldInput, HelloWorldOutput
from py_boilerplate.greetings.domain.greeting import greet
from py_boilerplate.greetings.ports.logger import Logger


@dataclass(frozen=True, slots=True)
class SayHelloDeps:
    """Dipendenze esplicite del caso d'uso (iniettate dal composition root)."""

    logger: Logger


def say_hello(deps: SayHelloDeps, input: HelloWorldInput) -> HelloWorldOutput:
    """Saluta il nome validato e registra l'evento al confine applicativo.

    L'input è già validato a runtime dal confine: il caso d'uso non usa
    annotazioni o `cast` come se fossero validazione.
    """

    greeting = greet(input.name)
    deps.logger.info("saying hello", name=input.name)
    return HelloWorldOutput(message=greeting.message)
