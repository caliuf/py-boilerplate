"""RFC 9457 Problem Details, come prodotto dal confine HTTP."""

from pydantic import BaseModel, ConfigDict

from py_boilerplate.contracts.errors import ErrorCode, HttpErrorStatus


class ProblemDetails(BaseModel):
    """Payload `application/problem+json` condiviso con i client."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: ErrorCode
    type: str
    title: str
    status: HttpErrorStatus
    detail: str
