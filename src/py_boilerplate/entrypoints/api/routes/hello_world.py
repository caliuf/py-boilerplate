"""Route HTTP: un handler per caso d'uso, nessuna logica di dominio."""

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from py_boilerplate.contracts.errors import AppError, ErrorCode
from py_boilerplate.contracts.hello_world import (
    HelloWorldInput,
    HelloWorldOutput,
    format_validation_error,
)
from py_boilerplate.contracts.problem_details import ProblemDetails
from py_boilerplate.entrypoints.api.deps import ApiDeps
from py_boilerplate.entrypoints.api.error_mapper import to_problem_details
from py_boilerplate.greetings.application.say_hello import SayHelloDeps, say_hello

_PROBLEM_RESPONSE: dict[int | str, dict[str, Any]] = {
    400: {
        "model": ProblemDetails,
        "content": {"application/problem+json": {}},
        "description": "Input non valido",
    }
}


def create_hello_world_router(deps: ApiDeps) -> APIRouter:
    """Router del caso d'uso `hello-world`, montato dal composition root."""

    router = APIRouter()

    @router.get(
        "/api/hello-world",
        response_model=HelloWorldOutput,
        responses=_PROBLEM_RESPONSE,
        summary="Saluta un nome",
    )
    def get_hello_world(name: str | None = None) -> HelloWorldOutput | JSONResponse:
        """Valida l'input al confine, invoca il caso d'uso e mappa il risultato."""

        try:
            input_ = HelloWorldInput.model_validate({} if name is None else {"name": name})
        except ValidationError as exc:
            problem = to_problem_details(
                AppError(ErrorCode.VALIDATION, format_validation_error(exc))
            )
            return JSONResponse(
                content=problem.model_dump(mode="json"),
                status_code=problem.status,
                media_type="application/problem+json",
            )

        return say_hello(SayHelloDeps(logger=deps.logger), input_)

    return router
