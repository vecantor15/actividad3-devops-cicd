import pytest

from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_index_returns_application_metadata(client):
    response = client.get("/")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["application"] == "devops-web-lab"
    assert "CI/CD" in payload["message"]


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_unknown_route_returns_404(client):
    response = client.get("/ruta-inexistente")

    assert response.status_code == 404
    assert response.get_json() == {"error": "not_found"}
