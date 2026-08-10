from pathlib import Path
from typing import Protocol

from risk_calculator.portfolio import Portfolio
from risk_calculator.storage import load_portfolio, save_portfolio


class PortfolioRepository(Protocol):
    def get(self) -> Portfolio:
        """Load the current portfolio."""
        ...

    def save(self, portfolio: Portfolio) -> None:
        """Persist the portfolio."""
        ...


class SQLitePortfolioRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get(self) -> Portfolio:
        return load_portfolio(self.db_path)

    def save(self, portfolio: Portfolio) -> None:
        save_portfolio(portfolio, self.db_path)
