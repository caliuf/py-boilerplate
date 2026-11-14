"""Il caso d'uso `sayHello` orchestra dominio e porta di logging."""

from tests.support.logging import MemoryLogger

from py_boilerplate.contracts.hello_world import HelloWorldInput, HelloWorldOutput
from py_boilerplate.greetings.application.say_hello import SayHelloDeps, say_hello


def test_say_hello_returns_output_and_logs() -> None:
    logger = MemoryLogger()

    output = say_hello(SayHelloDeps(logger=logger), HelloWorldInput(name="Ada"))

    assert output == HelloWorldOutput(message="Hello, Ada!")
    assert logger.entries[0].level == "info"
    assert logger.entries[0].event == "saying hello"
    assert logger.entries[0].context == {"name": "Ada"}
