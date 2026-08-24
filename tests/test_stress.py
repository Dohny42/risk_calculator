import pytest

from risk_calculator.domain.exceptions import InvalidStressScenarioError, UnknownSymbolsError
from risk_calculator.domain.instrument import Instrument
from risk_calculator.domain.portfolio import Portfolio, Position, apply_stress_scenario
from risk_calculator.domain.stress import StressScenario


@pytest.fixture
def instruments_dict() -> dict[str, Instrument]:
    return {
        "AAPL": Instrument("AAPL", "equity", 0.3, "Apple Inc."),
        "MSFT": Instrument("MSFT", "equity", 0.3, "Microsoft Corp."),
    }


def test_valid_stress_scenario():
    stress_scenario = StressScenario(
        "Market Crash",
        {"AAPL": -0.1, "MSFT": -0.2},
        "A market crash scenario with significant drops in stock prices.",
    )
    assert stress_scenario.name == "Market Crash"
    assert stress_scenario.price_changes == {"AAPL": -0.1, "MSFT": -0.2}
    assert (
        stress_scenario.description
        == "A market crash scenario with significant drops in stock prices."
    )


def test_invalid_stress_scenario():
    with pytest.raises(InvalidStressScenarioError, match="Stress scenario name cannot be empty"):
        StressScenario(
            "",
            {"AAPL": -0.1, "MSFT": -0.2},
            "A market crash scenario with significant drops in stock prices.",
        )

    with pytest.raises(InvalidStressScenarioError, match="Price changes cannot be empty"):
        StressScenario(
            "Market Crash",
            {},
            "A market crash scenario with significant drops in stock prices.",
        )


def test_apply_stress_scenario(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["MSFT"], 5, 300.0))

    stress_factors = {"AAPL": -0.1, "MSFT": -0.2}
    stressed_portfolio = apply_stress_scenario(portfolio, stress_factors)

    pos_aapl = portfolio.get_position("AAPL")
    pos_msft = portfolio.get_position("MSFT")
    stressed_pos_aapl = stressed_portfolio.get_position("AAPL")
    stressed_pos_msft = stressed_portfolio.get_position("MSFT")

    assert pos_aapl is not None
    assert pos_aapl.price == 150.0
    assert pos_msft is not None
    assert pos_msft.price == 300.0

    assert stressed_pos_aapl is not None
    assert stressed_pos_aapl.price == 135.0
    assert stressed_pos_msft is not None
    assert stressed_pos_msft.price == 240.0


def test_apply_stress_scenario_with_nonexistent_symbol(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))

    stress_factors = {"GOOG": -0.1, "MSFT": -0.2}
    with pytest.raises(
        UnknownSymbolsError, match=r"Unknown symbols in price changes: \['GOOG', 'MSFT'\]"
    ):
        _ = apply_stress_scenario(portfolio, stress_factors)

    pos_aapl = portfolio.get_position("AAPL")
    assert pos_aapl is not None
    assert pos_aapl.price == 150.0


def test_apply_stress_scenario_with_negative_price(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))

    stress_factors = {"AAPL": -2.0}
    stressed_portfolio = apply_stress_scenario(portfolio, stress_factors)
    stressed_pos_aapl = stressed_portfolio.get_position("AAPL")
    assert stressed_pos_aapl is not None
    assert stressed_pos_aapl.price == 0.0


def test_apply_stress_scenario_zero_price_change(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))

    stress_factors = {"AAPL": 0.0}
    portfolio = apply_stress_scenario(portfolio, stress_factors)

    pos_aapl = portfolio.get_position("AAPL")
    assert pos_aapl is not None
    assert pos_aapl.price == 150.0


def test_margin_calculation_with_stress_scenario(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["MSFT"], 5, 300.0))

    stress_factors = {"AAPL": -0.1, "MSFT": -0.2}
    stressed_portfolio = apply_stress_scenario(portfolio, stress_factors)

    expected_total_original_margin = (
        abs(10 * 150.0) * instruments_dict["AAPL"].margin_rate
        + abs(5 * 300.0) * instruments_dict["MSFT"].margin_rate
    )
    assert portfolio.total_margin() == expected_total_original_margin

    expected_total_stressed_margin = (
        abs(10 * 135.0) * instruments_dict["AAPL"].margin_rate
        + abs(5 * 240.0) * instruments_dict["MSFT"].margin_rate
    )
    assert stressed_portfolio.total_margin() == expected_total_stressed_margin
