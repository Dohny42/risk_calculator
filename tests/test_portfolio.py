import pytest

from risk_calculator.portfolio import MARGIN_RATES, Portfolio, Position, apply_stress_scenario


def test_position_value():
    pos = Position("AAPL", 10, 150.0)
    assert pos.value() == 1500.0


def test_empty_portfolio():
    portfolio = Portfolio()
    assert portfolio.total_value() == 0.0
    assert portfolio.positions == {}


def test_add_positions_and_total():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.add_position(Position("MSFT", 5, 300.0))

    assert len(portfolio.positions) == 2
    assert portfolio.total_value() == 3000.0


def test_cannot_add_zero_quantity():
    portfolio = Portfolio()
    with pytest.raises(ValueError, match="Quantity cannot be zero"):
        portfolio.add_position(Position("AAPL", 0, 150.0))


def test_cannot_add_negative_price():
    portfolio = Portfolio()
    with pytest.raises(ValueError, match="Price cannot be negative"):
        portfolio.add_position(Position("AAPL", 10, -50.0))


def test_add_duplicate_position():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.add_position(Position("AAPL", 5, 155.0))

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.quantity == 15
    assert pos.price == 155.0
    assert portfolio.total_value() == 2325.0  # 15 * 155.0


def test_get_nonexistent_position():
    portfolio = Portfolio()
    pos = portfolio.get_position("GOOG")
    assert pos is None


def test_remove_position_positive():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.remove_position("AAPL")

    assert len(portfolio.positions) == 0
    assert portfolio.get_position("AAPL") is None


def test_remove_position_negative():
    portfolio = Portfolio()
    with pytest.raises(ValueError, match="Position for AAPL does not exist"):
        portfolio.remove_position("AAPL")


def test_total_value_after_removal():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.add_position(Position("MSFT", 5, 300.0))
    portfolio.remove_position("AAPL")

    assert portfolio.total_value() == 1500.0


def test_update_price_existing_positive():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.update_price("AAPL", 160.0)

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.price == 160.0
    assert pos.value() == 1600.0
    assert portfolio.total_value() == 1600.0


def test_update_price_existing_negative():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    with pytest.raises(ValueError, match="Price cannot be negative"):
        portfolio.update_price("AAPL", -10.0)


def test_update_price_nonexistent():
    portfolio = Portfolio()
    with pytest.raises(ValueError, match="Position for AAPL does not exist"):
        portfolio.update_price("AAPL", 160.0)


def test_add_duplicate_position_with_negative_price():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    with pytest.raises(ValueError, match="Price cannot be negative"):
        portfolio.add_position(Position("AAPL", 5, -155.0))


def test_add_duplicate_position_with_zero_quantity():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    with pytest.raises(ValueError, match="Quantity cannot be zero"):
        portfolio.add_position(Position("AAPL", 0, 155.0))


def test_add_duplicate_position_negative_quantity():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.add_position(Position("AAPL", -5, 155.0))

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.quantity == 5
    assert pos.price == 155.0
    assert pos.value() == 775.0


def test_add_duplicate_position_negative_quantity_to_zero():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.add_position(Position("AAPL", -10, 155.0))

    pos = portfolio.get_position("AAPL")
    assert pos is None
    assert len(portfolio.positions) == 0


# ========== Tests for instrument type validation ==========


def test_add_position_with_valid_instrument_type():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "future"))
    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.instrument_type == "future"


def test_add_position_with_invalid_instrument_type():
    portfolio = Portfolio()
    with pytest.raises(ValueError, match="Invalid instrument type: invalid_type"):
        portfolio.add_position(Position("AAPL", 10, 150.0, "invalid_type"))  # ty: ignore[invalid-argument-type]


def test_add_position_duplicate_with_same_instrument_type():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "future"))
    portfolio.add_position(Position("AAPL", 5, 155.0, "future"))

    pos = portfolio.get_position("AAPL")
    assert pos is not None
    assert pos.quantity == 15
    assert pos.price == 155.0
    assert pos.instrument_type == "future"


def test_add_position_duplicate_with_different_instrument_type():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "future"))
    with pytest.raises(ValueError, match="Cannot merge positions with different instrument types"):
        portfolio.add_position(Position("AAPL", 5, 155.0, "equity"))


# ========= Tests for margin calculation ==========


def test_margin_calculation_equity():
    pos = Position("AAPL", 10, 150.0, "equity")
    expected_margin = abs(pos.value()) * MARGIN_RATES["equity"]
    assert pos.margin() == expected_margin


def test_margin_calculation_future():
    pos = Position("ES", 5, 2000.0, "future")
    expected_margin = abs(pos.value()) * MARGIN_RATES["future"]
    assert pos.margin() == expected_margin


def test_total_margin_calculation():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "equity"))
    portfolio.add_position(Position("ES", 5, 2000.0, "future"))

    expected_total_margin = (
        abs(10 * 150.0) * MARGIN_RATES["equity"] + abs(5 * 2000.0) * MARGIN_RATES["future"]
    )
    assert portfolio.total_margin() == expected_total_margin


def test_margin_calculation_negative_quantity():
    pos = Position("AAPL", -10, 150.0, "equity")
    expected_margin = abs(pos.value()) * MARGIN_RATES["equity"]
    assert pos.margin() == expected_margin


# ========= Tests for applying stress scenario ==========


def test_apply_stress_scenario():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "equity"))
    portfolio.add_position(Position("MSFT", 5, 300.0, "equity"))

    stress_factors = {"AAPL": -0.1, "MSFT": -0.2}  # AAPL down 10%, MSFT down 20%
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
    assert stressed_pos_aapl.price == 135.0  # 150 * (1 - 0.1)
    assert stressed_pos_msft is not None
    assert stressed_pos_msft.price == 240.0  # 300 * (1 - 0.2)


def test_apply_stress_scenario_with_nonexistent_symbol():
    # Given a portfolio and a stress scenario with nonexistent symbols
    # When the stress scenario is applied
    # Then it should raise a ValueError for the nonexistent symbols

    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "equity"))

    stress_factors = {"GOOG": -0.1, "MSFT": -0.2}  # GOOG and MSFT are not in the portfolio
    with pytest.raises(ValueError) as exc_info:
        _ = apply_stress_scenario(portfolio, stress_factors)

    msg = str(exc_info.value)
    assert "Unknown symbols in price changes" in msg
    assert "GOOG" in msg
    assert "MSFT" in msg
    assert "AAPL" not in msg

    pos_aapl = portfolio.get_position("AAPL")
    assert pos_aapl is not None
    assert pos_aapl.price == 150.0


def test_apply_stress_scenario_with_negative_price():
    # Given a portfolio and a stress scenario that would result in a negative price
    # When the stress scenario is applied
    # Then it should clamp the price to zero and not raise an error

    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "equity"))

    stress_factors = {"AAPL": -2.0}  # This would make the price negative
    stressed_portfolio = apply_stress_scenario(portfolio, stress_factors)
    stressed_pos_aapl = stressed_portfolio.get_position("AAPL")
    assert stressed_pos_aapl is not None
    assert stressed_pos_aapl.price == 0.0


def test_apply_stress_scenario_zero_price_change():
    # Given a portfolio and a stress scenario with zero price change
    # When the stress scenario is applied
    # Then the prices should remain unchanged

    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "equity"))

    stress_factors = {"AAPL": 0.0}  # No change in price
    portfolio = apply_stress_scenario(portfolio, stress_factors)

    pos_aapl = portfolio.get_position("AAPL")
    assert pos_aapl is not None
    assert pos_aapl.price == 150.0  # Price should remain unchanged


def test_margin_calculation_with_stress_scenario():
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0, "equity"))
    portfolio.add_position(Position("MSFT", 5, 300.0, "equity"))

    stress_factors = {"AAPL": -0.1, "MSFT": -0.2}  # AAPL down 10%, MSFT down 20%
    stressed_portfolio = apply_stress_scenario(portfolio, stress_factors)

    expected_total_original_margin = (
        abs(10 * 150.0) * MARGIN_RATES["equity"] + abs(5 * 300.0) * MARGIN_RATES["equity"]
    )
    assert portfolio.total_margin() == expected_total_original_margin

    expected_total_stressed_margin = (
        abs(10 * 135.0) * MARGIN_RATES["equity"] + abs(5 * 240.0) * MARGIN_RATES["equity"]
    )
    assert stressed_portfolio.total_margin() == expected_total_stressed_margin
