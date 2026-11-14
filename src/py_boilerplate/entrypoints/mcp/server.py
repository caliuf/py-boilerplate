"""Bootstrap della superficie MCP su trasporto stdio (escluso da coverage)."""

import sys

from py_boilerplate.adapters.logging import create_logger
from py_boilerplate.entrypoints.mcp.create_server import create_server
from py_boilerplate.entrypoints.mcp.deps import McpDeps
from py_boilerplate.entrypoints.settings import RuntimeSettings


def main() -> None:
    """Entry point del console script `py-boilerplate-mcp`."""

    settings = RuntimeSettings()
    logger = create_logger(
        level=settings.log_level,
        json_output=settings.json_logs,
        stream=sys.stderr,
    )
    server = create_server(McpDeps(logger=logger))
    server.run("stdio")


if __name__ == "__main__":
    main()
