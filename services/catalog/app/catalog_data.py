"""Catálogo de ejemplo del salón: servicios base y extras."""

SERVICES = {
    "manicura-simple": {"name": "Manicura simple", "price": 25, "duration": 45},
    "manicura-japonesa": {"name": "Manicura japonesa", "price": 35, "duration": 60},
    "manicura-biab": {"name": "Manicura BIAB", "price": 40, "duration": 75},
    "extensiones": {"name": "Extensiones", "price": 65, "duration": 120},
    "pedicura-simple": {"name": "Pedicura simple", "price": 35, "duration": 60},
    "pedicura-japonesa": {"name": "Pedicura japonesa", "price": 45, "duration": 75},
    "pedicura-biab": {"name": "Pedicura BIAB", "price": 45, "duration": 80},
}

# per_nail = True: el precio y la duración se multiplican por el número de uñas.
EXTRAS = {
    "francesa": {"name": "Francesa / Cromo / Ombré", "price": 10, "duration": 15, "per_nail": False},
    "cat-eye": {"name": "Cat eye", "price": 7, "duration": 10, "per_nail": False},
    "diseno": {"name": "Diseño", "price": 2, "duration": 5, "per_nail": True},
    "reparacion": {"name": "Reparación", "price": 3, "duration": 10, "per_nail": True},
    "retirada": {"name": "Retirada de gel o BIAB", "price": 15, "duration": 20, "per_nail": False},
}
