from risk_calculator.portfolio import Portfolio, Position
from risk_calculator.storage import load_portfolio, save_portfolio


def test_save_and_load_portfolio(tmp_path):
    # Create a sample portfolio
    portfolio = Portfolio()
    portfolio.add_position(Position("AAPL", 10, 150.0))
    portfolio.add_position(Position("MSFT", 5, 300.0))

    # Define the database path
    db_path = tmp_path / "portfolio.db"

    # Save the portfolio to the database
    save_portfolio(portfolio, db_path)

    # Load the portfolio from the database
    loaded_portfolio = load_portfolio(db_path)

    # Check that the loaded portfolio matches the original
    assert len(loaded_portfolio.positions) == 2
    assert loaded_portfolio.total_value() == portfolio.total_value()


def test_load_empty_portfolio(tmp_path):
    # Define the database path
    db_path = tmp_path / "portfolio.db"

    # Load the portfolio from the database (should be empty)
    loaded_portfolio = load_portfolio(db_path)

    # Check that the loaded portfolio is empty
    assert len(loaded_portfolio.positions) == 0
    assert loaded_portfolio.total_value() == 0.0


def test_overwrite_existing_portfolio(tmp_path):
    # Create a sample portfolio and save it
    portfolio1 = Portfolio()
    portfolio1.add_position(Position("AAPL", 10, 150.0))
    db_path = tmp_path / "portfolio.db"
    save_portfolio(portfolio1, db_path)

    # Create a new portfolio and save it (should overwrite the existing one)
    portfolio2 = Portfolio()
    portfolio2.add_position(Position("MSFT", 5, 300.0))
    save_portfolio(portfolio2, db_path)

    # Load the portfolio from the database
    loaded_portfolio = load_portfolio(db_path)

    # Check that the loaded portfolio matches the second one
    assert len(loaded_portfolio.positions) == 1
    assert loaded_portfolio.get_position("AAPL") is None
    assert loaded_portfolio.get_position("MSFT") is not None
    assert loaded_portfolio.total_value() == portfolio2.total_value()
