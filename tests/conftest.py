"""Fixture condivise: isolamento delle variabili runtime tra i test."""

import pytest


@pytest.fixture(autouse=True)
def _isolated_runtime_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita che l'environment della macchina cambi i risultati dei test."""

    for name in ("LOG_LEVEL", "APP_ENV", "API_HOST", "API_PORT", "HELLO_WORLD_NAME"):
        monkeypatch.delenv(name, raising=False)
