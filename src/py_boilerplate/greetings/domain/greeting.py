"""Value object e funzioni pure del dominio `greetings`."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Greeting:
    """Saluto immutabile prodotto dal dominio."""

    message: str


def greet(name: str) -> Greeting:
    """Costruisce il saluto per un nome già validato al confine.

    La funzione è pura: nessun I/O, nessun logging, nessuna dipendenza esterna.
    """

    return Greeting(message=f"Hello, {name}!")
