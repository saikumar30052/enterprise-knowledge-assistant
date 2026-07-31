import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
for candidate in (project_root, project_root.parent):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "running"
    assert payload["application"] == "Enterprise Knowledge Assistant"


def test_query_endpoint_success() -> None:
    response = client.post(
        "/query",
        json={"question": "Explain Marketing Mart"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["question"]
    assert payload["answer"]
    assert payload["citations"] is not None


def test_query_endpoint_empty_question() -> None:
    response = client.post(
        "/query",
        json={"question": ""},
    )
    assert response.status_code == 400


def test_query_endpoint_whitespace_question() -> None:
    response = client.post(
        "/query",
        json={"question": "     "},
    )
    assert response.status_code == 400


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
    print("All API tests passed.")
