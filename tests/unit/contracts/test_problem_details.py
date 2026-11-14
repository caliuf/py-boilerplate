"""Problem Details: payload serializzabile e senza campi extra."""

import pytest
from pydantic import ValidationError

from py_boilerplate.contracts.errors import ErrorCode
from py_boilerplate.contracts.problem_details import ProblemDetails


def test_problem_details_serializes_enums() -> None:
    problem = ProblemDetails(
        code=ErrorCode.VALIDATION,
        type="urn:py-boilerplate:error:validation",
        title="Invalid input",
        status=400,
        detail="name: invalid",
    )

    dumped = problem.model_dump(mode="json")

    assert dumped["code"] == "VALIDATION"
    assert dumped["status"] == 400


def test_problem_details_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProblemDetails.model_validate(
            {
                "code": "VALIDATION",
                "type": "urn:py-boilerplate:error:validation",
                "title": "Invalid input",
                "status": 400,
                "detail": "name: invalid",
                "leak": "stack trace",
            }
        )
