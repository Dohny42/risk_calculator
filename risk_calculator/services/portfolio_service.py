from risk_calculator.domain.portfolio import Portfolio, Position, apply_stress_scenario
from risk_calculator.repositories.protocols import InstrumentRepository, PortfolioRepository


class PortfolioService:
    def __init__(
        self, instrument_repository: InstrumentRepository, portfolio_repository: PortfolioRepository
    ) -> None:
        self.instrument_repository = instrument_repository
        self.portfolio_repository = portfolio_repository

    def get_portfolio(self) -> Portfolio:
        return self.portfolio_repository.get()

    def add_position(self, symbol: str, quantity: float, price: float) -> Portfolio:
        instrument = self.instrument_repository.get(symbol)
        if instrument is None:
            raise ValueError(f"Instrument with symbol '{symbol}' not found.")

        position = Position(instrument=instrument, quantity=quantity, price=price)
        portfolio = self.get_portfolio()
        portfolio.add_position(position)
        self.portfolio_repository.save(portfolio)
        return portfolio

    def apply_stress(self, price_changes: dict[str, float]) -> Portfolio:
        portfolio = self.get_portfolio()
        return apply_stress_scenario(portfolio, price_changes)
