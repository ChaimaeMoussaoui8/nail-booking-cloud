"""Tests unitarios de la búsqueda de huecos."""

from datetime import date, datetime

from app.availability import find_free_slots, overlaps

MONDAY = date(2026, 11, 16)
SUNDAY = date(2026, 11, 15)


def appointment(technician_id, start, end, status="confirmed"):
    return {"technician_id": technician_id, "start": start, "end": end, "status": status}


def test_solapamiento():
    a = (datetime(2026, 11, 16, 10, 0), datetime(2026, 11, 16, 11, 0))
    assert overlaps(*a, datetime(2026, 11, 16, 10, 30), datetime(2026, 11, 16, 11, 30))
    # Una cita que empieza justo cuando termina otra no se solapa
    assert not overlaps(*a, datetime(2026, 11, 16, 11, 0), datetime(2026, 11, 16, 12, 0))


def test_domingo_cerrado():
    assert find_free_slots(SUNDAY, 60, []) == []


def test_dia_vacio_primer_y_ultimo_hueco():
    slots = [s for s in find_free_slots(MONDAY, 60, []) if s["technician_id"] == 1]
    assert slots[0]["start"] == datetime(2026, 11, 16, 10, 0)
    # El último hueco de 60 min empieza a las 19:00 para terminar a las 20:00
    assert slots[-1]["start"] == datetime(2026, 11, 16, 19, 0)


def test_cita_existente_bloquea_huecos_solapados():
    existing = [appointment(1, datetime(2026, 11, 16, 10, 0), datetime(2026, 11, 16, 12, 0))]
    starts = [s["start"] for s in find_free_slots(MONDAY, 60, existing) if s["technician_id"] == 1]
    assert datetime(2026, 11, 16, 11, 0) not in starts
    assert datetime(2026, 11, 16, 12, 0) in starts


def test_cita_de_otro_tecnico_no_bloquea():
    existing = [appointment(2, datetime(2026, 11, 16, 10, 0), datetime(2026, 11, 16, 12, 0))]
    starts = [s["start"] for s in find_free_slots(MONDAY, 60, existing) if s["technician_id"] == 1]
    assert datetime(2026, 11, 16, 10, 0) in starts


def test_cita_cancelada_no_bloquea():
    existing = [appointment(1, datetime(2026, 11, 16, 10, 0), datetime(2026, 11, 16, 12, 0), "cancelled")]
    starts = [s["start"] for s in find_free_slots(MONDAY, 60, existing) if s["technician_id"] == 1]
    assert datetime(2026, 11, 16, 10, 0) in starts


def test_servicio_mas_largo_que_el_dia():
    assert find_free_slots(MONDAY, 11 * 60, []) == []
