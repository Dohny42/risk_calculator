from risk_calculator.config import get_settings
from risk_calculator.repositories.sqlite.instrument import SQLiteInstrumentRepository
from risk_calculator.repositories.sqlite.portfolio import SQLitePortfolioRepository
from risk_calculator.services.instrument_service import InstrumentService
from risk_calculator.services.portfolio_service import PortfolioService


def get_portfolio_service() -> PortfolioService:
    instrument_repository = SQLiteInstrumentRepository(get_settings().db_path)
    portfolio_repository = SQLitePortfolioRepository(get_settings().db_path)
    return PortfolioService(instrument_repository, portfolio_repository)


def get_instrument_service() -> InstrumentService:
    instrument_repository = SQLiteInstrumentRepository(get_settings().db_path)
    return InstrumentService(instrument_repository)
