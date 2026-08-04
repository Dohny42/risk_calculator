import pytest

from risk_calculator.portfolio import Portfolio, Position


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
    with pytest.raises(ValueError, match="Quantity cannot be zero or negative"):
        portfolio.add_position(Position("AAPL", 0, 150.0))


def test_cannot_add_negative_quantity():
    portfolio = Portfolio()
    with pytest.raises(ValueError, match="Quantity cannot be zero or negative"):
        portfolio.add_position(Position("AAPL", -5, 150.0))


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
    with pytest.raises(ValueError, match="Quantity cannot be zero or negative"):
        portfolio.add_position(Position("AAPL", 0, 155.0))
