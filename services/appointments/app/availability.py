from datetime import date, datetime, timedelta

from app.schedule_data import (
    CLOSING_TIME,
    OPENING_TIME,
    SLOT_STEP_MINUTES,
    TECHNICIANS,
    WORKING_DAYS,
)


def overlaps(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and start_b < end_a


def is_free(technician_id: int, start: datetime, end: datetime, appointments: list[dict]) -> bool:
    for appointment in appointments:
        if appointment["technician_id"] != technician_id or appointment["status"] != "confirmed":
            continue
        if overlaps(start, end, appointment["start"], appointment["end"]):
            return False
    return True


def find_free_slots(day: date, duration_minutes: int, appointments: list[dict]) -> list[dict]:
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
