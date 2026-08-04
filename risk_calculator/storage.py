import sqlite3
from pathlib import Path

from risk_calculator.portfolio import Portfolio, Position


def save_portfolio(portfolio: Portfolio, db_path: Path) -> None:
    """Save the portfolio into an SQLite database (overwrites existing data)."""

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Create the table if it does not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                symbol   TEXT PRIMARY KEY,
                quantity REAL NOT NULL,
                price    REAL NOT NULL
            )
        """)

        # Clear previous data
        cursor.execute("DELETE FROM positions")

        # Insert current positions
        for position in portfolio.positions.values():
            cursor.execute(
                "INSERT INTO positions (symbol, quantity, price) VALUES (?, ?, ?)",
                (position.symbol, position.quantity, position.price),
            )

        conn.commit()


def load_portfolio(db_path: Path) -> Portfolio:
    """Load a portfolio from an SQLite database. Returns empty portfolio if file/table does not exist."""
    portfolio = Portfolio()

    if not db_path.exists():
        return portfolio

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT symbol, quantity, price FROM positions")
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            # Table does not exist yet
            return portfolio

        for symbol, quantity, price in rows:
            portfolio.add_position(Position(symbol, quantity, price))

    return portfolio
