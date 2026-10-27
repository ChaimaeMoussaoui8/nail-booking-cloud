"""Tests de los endpoints de la API."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_listar_servicios():
    response = client.get("/services")
    assert response.status_code == 200
    ids = [service["id"] for service in response.json()]
    assert "manicura-biab" in ids


def test_listar_extras():
    response = client.get("/extras")
    assert response.status_code == 200
    diseno = next(extra for extra in response.json() if extra["id"] == "diseno")
    assert diseno["per_nail"] is True


def test_quote_correcto():
    body = {"service_id": "manicura-biab", "extras": [{"extra_id": "francesa"}, {"extra_id": "diseno", "nails": 2}]}
    response = client.post("/quote", json=body)
    assert response.status_code == 200
    assert response.json() == {"total_price": 54, "total_duration_minutes": 100}


def test_quote_servicio_desconocido_devuelve_400():
    response = client.post("/quote", json={"service_id": "no-existe"})
    assert response.status_code == 400
