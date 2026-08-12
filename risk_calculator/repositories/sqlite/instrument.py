import sqlite3
from pathlib import Path

from risk_calculator.domain.instrument import Instrument


class SQLiteInstrumentRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def get(self, symbol: str) -> Instrument | None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT symbol, instrument_type, margin_rate, name FROM instruments WHERE symbol = ?",
                (symbol.upper(),),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Instrument(*row)

    def get_all(self) -> list[Instrument]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT symbol, instrument_type, margin_rate, name FROM instruments"
            )
            rows = cursor.fetchall()
            return [Instrument(*row) for row in rows]

    def save(self, instrument: Instrument) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO instruments (symbol, instrument_type, margin_rate, name)
                VALUES (?, ?, ?, ?)
                """,
                (
                    instrument.symbol,
                    instrument.instrument_type,
                    instrument.margin_rate,
                    instrument.name,
                ),
            )

    def save_all(self, instruments: list[Instrument]) -> None:
        for instrument in instruments:
            self.save(instrument)
