"""Adapter structlog: formato JSON/console, livelli e rispetto di NO_COLOR."""

import io
import json

import pytest

from py_boilerplate.adapters.logging import create_logger


class TtyStringIO(io.StringIO):
    """Stream che si dichiara TTY per esercitare il ramo colori."""

    def isatty(self) -> bool:
        return True


def test_json_logger_emits_one_json_object_per_event() -> None:
    stream = io.StringIO()
    logger = create_logger(level="debug", json_output=True, stream=stream)

    logger.debug("d")
    logger.info("i", name="Ada")
    logger.warning("w")
    logger.error("e")
    logger.critical("c")

    payloads = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert [payload["event"] for payload in payloads] == ["d", "i", "w", "e", "c"]
    assert payloads[1]["name"] == "Ada"
    assert payloads[1]["level"] == "info"
    assert "timestamp" in payloads[1]


def test_console_logger_is_readable_and_has_no_ansi_on_non_tty() -> None:
    stream = io.StringIO()
    logger = create_logger(level="info", json_output=False, stream=stream)

    logger.info("hello", name="Ada")

    rendered = stream.getvalue()
    assert "hello" in rendered
    assert "Ada" in rendered
    assert "\x1b[" not in rendered


def test_no_color_disables_ansi_on_a_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    stream = TtyStringIO()
    logger = create_logger(level="info", json_output=False, stream=stream)

    logger.info("hello")

    assert "\x1b[" not in stream.getvalue()


def test_tty_without_no_color_uses_ansi(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)
    stream = TtyStringIO()
    logger = create_logger(level="info", json_output=False, stream=stream)

    logger.info("hello")

    assert "\x1b[" in stream.getvalue()


def test_level_filters_lower_severity_events() -> None:
    stream = io.StringIO()
    logger = create_logger(level="error", json_output=True, stream=stream)

    logger.info("hidden")
    logger.error("visible")

    payloads = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert [payload["event"] for payload in payloads] == ["visible"]
