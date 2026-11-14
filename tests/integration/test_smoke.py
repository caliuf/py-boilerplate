"""Smoke test: il percorso pubblico più importante parte da processo reale."""

from tests.support.process import run_cli


def test_cli_hello_world_smoke() -> None:
    result = run_cli(["hello-world", "--json"])

    assert result.returncode == 0
    assert '"message": "Hello, world!"' in result.stdout
    assert result.stderr == ""
