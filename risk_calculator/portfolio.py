from dataclasses import dataclass
from typing import Literal

InstrumentType = Literal["equity", "future"]

MARGIN_RATES = {
    "equity": 0.30,
    "future": 0.10,
}


@dataclass
class Position:
    symbol: str
    quantity: float
    price: float
    instrument_type: InstrumentType = "equity"

    def value(self) -> float:
        """Current value of this position."""
        return self.quantity * self.price

    def margin(self) -> float:
        """Calculate the margin requirement for this position."""
        rate = MARGIN_RATES[self.instrument_type]
        return abs(self.value()) * rate

    def __str__(self) -> str:
        return (
            f"{self.symbol} ({self.instrument_type}): "
            f"{self.quantity} @ {self.price:.2f} = {self.value():.2f} "
            f"| margin: {self.margin():.2f}"
        )


class Portfolio:
    def __init__(self):
        self.positions: dict[str, Position] = {}

    def add_position(self, position: Position):
        if position.quantity == 0:
            raise ValueError("Quantity cannot be zero")
        if position.price < 0:
            raise ValueError("Price cannot be negative")
        if position.instrument_type not in MARGIN_RATES:
            raise ValueError(f"Invalid instrument type: {position.instrument_type}")

        # if the position already exists, update the quantity and price
        if position.symbol in self.positions:
            existing_position = self.positions[position.symbol]
            if existing_position.instrument_type != position.instrument_type:
                raise ValueError("Cannot merge positions with different instrument types")

            existing_position.quantity += position.quantity
            existing_position.price = position.price

            if existing_position.quantity == 0:
                del self.positions[position.symbol]
        else:
            self.positions[position.symbol] = position

    def get_position(self, symbol: str) -> Position | None:
        return self.positions.get(symbol)

    def update_price(self, symbol: str, price: float):
        if symbol not in self.positions:
            raise ValueError(f"Position for {symbol} does not exist")
        if price < 0:
            raise ValueError("Price cannot be negative")

        position = self.positions[symbol]
        position.price = price

    def remove_position(self, symbol: str):
        if symbol not in self.positions:
            raise ValueError(f"Position for {symbol} does not exist")
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
        raise ValueError(f"Unknown symbols in price changes: {unknown_symbols}")

    stressed = Portfolio()

    for symbol, change in price_changes.items():
        position = portfolio.positions[symbol]
        new_price = position.price * (1.0 + change)
        new_price = max(new_price, 0.0)
        stressed.add_position(
            Position(
                symbol=symbol,
                quantity=position.quantity,
                price=new_price,
                instrument_type=position.instrument_type,
            )
        )

    return stressed
