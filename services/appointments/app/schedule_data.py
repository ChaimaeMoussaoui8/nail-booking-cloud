"""Datos del salón: técnicos y horario de trabajo."""

from datetime import time

TECHNICIANS = {
    1: {"name": "Ana"},
    2: {"name": "Sara"},
}

# Todos los técnicos trabajan con el mismo horario.
OPENING_TIME = time(10, 0)
CLOSING_TIME = time(20, 0)
WORKING_DAYS = {0, 1, 2, 3, 4, 5}  # 0 = lunes ... 5 = sábado (el domingo está cerrado)

# Cada cuántos minutos puede empezar una cita (10:00, 10:15, 10:30...).
SLOT_STEP_MINUTES = 15
