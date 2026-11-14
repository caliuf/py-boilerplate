"""Mapping della tassonomia errori condivisa su RFC 9457 Problem Details."""

from py_boilerplate.contracts.errors import (
    ERROR_CODE_TO_HTTP_STATUS,
    ERROR_CODE_TO_PROBLEM,
    AppError,
)
from py_boilerplate.contracts.problem_details import ProblemDetails


def to_problem_details(error: AppError) -> ProblemDetails:
    """Traduce un errore applicativo nel payload `application/problem+json`."""

    info = ERROR_CODE_TO_PROBLEM[error.code]
    return ProblemDetails(
        code=error.code,
        type=info.type,
        title=info.title,
        status=ERROR_CODE_TO_HTTP_STATUS[error.code],
        detail=error.message,
    )
