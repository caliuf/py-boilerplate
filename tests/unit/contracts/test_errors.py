"""Unicità e coerenza della tassonomia errori tra le superfici."""

import pytest

from py_boilerplate.contracts.errors import (
    ERROR_CODE_TO_EXIT_CODE,
    ERROR_CODE_TO_HTTP_STATUS,
    ERROR_CODE_TO_PROBLEM,
    AppError,
    ApplicationError,
    ErrorCode,
)


def test_every_error_code_has_a_mapping() -> None:
    codes = set(ErrorCode)
    assert set(ERROR_CODE_TO_EXIT_CODE) == codes
    assert set(ERROR_CODE_TO_HTTP_STATUS) == codes
    assert set(ERROR_CODE_TO_PROBLEM) == codes


@pytest.mark.parametrize(
    ("code", "exit_code"),
    [
        (ErrorCode.INTERNAL, 1),
        (ErrorCode.VALIDATION, 2),
        (ErrorCode.UNAUTHORIZED, 3),
        (ErrorCode.NOT_FOUND, 4),
        (ErrorCode.CONFLICT, 5),
    ],
)
def test_exit_codes_are_stable(code: ErrorCode, exit_code: int) -> None:
    assert ERROR_CODE_TO_EXIT_CODE[code] == exit_code


@pytest.mark.parametrize(
    ("code", "status"),
    [
        (ErrorCode.INTERNAL, 500),
        (ErrorCode.VALIDATION, 400),
        (ErrorCode.UNAUTHORIZED, 401),
        (ErrorCode.NOT_FOUND, 404),
        (ErrorCode.CONFLICT, 409),
    ],
)
def test_http_statuses_are_stable(code: ErrorCode, status: int) -> None:
    assert ERROR_CODE_TO_HTTP_STATUS[code] == status


def test_problem_types_are_urn_namespaced() -> None:
    for info in ERROR_CODE_TO_PROBLEM.values():
        assert info.type.startswith("urn:py-boilerplate:error:")
        assert info.title


def test_app_error_exception_carries_the_value() -> None:
    error = AppError(ErrorCode.NOT_FOUND, "missing")
    exception = ApplicationError(error)

    assert exception.error is error
    assert str(exception) == "missing"
