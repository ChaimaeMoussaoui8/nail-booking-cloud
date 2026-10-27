"""Lógica de negocio: búsqueda de huecos libres."""

from datetime import date, datetime, timedelta

from app.schedule_data import (
    CLOSING_TIME,
    OPENING_TIME,
    SLOT_STEP_MINUTES,
    TECHNICIANS,
    WORKING_DAYS,
)


def overlaps(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    """Dos intervalos se solapan si cada uno empieza antes de que termine el otro."""
    return start_a < end_b and start_b < end_a


def is_free(technician_id: int, start: datetime, end: datetime, appointments: list[dict]) -> bool:
    """Comprueba que el técnico no tiene ninguna cita confirmada entre start y end."""
    for appointment in appointments:
        if appointment["technician_id"] != technician_id or appointment["status"] != "confirmed":
            continue
        if overlaps(start, end, appointment["start"], appointment["end"]):
            return False
    return True


def find_free_slots(day: date, duration_minutes: int, appointments: list[dict]) -> list[dict]:
    """Devuelve los huecos de un día donde cabe un servicio de la duración indicada."""
    if day.weekday() not in WORKING_DAYS:
        return []

    duration = timedelta(minutes=duration_minutes)
    step = timedelta(minutes=SLOT_STEP_MINUTES)
    opening = datetime.combine(day, OPENING_TIME)
    closing = datetime.combine(day, CLOSING_TIME)

    slots = []
    for technician_id in TECHNICIANS:
        start = opening
        while start + duration <= closing:
            end = start + duration
            if is_free(technician_id, start, end, appointments):
                slots.append({"technician_id": technician_id, "start": start, "end": end})
            start += step
    return slots
