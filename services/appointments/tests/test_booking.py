"""Tests unitarios de las reglas de reserva y cancelación."""

from datetime import date, datetime

import pytest

from app.booking import (
    AppointmentNotFound,
    AppointmentStore,
    CancellationNotAllowed,
    InvalidBooking,
    SlotUnavailable,
    cancel_appointment,
    create_appointment,
    technician_agenda,
)

NOW = datetime(2026, 11, 10, 12, 0)
MONDAY_10 = datetime(2026, 11, 16, 10, 0)


def book(store, start=MONDAY_10, technician_id=1, duration=100):
    return create_appointment(
        store,
        client_name="Laura Pérez",
        client_email="laura@example.com",
        technician_id=technician_id,
        start=start,
        duration_minutes=duration,
        total_price=54,
        now=NOW,
    )


def test_reserva_correcta():
    store = AppointmentStore()
    appointment = book(store)
    assert appointment["id"] == 1
    assert appointment["end"] == datetime(2026, 11, 16, 11, 40)
    assert appointment["status"] == "confirmed"


def test_reserva_solapada_rechazada():
    store = AppointmentStore()
    book(store)
    with pytest.raises(SlotUnavailable):
        book(store, start=datetime(2026, 11, 16, 11, 0))


def test_otro_tecnico_puede_reservar_a_la_misma_hora():
    store = AppointmentStore()
    book(store)
    assert book(store, technician_id=2)["id"] == 2


@pytest.mark.parametrize(
    "start, technician_id",
    [
        (datetime(2026, 11, 9, 10, 0), 1),  # en el pasado
        (datetime(2026, 11, 15, 10, 0), 1),  # domingo
        (datetime(2026, 11, 16, 9, 0), 1),  # antes de abrir
        (datetime(2026, 11, 16, 19, 0), 1),  # termina después de cerrar
        (MONDAY_10, 99),  # técnico inexistente
    ],
)
def test_reservas_no_validas(start, technician_id):
    with pytest.raises(InvalidBooking):
        book(AppointmentStore(), start=start, technician_id=technician_id)


def test_cancelar_con_mas_de_24h_libera_el_hueco():
    store = AppointmentStore()
    appointment = book(store)
    cancel_appointment(store, appointment["id"], NOW)
    assert appointment["status"] == "cancelled"
    # El hueco vuelve a estar libre
    assert book(store)["id"] == 2


def test_cancelar_con_menos_de_24h_rechazado():
    store = AppointmentStore()
    appointment = book(store)
    with pytest.raises(CancellationNotAllowed):
        cancel_appointment(store, appointment["id"], datetime(2026, 11, 15, 12, 0))


def test_cancelar_cita_inexistente():
    with pytest.raises(AppointmentNotFound):
        cancel_appointment(AppointmentStore(), 42, NOW)


def test_agenda_ordenada_y_sin_canceladas():
    store = AppointmentStore()
    late = book(store, start=datetime(2026, 11, 16, 16, 0))
    early = book(store, start=datetime(2026, 11, 16, 12, 0))
    cancelled = book(store, start=datetime(2026, 11, 16, 14, 0))
    cancel_appointment(store, cancelled["id"], NOW)
    agenda = technician_agenda(store, 1, date(2026, 11, 16))
    assert [a["id"] for a in agenda] == [early["id"], late["id"]]
