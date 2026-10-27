"""API REST del Servicio de Citas."""

from datetime import date, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.availability import find_free_slots
from app.booking import (
    AppointmentStore,
    BookingError,
    cancel_appointment,
    create_appointment,
    technician_agenda,
)
from app.catalog_client import CatalogClient
from app.schedule_data import TECHNICIANS

app = FastAPI(title="Servicio de Citas")
store = AppointmentStore()


def get_store() -> AppointmentStore:
    return store


def get_catalog() -> CatalogClient:
    return CatalogClient()


def get_now() -> datetime:
    return datetime.now()


Store = Annotated[AppointmentStore, Depends(get_store)]
Catalog = Annotated[CatalogClient, Depends(get_catalog)]
Now = Annotated[datetime, Depends(get_now)]
Day = Annotated[date, Query(alias="date")]


class ExtraItem(BaseModel):
    extra_id: str
    nails: int | None = None


class AppointmentRequest(BaseModel):
    client_name: str
    client_email: str
    technician_id: int
    service_id: str
    extras: list[ExtraItem] = []
    start: datetime


@app.exception_handler(BookingError)
def handle_booking_error(request, error: BookingError):
    return JSONResponse(status_code=error.status_code, content={"error": str(error)})


@app.get("/technicians")
def list_technicians():
    return [{"id": key, **value} for key, value in TECHNICIANS.items()]


@app.get("/availability")
def availability(
    day: Day,
    duration: Annotated[int, Query(gt=0, le=600)],
    store: Store,
):
    return find_free_slots(day, duration, store.appointments)


@app.post("/appointments", status_code=201)
def book(
    request: AppointmentRequest,
    store: Store,
    catalog: Catalog,
    now: Now,
):
    extras = [item.model_dump() for item in request.extras]
    quote = catalog.quote(request.service_id, extras)
    return create_appointment(
        store,
        client_name=request.client_name,
        client_email=request.client_email,
        technician_id=request.technician_id,
        start=request.start,
        duration_minutes=quote["total_duration_minutes"],
        total_price=quote["total_price"],
        now=now,
    )


@app.delete("/appointments/{appointment_id}", status_code=204)
def cancel(
    appointment_id: int,
    store: Store,
    now: Now,
):
    cancel_appointment(store, appointment_id, now)
    return Response(status_code=204)


@app.get("/technicians/{technician_id}/appointments")
def agenda(
    technician_id: int,
    day: Day,
    store: Store,
):
    return technician_agenda(store, technician_id, day)