import sqlite3
from pathlib import Path

from risk_calculator.domain.instrument import Instrument
from risk_calculator.domain.portfolio import Portfolio, Position


class SQLitePortfolioRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get(self) -> Portfolio:
        portfolio = Portfolio()

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT
                    p.symbol,
                    p.quantity,
                    p.price,
                    i.instrument_type,
                    i.margin_rate,
                    i.name
                FROM positions p
                JOIN instruments i ON i.symbol = p.symbol
            """).fetchall()

            for row in rows:
                symbol, quantity, price, instrument_type, margin_rate, name = row
                instrument = Instrument(
                    symbol=symbol,
                    instrument_type=instrument_type,
                    margin_rate=margin_rate,
                    name=name,
                )
                position = Position(
                    instrument=instrument,
                    quantity=quantity,
                    price=price,
                )
                # We bypass validation here because data already comes from DB
                portfolio.positions[symbol] = position

        return portfolio

    def save(self, portfolio: Portfolio) -> None:
        with sqlite3.connect(self.db_path) as conn:
            # Clear previous data
            conn.execute("DELETE FROM positions")

            # Insert current positions
            for position in portfolio.positions.values():
                conn.execute(
                    "INSERT INTO positions (symbol, quantity, price) VALUES (?, ?, ?)",
                    (
                        position.instrument.symbol,
                        position.quantity,
                        position.price,
                    ),
                )

            conn.commit()
