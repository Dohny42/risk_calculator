from risk_calculator.portfolio import Portfolio, Position, apply_stress_scenario
from risk_calculator.repository import PortfolioRepository


class PortfolioService:
    def __init__(self, repository: PortfolioRepository):
        self.repository = repository

    def get_portfolio(self) -> Portfolio:
        return self.repository.get()

    def save(self, portfolio: Portfolio) -> None:
        self.repository.save(portfolio)

    def add_position(self, position: Position) -> Portfolio:
        portfolio = self.get_portfolio()
        portfolio.add_position(position)
        self.save(portfolio)
        return portfolio

    def apply_stress(self, price_changes: dict[str, float]) -> Portfolio:
        portfolio = self.get_portfolio()
        return apply_stress_scenario(portfolio, price_changes)
