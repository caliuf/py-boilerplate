"""Mapping errori → Problem Details e configurazione runtime."""

import pytest
from pydantic import ValidationError

from py_boilerplate.contracts.errors import (
    ERROR_CODE_TO_HTTP_STATUS,
    ERROR_CODE_TO_PROBLEM,
    AppError,
    ErrorCode,
)
from py_boilerplate.entrypoints.api.error_mapper import to_problem_details


@pytest.mark.parametrize("code", list(ErrorCode))
def test_every_error_maps_to_problem_details(code: ErrorCode) -> None:
    problem = to_problem_details(AppError(code, "detail"))

    assert problem.code == code
    assert problem.status == ERROR_CODE_TO_HTTP_STATUS[code]
    assert problem.type == ERROR_CODE_TO_PROBLEM[code].type
    assert problem.title == ERROR_CODE_TO_PROBLEM[code].title
    assert problem.detail == "detail"


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    from py_boilerplate.entrypoints.settings import ApiSettings

    settings = ApiSettings()

    assert settings.log_level == "info"
    assert settings.app_env == "production"
    assert settings.json_logs is True
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8100


def test_settings_read_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    from py_boilerplate.entrypoints.settings import ApiSettings

    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("API_PORT", "9000")

    settings = ApiSettings()

    assert settings.log_level == "debug"
    assert settings.json_logs is False
    assert settings.api_port == 9000


def test_log_level_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    from py_boilerplate.entrypoints.settings import RuntimeSettings

    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    assert RuntimeSettings().log_level == "error"


def test_invalid_log_level_fails_at_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    from py_boilerplate.entrypoints.settings import RuntimeSettings

    monkeypatch.setenv("LOG_LEVEL", "verbose")

    with pytest.raises(ValidationError):
        RuntimeSettings()


def test_invalid_port_fails_at_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    from py_boilerplate.entrypoints.settings import ApiSettings

    monkeypatch.setenv("API_PORT", "0")

    with pytest.raises(ValidationError):
        ApiSettings()
