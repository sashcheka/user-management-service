import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.integration
def test_healthcheck_endpoint():
    response = client.get("/healthcheck/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
