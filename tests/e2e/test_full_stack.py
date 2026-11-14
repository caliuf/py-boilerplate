"""E2E: processi reali per CLI, API HTTP e server MCP stdio."""

import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager

import httpx
import pytest
from mcp.client.client import Client
from mcp.client.stdio import StdioServerParameters
from tests.support.process import REPO_ROOT, clean_env, run_cli

pytestmark = pytest.mark.e2e


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@contextmanager
def _api_process() -> Iterator[str]:
    port = _free_port()
    env = clean_env(
        {
            "API_HOST": "127.0.0.1",
            "API_PORT": str(port),
        }
    )
    process = subprocess.Popen(
        [sys.executable, "-m", "py_boilerplate.entrypoints.api.main"],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 15
    try:
        while True:
            try:
                response = httpx.get(f"{base_url}/api/hello-world", timeout=1.0)
            except httpx.HTTPError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)
                continue
            if response.status_code == 200:
                break
            if time.monotonic() >= deadline:
                raise AssertionError(f"API not ready, last status {response.status_code}")
            time.sleep(0.05)
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_cli_process_end_to_end() -> None:
    result = run_cli(["hello-world", "--json", "--name", "Ada"])

    assert result.returncode == 0
    assert result.stdout.strip() == '{\n  "message": "Hello, Ada!"\n}'


def test_api_process_end_to_end() -> None:
    with _api_process() as base_url:
        response = httpx.get(f"{base_url}/api/hello-world", params={"name": "Ada"}, timeout=5)
        invalid = httpx.get(f"{base_url}/api/hello-world", params={"name": ""}, timeout=5)

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada!"}
    assert invalid.status_code == 400
    assert invalid.headers["content-type"] == "application/problem+json"


async def test_mcp_stdio_process_end_to_end() -> None:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "py_boilerplate.entrypoints.mcp.server"],
        env=clean_env(),
        cwd=REPO_ROOT,
    )

    async with Client(parameters) as client:
        result = await client.call_tool("hello_world", {"name": "Ada"})

    assert result.is_error is False
    assert result.structured_content == {"message": "Hello, Ada!"}
