"""Lógica de negocio: cálculo del precio y la duración de una combinación."""

from app.catalog_data import EXTRAS, SERVICES

MAX_NAILS = 10


class QuoteError(ValueError):
    """La combinación pedida no es válida."""


def calculate_quote(service_id: str, extras: list[dict]) -> dict:
    """Devuelve el precio (€) y la duración (min) totales de un servicio con sus extras.

    Cada extra es un dict con "extra_id" y, si se cobra por uña, "nails".
    """
    if service_id not in SERVICES:
        raise QuoteError(f"Servicio desconocido: {service_id}")

    service = SERVICES[service_id]
    total_price = service["price"]
    total_duration = service["duration"]

    for item in extras:
        extra_id = item.get("extra_id")
        if extra_id not in EXTRAS:
            raise QuoteError(f"Extra desconocido: {extra_id}")

        extra = EXTRAS[extra_id]
        if extra["per_nail"]:
            nails = item.get("nails")
            if not isinstance(nails, int) or not 1 <= nails <= MAX_NAILS:
                raise QuoteError(f"El extra '{extra_id}' necesita un número de uñas entre 1 y {MAX_NAILS}")
        else:
            nails = 1

        total_price += extra["price"] * nails
        total_duration += extra["duration"] * nails

    return {"total_price": total_price, "total_duration_minutes": total_duration}
