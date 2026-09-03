from risk_calculator.config import get_settings
from risk_calculator.repositories.sqlite.instrument import SQLiteInstrumentRepository
from risk_calculator.repositories.sqlite.portfolio import SQLitePortfolioRepository
from risk_calculator.repositories.sqlite.snapshot import SQLitePortfolioSnapshotRepository
from risk_calculator.repositories.sqlite.stress_scenario import SQLiteStressScenarioRepository
from risk_calculator.services.instrument_service import InstrumentService
from risk_calculator.services.portfolio_service import PortfolioService
from risk_calculator.services.snapshot_service import PortfolioSnapshotService
from risk_calculator.services.stress_service import StressScenarioService


def get_portfolio_service() -> PortfolioService:
    instrument_repository = SQLiteInstrumentRepository(get_settings().db_path)
    portfolio_repository = SQLitePortfolioRepository(get_settings().db_path)
    return PortfolioService(instrument_repository, portfolio_repository)


def get_instrument_service() -> InstrumentService:
    instrument_repository = SQLiteInstrumentRepository(get_settings().db_path)
    return InstrumentService(instrument_repository)


def get_stress_scenario_service() -> StressScenarioService:
    stress_scenario_repository = SQLiteStressScenarioRepository(get_settings().db_path)
    return StressScenarioService(stress_scenario_repository)


def get_portfolio_snapshot_service() -> PortfolioSnapshotService:
    portfolio_repository = SQLitePortfolioRepository(get_settings().db_path)
    portfolio_snapshot_repository = SQLitePortfolioSnapshotRepository(get_settings().db_path)
    return PortfolioSnapshotService(
        portfolio_repository=portfolio_repository,
        snapshot_repository=portfolio_snapshot_repository,
    )
