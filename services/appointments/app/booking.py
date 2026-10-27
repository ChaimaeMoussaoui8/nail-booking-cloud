"""Lógica de negocio: crear, cancelar y consultar citas."""

from datetime import date, datetime, timedelta

from app.availability import is_free
from app.schedule_data import CLOSING_TIME, OPENING_TIME, TECHNICIANS, WORKING_DAYS

MIN_HOURS_TO_CANCEL = 24


class BookingError(Exception):
    """Error de negocio. Cada subclase corresponde a un código HTTP."""

    status_code = 400


class InvalidBooking(BookingError):
    status_code = 422


class AppointmentNotFound(BookingError):
    status_code = 404


class SlotUnavailable(BookingError):
    status_code = 409


class CancellationNotAllowed(BookingError):
    status_code = 422


class AppointmentStore:
    """Almacén de citas en memoria (se sustituirá por PostgreSQL)."""

    def __init__(self):
        self.appointments: list[dict] = []
        self._next_id = 1

    def add(self, appointment: dict) -> dict:
        appointment["id"] = self._next_id
        self._next_id += 1
        self.appointments.append(appointment)
        return appointment

    def get(self, appointment_id: int) -> dict:
        for appointment in self.appointments:
            if appointment["id"] == appointment_id:
                return appointment
        raise AppointmentNotFound(f"No existe la cita {appointment_id}")


def create_appointment(
    store: AppointmentStore,
    *,
    client_name: str,
    client_email: str,
    technician_id: int,
    start: datetime,
    duration_minutes: int,
    total_price: int,
    now: datetime,
) -> dict:
    """Crea una cita si el hueco es válido y está libre."""
    end = start + timedelta(minutes=duration_minutes)

    if technician_id not in TECHNICIANS:
        raise InvalidBooking(f"No existe el técnico {technician_id}")
    if start <= now:
        raise InvalidBooking("No se pueden reservar citas en el pasado")
    if start.weekday() not in WORKING_DAYS:
        raise InvalidBooking("El salón está cerrado ese día")
    if start.time() < OPENING_TIME or end.time() > CLOSING_TIME or end.date() != start.date():
        raise InvalidBooking("La cita debe estar dentro del horario del salón")
    if not is_free(technician_id, start, end, store.appointments):
        raise SlotUnavailable("El técnico ya tiene una cita en ese horario")

    return store.add(
        {
            "client_name": client_name,
            "client_email": client_email,
            "technician_id": technician_id,
            "start": start,
            "end": end,
            "total_price": total_price,
            "status": "confirmed",
        }
    )


def cancel_appointment(store: AppointmentStore, appointment_id: int, now: datetime) -> dict:
    """Cancela una cita si faltan al menos 24 horas. El hueco queda libre."""
    appointment = store.get(appointment_id)
    if appointment["status"] == "cancelled":
        raise InvalidBooking("La cita ya está cancelada")
    if appointment["start"] - now < timedelta(hours=MIN_HOURS_TO_CANCEL):
        raise CancellationNotAllowed("Las citas solo pueden cancelarse hasta 24 horas antes")
    appointment["status"] = "cancelled"
    return appointment


def technician_agenda(store: AppointmentStore, technician_id: int, day: date) -> list[dict]:
    """Citas confirmadas de un técnico en un día, ordenadas por hora."""
    if technician_id not in TECHNICIANS:
        raise AppointmentNotFound(f"No existe el técnico {technician_id}")
    agenda = [
        appointment
        for appointment in store.appointments
        if appointment["technician_id"] == technician_id
        and appointment["status"] == "confirmed"
        and appointment["start"].date() == day
    ]
    return sorted(agenda, key=lambda appointment: appointment["start"])