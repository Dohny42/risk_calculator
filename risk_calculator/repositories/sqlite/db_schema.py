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

        # stress scenarios
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stress_scenarios (
                name            TEXT PRIMARY KEY,
                price_changes   TEXT NOT NULL,
                description     TEXT,
                created_at      TEXT NOT NULL
            );
            """
        )

        # portfolio snapshots
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id              TEXT PRIMARY KEY,
                timestamp       TEXT NOT NULL,
                total_value     REAL NOT NULL,
                total_margin    REAL NOT NULL,
                source          TEXT NOT NULL,
                label           TEXT
            );
            """
        )

        # position snapshots
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS position_snapshots (
                snapshot_id     TEXT NOT NULL,
                symbol          TEXT NOT NULL,
                quantity        REAL NOT NULL,
                price           REAL NOT NULL,
                instrument_type TEXT NOT NULL,
                margin_rate     REAL NOT NULL,
                value           REAL NOT NULL,
                margin          REAL NOT NULL,
                PRIMARY KEY (snapshot_id, symbol),
                FOREIGN KEY(snapshot_id) REFERENCES portfolio_snapshots(id)
            );
            """
        )
