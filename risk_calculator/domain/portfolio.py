from dataclasses import dataclass

from risk_calculator.domain.exceptions import (
    InvalidPositionError,
    UnknownPositionError,
    UnknownSymbolsError,
)
from risk_calculator.domain.instrument import Instrument


@dataclass
class Position:
    instrument: Instrument
    quantity: float
    price: float

    def value(self) -> float:
        """Current value of this position."""
        return self.quantity * self.price

    def margin(self) -> float:
        """Calculate the margin requirement for this position."""

        return abs(self.value()) * self.instrument.margin_rate

    def __str__(self) -> str:
        return (
            f"{self.instrument.symbol} ({self.instrument.instrument_type}): "
            f"{self.quantity} @ {self.price:.2f} = {self.value():.2f} "
            f"| margin: {self.margin():.2f}"
        )


class Portfolio:
    def __init__(self):
        self.positions: dict[str, Position] = {}

    def add_position(self, position: Position):
        if position.quantity == 0:
            raise InvalidPositionError("Quantity cannot be zero")
        if position.price < 0:
            raise InvalidPositionError("Price cannot be negative")
        # if position.instrument.instrument_type not in MARGIN_RATES:
        #     raise ValueError(f"Invalid instrument type: {position.instrument.instrument_type}")

        # if the position already exists, update the quantity and price
        if position.instrument.symbol in self.positions:
            existing_position = self.positions[position.instrument.symbol]
            if existing_position.instrument.instrument_type != position.instrument.instrument_type:
                raise InvalidPositionError("Cannot merge positions with different instrument types")

            existing_position.quantity += position.quantity
            existing_position.price = position.price

            if existing_position.quantity == 0:
                del self.positions[position.instrument.symbol]
        else:
            self.positions[position.instrument.symbol] = position

    def get_position(self, symbol: str) -> Position | None:
        return self.positions.get(symbol)

    def update_price(self, symbol: str, price: float):
        if symbol not in self.positions:
            raise UnknownPositionError(f"Position for symbol '{symbol}' not found.")
        if price < 0:
            raise InvalidPositionError("Price cannot be negative")

        position = self.positions[symbol]
        position.price = price

    def remove_position(self, symbol: str):
        if symbol not in self.positions:
            raise UnknownPositionError(f"Position for symbol '{symbol}' not found.")
        del self.positions[symbol]

    def total_value(self) -> float:
        """Calculate the total value of the portfolio."""
        return sum(position.value() for position in self.positions.values())

    def total_margin(self) -> float:
        """Calculate the total margin requirement of the portfolio."""
        return sum(position.margin() for position in self.positions.values())

    def __str__(self) -> str:
        if not self.positions:
            return "Empty portfolio"
        lines = [str(pos) for pos in self.positions.values()]
        lines.append(f"Total value: {self.total_value():.2f}")
        lines.append(f"Total margin: {self.total_margin():.2f}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Portfolio(positions={self.positions!r})"


def apply_stress_scenario(
    portfolio: Portfolio,
    price_changes: dict[str, float],
) -> Portfolio:
    """
    Apply a stress scenario and return a new portfolio.

    price_changes example: {"AAPL": -0.20, "MSFT": 0.05}
    Missing symbols are left unchanged.
    Prices are not allowed to go negative (clamped to 0).
    """
    unknown_symbols = sorted(set(price_changes.keys()) - set(portfolio.positions.keys()))
    if unknown_symbols:
        raise UnknownSymbolsError(unknown_symbols)

    stressed = Portfolio()

    for symbol, change in price_changes.items():
        position = portfolio.positions[symbol]
        new_price = position.price * (1.0 + change)
        new_price = max(new_price, 0.0)
        stressed.add_position(
            Position(
                instrument=position.instrument,
                quantity=position.quantity,
                price=new_price,
            )
        )

    return stressed
