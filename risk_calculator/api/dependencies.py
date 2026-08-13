from pathlib import Path

from risk_calculator.repositories.sqlite.instrument import SQLiteInstrumentRepository
from risk_calculator.repositories.sqlite.portfolio import SQLitePortfolioRepository
from risk_calculator.services.instrument_service import InstrumentService
from risk_calculator.services.portfolio_service import PortfolioService


def get_portfolio_service() -> PortfolioService:
    instrument_repository = SQLiteInstrumentRepository(db_path=Path("portfolio.db"))
    portfolio_repository = SQLitePortfolioRepository(db_path=Path("portfolio.db"))
    return PortfolioService(instrument_repository, portfolio_repository)


def get_instrument_service() -> InstrumentService:
    instrument_repository = SQLiteInstrumentRepository(db_path=Path("portfolio.db"))
    return InstrumentService(instrument_repository)
