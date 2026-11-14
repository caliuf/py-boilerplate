"""Il dominio `greetings` è puro, immutabile e indipendente dai framework."""

from dataclasses import FrozenInstanceError

import pytest

from py_boilerplate.greetings.domain.greeting import Greeting, greet


def test_greet_builds_a_greeting() -> None:
    assert greet("Ada") == Greeting(message="Hello, Ada!")


def test_greeting_is_frozen() -> None:
    greeting = greet("Ada")
    with pytest.raises(FrozenInstanceError):
        greeting.__setattr__("message", "changed")
