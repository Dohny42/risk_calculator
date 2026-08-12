import sqlite3
from pathlib import Path


def create_schema(db_path: Path):
    with sqlite3.connect(db_path) as conn:
        # instruments
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS instruments (
                symbol          TEXT PRIMARY KEY,
                instrument_type TEXT NOT NULL,
                margin_rate     REAL NOT NULL,
                name            TEXT
            );
            """
        )

        # positions
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS positions (
                symbol          TEXT PRIMARY KEY,
                quantity        REAL NOT NULL,
                price           REAL NOT NULL,
                FOREIGN KEY(symbol) REFERENCES instruments(symbol)
            );
            """
        )
