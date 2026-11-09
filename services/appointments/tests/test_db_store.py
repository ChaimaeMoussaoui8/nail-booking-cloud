import os
from datetime import date, datetime

import pytest

from app.booking import (
    AppointmentNotFound,
    SlotUnavailable,
    cancel_appointment,
    create_appointment,
    technician_agenda,
)

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="TEST_DATABASE_URL no está definida")

NOW = datetime(2026, 11, 10, 12, 0)


@pytest.fixture
def store():
    from app.db_store import PostgresAppointmentStore

    db_store = PostgresAppointmentStore(DATABASE_URL)
    db_store.init_schema()
    with db_store._connect() as conn:
        conn.execute("TRUNCATE appointments RESTART IDENTITY")
    return db_store


def book(store, start):
    return create_appointment(
        store,
        client_name="Laura Pérez",
        client_email="laura@example.com",
        technician_id=1,
        start=start,
        duration_minutes=100,
        total_price=54,
        now=NOW,
    )


def test_la_cita_se_guarda_en_la_base_de_datos(store):
    appointment = book(store, datetime(2026, 11, 16, 10, 0))
    saved = store.get(appointment["id"])
    assert saved["client_name"] == "Laura Pérez"
    assert saved["end"] == datetime(2026, 11, 16, 11, 40)


def test_solapamiento_con_citas_guardadas(store):
    book(store, datetime(2026, 11, 16, 10, 0))
    with pytest.raises(SlotUnavailable):
        book(store, datetime(2026, 11, 16, 11, 0))


def test_cancelar_actualiza_la_base_de_datos(store):
    appointment = book(store, datetime(2026, 11, 16, 10, 0))
    cancel_appointment(store, appointment["id"], NOW)
    assert store.get(appointment["id"])["status"] == "cancelled"
    assert technician_agenda(store, 1, date(2026, 11, 16)) == []


def test_cita_inexistente(store):
    with pytest.raises(AppointmentNotFound):
        store.get(999)
