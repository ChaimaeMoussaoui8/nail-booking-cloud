"""Cliente REST para consultar el Servicio de Catálogo."""

import os

import httpx

from app.booking import BookingError, InvalidBooking

CATALOG_URL = os.getenv("CATALOG_URL", "http://localhost:8001")


class CatalogUnavailable(BookingError):
    status_code = 503


class CatalogClient:
    def __init__(self, base_url: str = CATALOG_URL):
        self.base_url = base_url

    def quote(self, service_id: str, extras: list[dict]) -> dict:
        """Pide al Servicio de Catálogo el precio y la duración de una combinación."""
        try:
            response = httpx.post(
                f"{self.base_url}/quote",
                json={"service_id": service_id, "extras": extras},
                timeout=5,
            )
        except httpx.HTTPError as error:
            raise CatalogUnavailable("El Servicio de Catálogo no está disponible") from error

        if response.status_code == 400:
            raise InvalidBooking(response.json().get("detail", "Combinación no válida"))
        if response.status_code != 200:
            raise CatalogUnavailable("Respuesta inesperada del Servicio de Catálogo")
        return response.json()