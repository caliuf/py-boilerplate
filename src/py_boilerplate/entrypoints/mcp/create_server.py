"""Factory del server MCP, testabile senza trasporto."""

from mcp.server import MCPServer

from py_boilerplate import __version__
from py_boilerplate.entrypoints.mcp.deps import McpDeps
from py_boilerplate.entrypoints.mcp.tools.hello_world import register_hello_world_tool


def create_server(deps: McpDeps) -> MCPServer[None]:
    """Costruisce il server e registra solo i tool deliberatamente esposti."""

    server: MCPServer[None] = MCPServer(
        "py-boilerplate",
        title="py-boilerplate",
        instructions="Tool read-only di esempio esposti dal boilerplate Python.",
        version=__version__,
        log_level="ERROR",
    )
    register_hello_world_tool(server, deps)
    return server
