"""Contract test tra il contratto canonico Python e il mirror web.

Il client web usa Zod per validare le risposte, ma la fonte canonica resta
Pydantic/OpenAPI. Questo test fallisce se i vincoli condivisi o la superficie
HTTP cambiano senza aggiornare il client.
"""

from tests.support.logging import MemoryLogger

from py_boilerplate.contracts.hello_world import HelloWorldInput, HelloWorldOutput
from py_boilerplate.contracts.problem_details import ProblemDetails
from py_boilerplate.entrypoints.api.app import create_app
from py_boilerplate.entrypoints.api.deps import ApiDeps


def test_input_contract_matches_the_web_mirror() -> None:
    schema = HelloWorldInput.model_json_schema()

    assert schema["additionalProperties"] is False
    assert schema["$defs"]["HelloWorldName"] == {
        "maxLength": 100,
        "minLength": 1,
        "type": "string",
    }
    assert schema["properties"]["name"]["default"] == "world"
    assert schema["properties"]["name"]["$ref"] == "#/$defs/HelloWorldName"


def test_output_contract_matches_the_web_mirror() -> None:
    schema = HelloWorldOutput.model_json_schema()

    assert schema["required"] == ["message"]
    assert schema["properties"]["message"]["type"] == "string"
    assert schema["additionalProperties"] is False


def test_problem_details_contract_matches_the_web_mirror() -> None:
    schema = ProblemDetails.model_json_schema()

    assert schema["$defs"]["ErrorCode"]["enum"] == [
        "INTERNAL",
        "VALIDATION",
        "UNAUTHORIZED",
        "NOT_FOUND",
        "CONFLICT",
    ]
    assert schema["$defs"]["HttpErrorStatus"]["enum"] == [400, 401, 404, 409, 500]
    assert schema["required"] == ["code", "type", "title", "status", "detail"]


def test_openapi_exposes_the_hello_world_route() -> None:
    document = create_app(ApiDeps(logger=MemoryLogger())).openapi()
    route = document["paths"]["/api/hello-world"]["get"]

    assert route["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/HelloWorldOutput"
    )
    assert "application/problem+json" in route["responses"]["400"]["content"]
