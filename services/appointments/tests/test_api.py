"""Tests de los endpoints de la API (el Servicio de Catálogo se simula)."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.booking import AppointmentStore, InvalidBooking
from app.main import app, get_catalog, get_now, get_store


class FakeCatalog:
    def quote(self, service_id, extras):
        if service_id == "no-existe":
            raise InvalidBooking("Servicio desconocido: no-existe")
        return {"total_price": 54, "total_duration_minutes": 100}


@pytest.fixture
def client():
    store = AppointmentStore()
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_catalog] = lambda: FakeCatalog()
    app.dependency_overrides[get_now] = lambda: datetime(2026, 11, 10, 12, 0)
    yield TestClient(app)
    app.dependency_overrides.clear()


BOOKING = {
    "client_name": "Laura Pérez",
    "client_email": "laura@example.com",
    "technician_id": 1,
    "service_id": "manicura-biab",
    "extras": [{"extra_id": "francesa"}, {"extra_id": "diseno", "nails": 2}],
    "start": "2026-11-16T10:00:00",
}


def test_listar_tecnicos(client):
    assert len(client.get("/technicians").json()) == 2


def test_disponibilidad(client):
    response = client.get("/availability", params={"date": "2026-11-16", "duration": 100})
    assert response.status_code == 200
    assert response.json()[0]["start"] == "2026-11-16T10:00:00"


def test_reservar_y_conflicto(client):
    response = client.post("/appointments", json=BOOKING)
    assert response.status_code == 201
    assert response.json()["end"] == "2026-11-16T11:40:00"
    assert response.json()["total_price"] == 54
    assert client.post("/appointments", json=BOOKING).status_code == 409


def test_reservar_servicio_desconocido(client):
    response = client.post("/appointments", json={**BOOKING, "service_id": "no-existe"})
    assert response.status_code == 422


def test_cancelar_y_agenda(client):
    appointment_id = client.post("/appointments", json=BOOKING).json()["id"]
    agenda = client.get("/technicians/1/appointments", params={"date": "2026-11-16"}).json()
    assert len(agenda) == 1
    assert client.delete(f"/appointments/{appointment_id}").status_code == 204
    agenda = client.get("/technicians/1/appointments", params={"date": "2026-11-16"}).json()
    assert agenda == []


def test_cancelar_inexistente(client):
    assert client.delete("/appointments/42").status_code == 404