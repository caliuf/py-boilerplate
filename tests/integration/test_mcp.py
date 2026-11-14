"""Integration test del server MCP sul trasporto in-memory."""

import pytest
from mcp.client.client import Client
from mcp.server import MCPServer
from mcp.types import TextContent
from tests.support.logging import MemoryLogger

from py_boilerplate.entrypoints.mcp.create_server import create_server
from py_boilerplate.entrypoints.mcp.deps import McpDeps


def _server() -> tuple[MCPServer[None], MemoryLogger]:
    logger = MemoryLogger()
    return create_server(McpDeps(logger=logger)), logger


async def test_server_exposes_only_the_curated_tool() -> None:
    server, _logger = _server()

    async with Client(server) as client:
        tools = await client.list_tools()

    assert [tool.name for tool in tools.tools] == ["hello_world"]
    tool = tools.tools[0]
    assert tool.description is not None
    assert "read-only" in tool.description
    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True


async def test_tool_calls_the_same_use_case() -> None:
    server, logger = _server()

    async with Client(server) as client:
        result = await client.call_tool("hello_world", {"name": "Ada"})

    assert result.is_error is False
    assert result.structured_content == {"message": "Hello, Ada!"}
    assert logger.entries[0].context == {"name": "Ada"}


async def test_tool_trims_the_name() -> None:
    server, _logger = _server()

    async with Client(server) as client:
        result = await client.call_tool("hello_world", {"name": "  Ada  "})

    assert result.structured_content == {"message": "Hello, Ada!"}


@pytest.mark.parametrize("name", ["", "   ", "x" * 101])
async def test_invalid_name_is_a_tool_error(name: str) -> None:
    server, _logger = _server()

    async with Client(server) as client:
        result = await client.call_tool("hello_world", {"name": name})

    assert result.is_error is True
    first = result.content[0]
    assert isinstance(first, TextContent)
    assert "Error executing tool hello_world" in first.text
