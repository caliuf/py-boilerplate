"""Integration test della superficie HTTP: valida, invoca il caso d'uso, mappa."""

from fastapi.testclient import TestClient
from tests.support.logging import MemoryLogger

from py_boilerplate.entrypoints.api.app import create_app
from py_boilerplate.entrypoints.api.deps import ApiDeps


def _client() -> tuple[TestClient, MemoryLogger]:
    logger = MemoryLogger()
    return TestClient(create_app(ApiDeps(logger=logger))), logger


def test_default_hello_world() -> None:
    client, logger = _client()

    response = client.get("/api/hello-world")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"message": "Hello, world!"}
    assert logger.events() == ["saying hello"]


def test_name_is_trimmed() -> None:
    client, _logger = _client()

    response = client.get("/api/hello-world", params={"name": "  Ada  "})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada!"}


def test_invalid_name_returns_problem_details() -> None:
    client, _logger = _client()

    response = client.get("/api/hello-world", params={"name": ""})

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    payload = response.json()
    assert payload["code"] == "VALIDATION"
    assert payload["type"] == "urn:py-boilerplate:error:validation"
    assert payload["status"] == 400
    assert payload["detail"].startswith("name: ")


def test_name_over_the_limit_returns_problem_details() -> None:
    client, _logger = _client()

    response = client.get("/api/hello-world", params={"name": "x" * 101})

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION"
