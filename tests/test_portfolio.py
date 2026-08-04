import pytest

from risk_calculator.portfolio import Portfolio, Position


def test_position_value():
    pos = Position("AAPL", 10, 150.0)
    assert pos.value() == 1500.0


def test_empty_portfolio():
    portfolio = Portfolio()
    assert portfolio.total_value() == 0.0
    assert portfolio.positions == []


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
