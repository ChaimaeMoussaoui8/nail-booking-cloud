import time

import psycopg
from psycopg.rows import dict_row

from app.booking import AppointmentNotFound

SCHEMA = """
CREATE TABLE IF NOT EXISTS appointments (
    id            SERIAL PRIMARY KEY,
    client_name   TEXT        NOT NULL,
    client_email  TEXT        NOT NULL,
    technician_id INTEGER     NOT NULL,
    start         TIMESTAMP   NOT NULL,
    "end"         TIMESTAMP   NOT NULL,
    total_price   INTEGER     NOT NULL,
    status        TEXT        NOT NULL
)
"""

COLUMNS = 'id, client_name, client_email, technician_id, start, "end", total_price, status'


class PostgresAppointmentStore:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def _connect(self):
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def init_schema(self, attempts: int = 10, wait_seconds: float = 2) -> None:
        for attempt in range(1, attempts + 1):
            try:
                with self._connect() as conn:
                    conn.execute(SCHEMA)
                return
            except psycopg.OperationalError:
                if attempt == attempts:
                    raise
                time.sleep(wait_seconds)

    @property
    def appointments(self) -> list[dict]:
        with self._connect() as conn:
            return conn.execute(f"SELECT {COLUMNS} FROM appointments ORDER BY id").fetchall()

    def add(self, appointment: dict) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                """
                INSERT INTO appointments
                    (client_name, client_email, technician_id, start, "end", total_price, status)
                VALUES
                    (%(client_name)s, %(client_email)s, %(technician_id)s, %(start)s, %(end)s,
                     %(total_price)s, %(status)s)
                RETURNING id
                """,
                appointment,
            ).fetchone()
        return {"id": row["id"], **appointment}

    def get(self, appointment_id: int) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT {COLUMNS} FROM appointments WHERE id = %s", (appointment_id,)
            ).fetchone()
        if row is None:
            raise AppointmentNotFound(f"No existe la cita {appointment_id}")
        return row

    def set_status(self, appointment_id: int, status: str) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                f"UPDATE appointments SET status = %s WHERE id = %s RETURNING {COLUMNS}",
                (status, appointment_id),
            ).fetchone()
        if row is None:
            raise AppointmentNotFound(f"No existe la cita {appointment_id}")
        return row
