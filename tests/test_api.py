from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from risk_calculator.api import app, get_portfolio_service
from risk_calculator.service import PortfolioService


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_portfolio.db"


@pytest.fixture
def test_client(temp_db_path: Path) -> Generator[TestClient]:
    # Override the dependency to use a temporary database for testing
    def override_get_portfolio_service() -> PortfolioService:
        return PortfolioService(db_path=temp_db_path)

    app.dependency_overrides[get_portfolio_service] = override_get_portfolio_service
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def default_state_client(test_client: TestClient) -> TestClient:
    """
    Fixture to set up a default state portfolio with some positions for testing.

    Returns:
        TestClient: The test client with the default state portfolio set up.
    """

    payloads = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.0,
            "instrument_type": "equity",
        },
        {
            "symbol": "GOOGL",
            "quantity": 5,
            "price": 1000.0,
            "instrument_type": "equity",
        },
    ]
    for payload in payloads:
        test_client.post("/positions", json=payload)

    return test_client


def assert_portfolio_matches(
    actual: dict, expected_positions: list[dict], total_value: float, total_margin: float
):
    assert sorted(actual["positions"], key=lambda p: p["symbol"]) == sorted(
        expected_positions, key=lambda p: p["symbol"]
    )
    assert actual["total_value"] == total_value
    assert actual["total_margin"] == total_margin


def test_get_empty_portfolio(test_client: TestClient):
    response = test_client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["positions"] == []
    assert data["total_value"] == 0.0
    assert data["total_margin"] == 0.0


def test_add_position(test_client: TestClient):
    payload = {
        "symbol": "AAPL",
        "quantity": 10,
        "price": 150.0,
        "instrument_type": "equity",
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


def test_add_position_validation_error(test_client: TestClient):
    payload = {
        "symbol": "AAPL",
        "quantity": 10,
        "price": -50.0,
    }
    response = test_client.post("/positions", json=payload)
    assert response.status_code == 422  # FastAPI validation error


def test_get_portfolio_with_positions(default_state_client: TestClient):
    test_client = default_state_client
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


def test_stress_test(default_state_client: TestClient):
    test_client = default_state_client
    payload = {
        "price_changes": {
            "AAPL": -0.1,
            "GOOGL": 0.1,
        }
    }
    response = test_client.post("/stress", json=payload)
    assert response.status_code == 200
    data = response.json()

    expected_positions = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 135.0,  # 150 * 0.9
            "instrument_type": "equity",
            "value": 1350.0,
            "margin": 405.0,  # 30% of 1350
        },
        {
            "symbol": "GOOGL",
            "quantity": 5,
            "price": 1100.0,  # 1000 * 1.1
            "instrument_type": "equity",
            "value": 5500.0,
            "margin": 1650.0,
        },
    ]

    assert_portfolio_matches(
        actual=data,
        expected_positions=expected_positions,
        total_value=6850.0,
        total_margin=2055.0,
    )


def test_stress_test_invalid_symbol(default_state_client: TestClient):
    test_client = default_state_client
    payload = {
        "price_changes": {
            "INVALID": -0.1,
        }
    }
    response = test_client.post("/stress", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Unknown symbols in price changes: ['INVALID']" in data["detail"]
