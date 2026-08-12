from pathlib import Path

from risk_calculator.repositories.sqlite.portfolio import SQLitePortfolioRepository
from risk_calculator.services.portfolio_service import PortfolioService


def get_portfolio_service() -> PortfolioService:
    """Default dependency. In tests we will override this."""

    repository = SQLitePortfolioRepository(db_path=Path("portfolio.db"))
    return PortfolioService(repository)
