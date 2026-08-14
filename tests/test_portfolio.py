import pytest

from risk_calculator.domain.exceptions import (
    InvalidPositionError,
    UnknownInstrumentError,
    UnknownPositionError,
    UnknownSymbolsError,
)
from risk_calculator.domain.instrument import Instrument
from risk_calculator.domain.portfolio import Portfolio, Position, apply_stress_scenario


@pytest.fixture
def instruments_dict() -> dict[str, Instrument]:
    return {
        "AAPL": Instrument("AAPL", "equity", 0.3, "Apple Inc."),
        "MSFT": Instrument("MSFT", "equity", 0.3, "Microsoft Corp."),
    }


def test_position_value(instruments_dict: dict[str, Instrument]):
    pos = Position(instruments_dict["AAPL"], 10, 150.0)
    assert pos.value() == 1500.0


def test_empty_portfolio():
    portfolio = Portfolio()
    assert portfolio.total_value() == 0.0
    assert portfolio.positions == {}


def test_add_positions_and_total(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["MSFT"], 5, 300.0))

    assert len(portfolio.positions) == 2
    assert portfolio.total_value() == 3000.0


def test_cannot_add_zero_quantity(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    with pytest.raises(InvalidPositionError, match="Quantity cannot be zero"):
        portfolio.add_position(Position(instruments_dict["AAPL"], 0, 150.0))


def test_cannot_add_negative_price(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    with pytest.raises(InvalidPositionError, match="Price cannot be negative"):
        portfolio.add_position(Position(instruments_dict["AAPL"], 10, -50.0))


def test_add_duplicate_position(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["AAPL"], 5, 155.0))

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.quantity == 15
    assert pos.price == 155.0
    assert portfolio.total_value() == 2325.0  # 15 * 155.0


def test_get_nonexistent_position():
    portfolio = Portfolio()
    pos = portfolio.get_position("GOOG")
    assert pos is None


def test_remove_position_positive(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.remove_position("AAPL")

    assert len(portfolio.positions) == 0
    assert portfolio.get_position("AAPL") is None


def test_remove_position_negative():
    portfolio = Portfolio()
    with pytest.raises(UnknownPositionError, match="Position for symbol 'AAPL' not found"):
        portfolio.remove_position("AAPL")


def test_total_value_after_removal(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["MSFT"], 5, 300.0))
    portfolio.remove_position("AAPL")

    assert portfolio.total_value() == 1500.0


def test_update_price_existing_positive(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.update_price("AAPL", 160.0)

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.price == 160.0
    assert pos.value() == 1600.0
    assert portfolio.total_value() == 1600.0


def test_update_price_existing_negative(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    with pytest.raises(InvalidPositionError, match="Price cannot be negative"):
        portfolio.update_price("AAPL", -10.0)


def test_update_price_nonexistent():
    portfolio = Portfolio()
    with pytest.raises(UnknownPositionError, match="Position for symbol 'AAPL' not found"):
        portfolio.update_price("AAPL", 160.0)


def test_add_duplicate_position_with_negative_price(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    with pytest.raises(InvalidPositionError, match="Price cannot be negative"):
        portfolio.add_position(Position(instruments_dict["AAPL"], 5, -155.0))


def test_add_duplicate_position_with_zero_quantity(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    with pytest.raises(InvalidPositionError, match="Quantity cannot be zero"):
        portfolio.add_position(Position(instruments_dict["AAPL"], 0, 155.0))


def test_add_duplicate_position_negative_quantity(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["AAPL"], -5, 155.0))

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.quantity == 5
    assert pos.price == 155.0
    assert pos.value() == 775.0


def test_add_duplicate_position_negative_quantity_to_zero(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["AAPL"], -10, 155.0))

    pos = portfolio.get_position("AAPL")
    assert pos is None
    assert len(portfolio.positions) == 0


# ========== Tests for instrument type validation ==========

# ========== Tests for instrument type validation ==========


def test_add_position_with_valid_instrument_type(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.instrument.instrument_type == "equity"


def test_add_position_duplicate_with_same_instrument_type(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["AAPL"], 5, 155.0))

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.quantity == 15
    assert pos.price == 155.0
    assert pos.instrument.instrument_type == "equity"


def test_add_position_duplicate_with_different_instrument_type(
    instruments_dict: dict[str, Instrument],
):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))

    same_symbol_different_type = Instrument("AAPL", "future", 0.1, "AAPL Future")
    with pytest.raises(
        InvalidPositionError, match="Cannot merge positions with different instrument types"
    ):
        portfolio.add_position(Position(same_symbol_different_type, 5, 155.0))


# ========= Tests for margin calculation ==========


def test_margin_calculation_equity(instruments_dict: dict[str, Instrument]):
    pos = Position(instruments_dict["AAPL"], 10, 150.0)
    expected_margin = abs(pos.value()) * instruments_dict["AAPL"].margin_rate
    assert pos.margin() == expected_margin


def test_margin_calculation_future(instruments_dict: dict[str, Instrument]):
    pos = Position(instruments_dict["AAPL"], 5, 2000.0)
    expected_margin = abs(pos.value()) * instruments_dict["AAPL"].margin_rate
    assert pos.margin() == expected_margin


def test_total_margin_calculation(instruments_dict: dict[str, Instrument]):
    portfolio = Portfolio()
    portfolio.add_position(Position(instruments_dict["AAPL"], 10, 150.0))
    portfolio.add_position(Position(instruments_dict["MSFT"], 5, 2000.0))

    expected_total_margin = (
        abs(10 * 150.0) * instruments_dict["AAPL"].margin_rate
        + abs(5 * 2000.0) * instruments_dict["MSFT"].margin_rate
    )
    assert portfolio.total_margin() == expected_total_margin


def test_margin_calculation_negative_quantity(instruments_dict: dict[str, Instrument]):
    pos = Position(instruments_dict["AAPL"], -10, 150.0)
    expected_margin = abs(pos.value()) * instruments_dict["AAPL"].margin_rate
    assert pos.margin() == expected_margin


# ========= Tests for applying stress scenario ==========


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
