from pathlib import Path

import pytest

from risk_calculator.domain.instrument import Instrument
from risk_calculator.domain.portfolio import Portfolio, Position
from risk_calculator.domain.stress import StressScenario
from risk_calculator.repositories.sqlite.db_schema import create_schema
from risk_calculator.repositories.sqlite.instrument import SQLiteInstrumentRepository
from risk_calculator.repositories.sqlite.portfolio import SQLitePortfolioRepository
from risk_calculator.repositories.sqlite.stress_scenario import SQLiteStressScenarioRepository


@pytest.fixture
def db_path(tmp_path) -> Path:
    db_path = tmp_path / "portfolio.db"
    create_schema(db_path)
    return db_path


@pytest.fixture
def instrument_repo(db_path: Path):
    return SQLiteInstrumentRepository(db_path)


@pytest.fixture
def portfolio_repo(db_path: Path) -> SQLitePortfolioRepository:
    return SQLitePortfolioRepository(db_path)


@pytest.fixture
def stress_scenario_repo(db_path: Path) -> SQLiteStressScenarioRepository:
    return SQLiteStressScenarioRepository(db_path)


@pytest.fixture
def sample_instruments(instrument_repo: SQLiteInstrumentRepository):
    instruments = [
        Instrument("AAPL", "equity", 0.3, "Apple Inc."),
        Instrument("MSFT", "equity", 0.3, "Microsoft Corp."),
    ]
    instrument_repo.save_all(instruments)
    return instruments


def test_save_and_load_instrument(instrument_repo: SQLiteInstrumentRepository):
    instrument = Instrument("AAPL", "equity", 0.3, "Apple Inc.")
    instrument_repo.save(instrument)

    loaded_instrument = instrument_repo.get("AAPL")

    # Check that the loaded instrument matches the original
    assert loaded_instrument is not None
    assert loaded_instrument.symbol == instrument.symbol
    assert loaded_instrument.instrument_type == instrument.instrument_type
    assert loaded_instrument.margin_rate == instrument.margin_rate
    assert loaded_instrument.name == instrument.name


def test_load_nonexistent_instrument(instrument_repo: SQLiteInstrumentRepository):
    assert instrument_repo.get("NONEXISTENT") is None


def test_overwrite_existing_instrument(instrument_repo: SQLiteInstrumentRepository):
    instrument1 = Instrument("AAPL", "equity", 0.3, "Apple Inc.")
    instrument_repo.save(instrument1)

    instrument2 = Instrument("AAPL", "equity", 0.25, "Apple Inc. Updated")
    instrument_repo.save(instrument2)

    loaded_instrument = instrument_repo.get("AAPL")
    assert loaded_instrument is not None
    assert loaded_instrument.symbol == instrument2.symbol
    assert loaded_instrument.instrument_type == instrument2.instrument_type
    assert loaded_instrument.margin_rate == instrument2.margin_rate
    assert loaded_instrument.name == instrument2.name


def test_save_and_load_all_instruments(instrument_repo: SQLiteInstrumentRepository):
    instruments = [
        Instrument("AAPL", "equity", 0.3, "Apple Inc."),
        Instrument("MSFT", "equity", 0.3, "Microsoft Corp."),
    ]
    instrument_repo.save_all(instruments)

    loaded_instruments = instrument_repo.get_all()
    assert len(loaded_instruments) == len(instruments)
    for instrument in instruments:
        loaded_instrument = instrument_repo.get(instrument.symbol)
        assert loaded_instrument is not None
        assert loaded_instrument.symbol == instrument.symbol
        assert loaded_instrument.instrument_type == instrument.instrument_type
        assert loaded_instrument.margin_rate == instrument.margin_rate
        assert loaded_instrument.name == instrument.name

    def test_save_and_load_portfolio(
        sample_instruments: list[Instrument], portfolio_repo: SQLitePortfolioRepository
    ):
        # Create a sample portfolio
        portfolio = Portfolio()
        portfolio.add_position(
            Position(
                Instrument("AAPL", "equity", 0.3),
                quantity=10,
                price=150.0,
            )
        )
        portfolio.add_position(
            Position(
                Instrument("MSFT", "equity", 0.3),
                quantity=5,
                price=300.0,
            )
        )
        portfolio_repo.save(portfolio)

        # Load the portfolio from the database
        loaded_portfolio = portfolio_repo.get()

        # Check that the loaded portfolio matches the original
        assert len(loaded_portfolio.positions) == 2
        assert loaded_portfolio.total_value() == portfolio.total_value()


def test_load_empty_portfolio(portfolio_repo: SQLitePortfolioRepository, tmp_path):
    # Load the portfolio from the database (should be empty)
    loaded_portfolio = portfolio_repo.get()

    # Check that the loaded portfolio is empty
    assert len(loaded_portfolio.positions) == 0
    assert loaded_portfolio.total_value() == 0.0


def test_overwrite_existing_portfolio(
    sample_instruments: list[Instrument],
    portfolio_repo: SQLitePortfolioRepository,
):
    # Create a sample portfolio and save it
    portfolio1 = Portfolio()
    portfolio1.add_position(
        Position(
            Instrument("AAPL", "equity", 0.3),
            quantity=10,
            price=150.0,
        )
    )
    portfolio_repo.save(portfolio1)

    # Create a new portfolio and save it (should overwrite the existing one)
    portfolio2 = Portfolio()
    portfolio2.add_position(
        Position(
            Instrument("MSFT", "equity", 0.3),
            quantity=5,
            price=300.0,
        )
    )
    portfolio_repo.save(portfolio2)

    # Load the portfolio from the database
    loaded_portfolio = portfolio_repo.get()

    # Check that the loaded portfolio matches the second one
    assert len(loaded_portfolio.positions) == 1
    assert loaded_portfolio.get_position("AAPL") is None
    assert loaded_portfolio.get_position("MSFT") is not None
    assert loaded_portfolio.total_value() == portfolio2.total_value()


def test_save_and_load_stress_scenario(
    stress_scenario_repo: SQLiteStressScenarioRepository,
):
    stress_scenario = StressScenario(
        name="Market Crash",
        price_changes={"AAPL": -0.1, "MSFT": -0.2},
        description="A sudden market crash scenario.",
    )
    stress_scenario_repo.save(stress_scenario)

    loaded_stress_scenario = stress_scenario_repo.get("Market Crash")

    assert loaded_stress_scenario is not None
    assert loaded_stress_scenario.name == stress_scenario.name
    assert loaded_stress_scenario.price_changes == stress_scenario.price_changes
    assert loaded_stress_scenario.description == stress_scenario.description


def test_save_and_load_all_stress_scenarios(
    stress_scenario_repo: SQLiteStressScenarioRepository,
):
    stress_scenarios = [
        StressScenario(
            name="Market Crash",
            price_changes={"AAPL": -0.1, "MSFT": -0.2},
            description="A sudden market crash scenario.",
        ),
        StressScenario(
            name="Interest Rate Hike",
            price_changes={"AAPL": -0.05, "MSFT": -0.1},
            description="An interest rate hike scenario.",
        ),
    ]
    stress_scenario_repo.save_all(stress_scenarios)

    loaded_stress_scenarios = stress_scenario_repo.get_all()

    assert len(loaded_stress_scenarios) == len(stress_scenarios)
    for scenario in stress_scenarios:
        loaded_scenario = stress_scenario_repo.get(scenario.name)
        assert loaded_scenario is not None
        assert loaded_scenario.name == scenario.name
        assert loaded_scenario.price_changes == scenario.price_changes
        assert loaded_scenario.description == scenario.description


def test_load_nonexistent_stress_scenario(
    stress_scenario_repo: SQLiteStressScenarioRepository,
):
    assert stress_scenario_repo.get("NONEXISTENT") is None
