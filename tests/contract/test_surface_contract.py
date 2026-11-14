"""Contratto condiviso tra CLI, API e MCP: stessa tassonomia e stessi limiti.

Se una superficie cambia codice errore, status o vincolo di validazione senza
cambiare le altre, questo test fallisce.
"""

import json

import pytest
from fastapi.testclient import TestClient
from mcp.client.client import Client
from mcp.server import MCPServer
from tests.support.logging import MemoryLogger
from tests.support.process import run_cli

from py_boilerplate.entrypoints.api.app import create_app
from py_boilerplate.entrypoints.api.deps import ApiDeps
from py_boilerplate.entrypoints.mcp.create_server import create_server
from py_boilerplate.entrypoints.mcp.deps import McpDeps


def _api() -> TestClient:
    return TestClient(create_app(ApiDeps(logger=MemoryLogger())))


@pytest.mark.parametrize("name", ["", "x" * 101])
async def test_validation_is_consistent_across_surfaces(name: str) -> None:
    cli = run_cli(["hello-world", "--json", "--name", name])
    api = _api().get("/api/hello-world", params={"name": name})
    server: MCPServer[None] = create_server(McpDeps(logger=MemoryLogger()))

    async with Client(server) as client:
        mcp = await client.call_tool("hello_world", {"name": name})

    assert cli.returncode == 2
    assert json.loads(cli.stderr)["error"] == "VALIDATION"
    assert api.status_code == 400
    assert api.json()["code"] == "VALIDATION"
    assert api.json()["type"] == "urn:py-boilerplate:error:validation"
    assert mcp.is_error is True


async def test_success_is_consistent_across_surfaces() -> None:
    cli = run_cli(["hello-world", "--json", "--name", "Ada"])
    api = _api().get("/api/hello-world", params={"name": "Ada"})
    server: MCPServer[None] = create_server(McpDeps(logger=MemoryLogger()))

    async with Client(server) as client:
        mcp = await client.call_tool("hello_world", {"name": "Ada"})

    assert json.loads(cli.stdout) == {"message": "Hello, Ada!"}
    assert api.json() == {"message": "Hello, Ada!"}
    assert mcp.structured_content == {"message": "Hello, Ada!"}
