"""Tool MCP `hello_world`: adapter sottile sul caso d'uso `sayHello`."""

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from py_boilerplate.contracts.hello_world import (
    HelloWorldInput,
    HelloWorldName,
    HelloWorldOutput,
)
from py_boilerplate.entrypoints.mcp.deps import McpDeps
from py_boilerplate.greetings.application.say_hello import SayHelloDeps, say_hello

_DESCRIPTION = (
    "Restituisce un saluto per `name`. Usalo per verificare il percorso "
    "hello-world end-to-end. È read-only e non ha side effect. Fallisce con un "
    "tool error se `name` è vuoto o supera 100 caratteri."
)


def register_hello_world_tool(server: MCPServer[None], deps: McpDeps) -> None:
    """Registra un tool curato, con descrizione scritta per il modello."""

    @server.tool(
        name="hello_world",
        title="Hello World",
        description=_DESCRIPTION,
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True),
    )
    def hello_world(name: HelloWorldName = "world") -> HelloWorldOutput:
        input_ = HelloWorldInput(name=name)
        return say_hello(SayHelloDeps(logger=deps.logger), input_)
