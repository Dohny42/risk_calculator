from pathlib import Path

from risk_calculator.portfolio import Portfolio, Position, apply_stress_scenario
from risk_calculator.storage import load_portfolio, save_portfolio


class PortfolioService:
    def __init__(self, db_path: Path = Path("portfolio.db")):
        self.db_path = Path(db_path)

    def get_portfolio(self) -> Portfolio:
        return load_portfolio(self.db_path)

    def save(self, portfolio: Portfolio) -> None:
        save_portfolio(portfolio, self.db_path)

    def add_position(self, position: Position) -> Portfolio:
        portfolio = self.get_portfolio()
        portfolio.add_position(position)
        self.save(portfolio)
        return portfolio

    def apply_stress(self, price_changes: dict[str, float]) -> Portfolio:
        portfolio = self.get_portfolio()
        return apply_stress_scenario(portfolio, price_changes)
