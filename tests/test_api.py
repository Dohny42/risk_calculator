from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from risk_calculator.api.app import app
from risk_calculator.api.dependencies import (
    get_instrument_service,
    get_portfolio_service,
    get_stress_scenario_service,
)
from risk_calculator.repositories.sqlite.db_schema import create_schema
from risk_calculator.repositories.sqlite.instrument import SQLiteInstrumentRepository
from risk_calculator.repositories.sqlite.portfolio import SQLitePortfolioRepository
from risk_calculator.repositories.sqlite.stress_scenario import SQLiteStressScenarioRepository
from risk_calculator.services.instrument_service import InstrumentService
from risk_calculator.services.portfolio_service import PortfolioService
from risk_calculator.services.stress_service import StressScenarioService


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "portfolio.db"
    create_schema(db_path)
    return db_path


@pytest.fixture
def test_client(temp_db_path: Path) -> Generator[TestClient]:
    # Override the dependencies to use a temporary database for testing
    def override_get_instrument_service() -> InstrumentService:
        instrument_repository = SQLiteInstrumentRepository(db_path=temp_db_path)
        return InstrumentService(instrument_repository)

    def override_get_portfolio_service() -> PortfolioService:
        instrument_repository = SQLiteInstrumentRepository(db_path=temp_db_path)
        portfolio_repository = SQLitePortfolioRepository(db_path=temp_db_path)
        return PortfolioService(instrument_repository, portfolio_repository)

    def override_get_stress_scenario_service() -> StressScenarioService:
        stress_scenario_repository = SQLiteStressScenarioRepository(db_path=temp_db_path)
        return StressScenarioService(stress_scenario_repository)

    app.dependency_overrides[get_instrument_service] = override_get_instrument_service
    app.dependency_overrides[get_portfolio_service] = override_get_portfolio_service
    app.dependency_overrides[get_stress_scenario_service] = override_get_stress_scenario_service
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def create_instrument(test_client: TestClient):
    def _create(
        symbol: str = "AAPL",
        instrument_type: str = "equity",
        margin_rate: float = 0.30,
        name: str | None = None,
    ) -> dict:
        payload = {
            "symbol": symbol,
            "instrument_type": instrument_type,
            "margin_rate": margin_rate,
            "name": name,
        }
        response = test_client.post("/instruments", json=payload)
        assert response.status_code == 200
        return response.json()

    return _create


@pytest.fixture
def create_position(test_client: TestClient):
    def _create(
        symbol: str = "AAPL",
        quantity: float = 10.0,
        price: float = 150.0,
    ) -> dict:
        payload = {
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
        }
        response = test_client.post("/positions", json=payload)
        assert response.status_code == 200
        return response.json()

    return _create


@pytest.fixture
def default_portfolio(create_instrument, create_position) -> None:
    create_instrument(symbol="AAPL", instrument_type="equity", margin_rate=0.30, name="Apple Inc.")
    create_instrument(
        symbol="GOOGL", instrument_type="equity", margin_rate=0.30, name="Alphabet Inc."
    )

    create_position(symbol="AAPL", quantity=10, price=150.0)
    create_position(symbol="GOOGL", quantity=5, price=1000.0)


def assert_portfolio_matches(
    actual: dict, expected_positions: list[dict], total_value: float, total_margin: float
):
    assert sorted(actual["positions"], key=lambda p: p["symbol"]) == sorted(
        expected_positions, key=lambda p: p["symbol"]
    )
    assert actual["total_value"] == total_value
    assert actual["total_margin"] == total_margin


def test_root_endpoint(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Risk Calculator API"
    assert data["docs"] == "/docs"


def test_create_instrument(test_client: TestClient):
    payload = {
        "symbol": "AAPL",
        "instrument_type": "equity",
        "margin_rate": 0.30,
        "name": "Apple Inc.",
    }
    response = test_client.post("/instruments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["instrument_type"] == "equity"
    assert data["margin_rate"] == 0.30
    assert data["name"] == "Apple Inc."


def test_create_instrument_validation_error(test_client: TestClient):
    payload = {
        "symbol": "AAPL",
        "instrument_type": "equity",
        "margin_rate": -0.30,  # Invalid margin rate
        "name": "Apple Inc.",
    }
    response = test_client.post("/instruments", json=payload)
    assert response.status_code == 422  # FastAPI validation error


def test_get_instrument_valid(test_client: TestClient, create_instrument):
    create_instrument(symbol="AAPL")
    response = test_client.get("/instruments/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["instrument_type"] == "equity"
    assert data["margin_rate"] == 0.30


def test_get_instrument_not_found(test_client: TestClient):
    response = test_client.get("/instruments/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert "Instrument with symbol 'INVALID' not found." in data["detail"]


def test_list_instruments_empty(test_client: TestClient):
    response = test_client.get("/instruments")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_list_instruments(test_client: TestClient, create_instrument):
    create_instrument(symbol="AAPL")
    create_instrument(symbol="GOOGL")
    response = test_client.get("/instruments")
    assert response.status_code == 200
    data = response.json()
    symbols = [instrument["symbol"] for instrument in data]
    assert "AAPL" in symbols
    assert "GOOGL" in symbols


def test_get_empty_portfolio(test_client: TestClient):
    response = test_client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["positions"] == []
    assert data["total_value"] == 0.0
    assert data["total_margin"] == 0.0


def test_add_position_valid(test_client: TestClient, create_instrument):
    create_instrument(symbol="AAPL")
    payload = {
        "symbol": "AAPL",
        "quantity": 10,
        "price": 150.0,
    }
    response = test_client.post("/positions", json=payload)
    assert response.status_code == 200
    data = response.json()

    expected_positions = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.0,
            "instrument_type": "equity",
            "value": 1500.0,
            "margin": 450.0,  # 30% of 1500
        }
    ]

    assert_portfolio_matches(
        actual=data,
        expected_positions=expected_positions,
        total_value=1500.0,
        total_margin=450.0,
    )


def test_add_position_validation_error(test_client: TestClient, create_instrument):
    create_instrument(symbol="AAPL")
    payload = {
        "symbol": "AAPL",
        "quantity": 10,
        "price": -50.0,
    }
    response = test_client.post("/positions", json=payload)
    assert response.status_code == 422  # FastAPI validation error


def test_get_portfolio_with_positions(test_client: TestClient, default_portfolio):
    response = test_client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()

    expected_positions = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.0,
            "instrument_type": "equity",
            "value": 1500.0,
            "margin": 450.0,  # 30% of 1500
        },
        {
            "symbol": "GOOGL",
            "quantity": 5,
            "price": 1000.0,
            "instrument_type": "equity",
            "value": 5000.0,
            "margin": 1500.0,  # 30% of 5000
        },
    ]

    assert_portfolio_matches(
        actual=data,
        expected_positions=expected_positions,
        total_value=6500.0,
        total_margin=1950.0,
    )


def test_post_and_get_stress_scenario(
    test_client: TestClient,
):
    stress_scenario_payload = {
        "name": "Market Crash",
        "price_changes": {
            "AAPL": -0.2,
            "GOOGL": -0.15,
        },
        "description": "A sudden and severe market downturn.",
    }

    response = test_client.post("/stress-scenarios", json=stress_scenario_payload)
    assert response.status_code == 200
    created_scenario = response.json()

    assert created_scenario["name"] == "Market Crash"
    assert created_scenario["price_changes"] == {"AAPL": -0.2, "GOOGL": -0.15}
    assert created_scenario["description"] == "A sudden and severe market downturn."

    response = test_client.get("/stress-scenarios/Market Crash")
    assert response.status_code == 200
    retrieved_scenario = response.json()

    assert retrieved_scenario == created_scenario


def test_apply_stress_scenario(test_client: TestClient, default_portfolio):
    stress_scenario_payload = {
        "name": "Market Crash",
        "price_changes": {
            "AAPL": -0.2,
            "GOOGL": -0.15,
        },
        "description": "A sudden and severe market downturn.",
    }

    response = test_client.post("/stress-scenarios", json=stress_scenario_payload)
    assert response.status_code == 200

    response = test_client.post("/stress-scenarios/Market Crash/apply")
    assert response.status_code == 200
    stressed_portfolio = response.json()

    expected_positions = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 120.0,  # 150 * (1 - 0.2)
            "instrument_type": "equity",
            "value": 1200.0,
            "margin": 360.0,  # 30% of 1200
        },
        {
            "symbol": "GOOGL",
            "quantity": 5,
            "price": 850.0,  # 1000 * (1 - 0.15)
            "instrument_type": "equity",
            "value": 4250.0,
            "margin": 1275.0,  # 30% of 4250
        },
    ]

    assert_portfolio_matches(
        actual=stressed_portfolio,
        expected_positions=expected_positions,
        total_value=5450.0,
        total_margin=1635.0,
    )


def test_apply_nonexistent_stress_scenario(test_client: TestClient, default_portfolio):
    response = test_client.post("/stress-scenarios/Nonexistent Scenario/apply")
    assert response.status_code == 404
    data = response.json()
    assert "Stress scenario with name 'Nonexistent Scenario' not found." in data["detail"]


def test_get_stress_scenarios_empty(test_client: TestClient):
    response = test_client.get("/stress-scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_stress_scenarios(test_client: TestClient):
    stress_scenario_payload_1 = {
        "name": "Market Crash",
        "price_changes": {
            "AAPL": -0.2,
            "GOOGL": -0.15,
        },
        "description": "A sudden and severe market downturn.",
    }

    stress_scenario_payload_2 = {
        "name": "Tech Boom",
        "price_changes": {
            "AAPL": 0.3,
            "GOOGL": 0.25,
        },
        "description": "A rapid increase in tech stock prices.",
    }

    test_client.post("/stress-scenarios", json=stress_scenario_payload_1)
    test_client.post("/stress-scenarios", json=stress_scenario_payload_2)

    response = test_client.get("/stress-scenarios")
    assert response.status_code == 200
    data = response.json()

    scenario_names = [scenario["name"] for scenario in data]
    assert "Market Crash" in scenario_names
    assert "Tech Boom" in scenario_names


def test_get_stress_scenario_not_found(test_client: TestClient):
    response = test_client.get("/stress-scenarios/Nonexistent Scenario")
    assert response.status_code == 404
    data = response.json()
    assert "Stress scenario with name 'Nonexistent Scenario' not found." in data["detail"]


def test_add_stress_scenario_validation_error(test_client: TestClient):
    stress_scenario_payload = {
        "name": "Invalid Scenario",
        "price_changes": {
            "AAPL": -1.5,  # Invalid price change (less than -1)
            "GOOGL": 0.25,
        },
        "description": "An invalid stress scenario.",
    }

    response = test_client.post("/stress-scenarios", json=stress_scenario_payload)
    assert response.status_code == 422  # FastAPI validation error


def test_add_stress_scenario_duplicate_name(test_client: TestClient):
    stress_scenario_payload = {
        "name": "Duplicate Scenario",
        "price_changes": {
            "AAPL": -0.2,
            "GOOGL": -0.15,
        },
        "description": "A stress scenario with a duplicate name.",
    }

    response = test_client.post("/stress-scenarios", json=stress_scenario_payload)
    assert response.status_code == 200

    response = test_client.post("/stress-scenarios", json=stress_scenario_payload)
    assert response.status_code == 409
    data = response.json()
    assert "Stress scenario with name 'Duplicate Scenario' already exists." in data["detail"]


def test_update_stress_scenario(test_client: TestClient):
    stress_scenario_payload = {
        "name": "Update Scenario",
        "price_changes": {
            "AAPL": -0.2,
            "GOOGL": -0.15,
        },
        "description": "A stress scenario to be updated.",
    }

    response = test_client.post("/stress-scenarios", json=stress_scenario_payload)
    assert response.status_code == 200

    update_payload = {
        "price_changes": {
            "AAPL": -0.1,
            "GOOGL": -0.05,
        },
        "description": "Updated description.",
    }

    response = test_client.put("/stress-scenarios/Update Scenario", json=update_payload)
    assert response.status_code == 200
    updated_scenario = response.json()

    assert updated_scenario["name"] == "Update Scenario"
    assert updated_scenario["price_changes"] == {"AAPL": -0.1, "GOOGL": -0.05}
    assert updated_scenario["description"] == "Updated description."


def test_update_stress_scenario_not_found(test_client: TestClient):
    update_payload = {
        "price_changes": {
            "AAPL": -0.1,
            "GOOGL": -0.05,
        },
        "description": "Updated description.",
    }

    response = test_client.put("/stress-scenarios/Nonexistent Scenario", json=update_payload)
    assert response.status_code == 404
    data = response.json()
    assert "Stress scenario with name 'Nonexistent Scenario' not found." in data["detail"]


def test_update_stress_scenario_validation_error(test_client: TestClient):
    stress_scenario_payload = {
        "name": "Validation Scenario",
        "price_changes": {
            "AAPL": -0.2,
            "GOOGL": -0.15,
        },
        "description": "A stress scenario to test validation.",
    }

    response = test_client.post("/stress-scenarios", json=stress_scenario_payload)
    assert response.status_code == 200

    update_payload = {
        "price_changes": {
            "AAPL": -1.5,  # Invalid price change (less than -1)
            "GOOGL": -0.05,
        },
        "description": "Updated description with invalid price change.",
    }

    response = test_client.put("/stress-scenarios/Validation Scenario", json=update_payload)
    assert response.status_code == 422  # FastAPI validation error
