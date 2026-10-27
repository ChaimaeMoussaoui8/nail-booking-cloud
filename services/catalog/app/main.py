"""API REST del Servicio de Catálogo."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.catalog_data import EXTRAS, SERVICES
from app.pricing import QuoteError, calculate_quote

app = FastAPI(title="Servicio de Catálogo")


class ExtraItem(BaseModel):
    extra_id: str
    nails: int | None = None


class QuoteRequest(BaseModel):
    service_id: str
    extras: list[ExtraItem] = []


@app.get("/services")
def list_services():
    return [{"id": key, **value} for key, value in SERVICES.items()]


@app.get("/extras")
def list_extras():
    return [{"id": key, **value} for key, value in EXTRAS.items()]


@app.post("/quote")
def quote(request: QuoteRequest):
    try:
        extras = [item.model_dump() for item in request.extras]
        return calculate_quote(request.service_id, extras)
    except QuoteError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
