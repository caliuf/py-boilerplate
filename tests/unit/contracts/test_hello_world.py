"""Contratto del DTO `hello-world`: validazione runtime, non solo typing."""

import pytest
from pydantic import ValidationError

from py_boilerplate.contracts.hello_world import (
    HelloWorldInput,
    HelloWorldOutput,
    format_validation_error,
)


def test_default_name_is_world() -> None:
    assert HelloWorldInput().name == "world"


def test_name_is_trimmed() -> None:
    assert HelloWorldInput(name="  Ada  ").name == "Ada"


@pytest.mark.parametrize("name", ["", "   ", "x" * 101])
def test_invalid_name_is_rejected(name: str) -> None:
    with pytest.raises(ValidationError):
        HelloWorldInput(name=name)


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        HelloWorldInput.model_validate({"name": "Ada", "extra": "nope"})


def test_output_is_frozen() -> None:
    output = HelloWorldOutput(message="Hello, Ada!")
    with pytest.raises(ValidationError):
        output.__setattr__("message", "changed")


def test_validation_error_is_formatted_with_field() -> None:
    with pytest.raises(ValidationError) as captured:
        HelloWorldInput(name="")

    message = format_validation_error(captured.value)

    assert message.startswith("name: ")
    assert "at least 1 character" in message
