from dataclasses import dataclass


@dataclass
class Position:
    symbol: str
    quantity: float
    price: float

    def value(self) -> float:
        """Current value of this position."""
        return self.quantity * self.price

    def __str__(self) -> str:
        return f"{self.symbol}: {self.quantity} @ {self.price:.2f} = {self.value():.2f}"


class Portfolio:
    def __init__(self):
        self.positions: dict[str, Position] = {}

    def add_position(self, position: Position):
        if position.quantity <= 0:
            raise ValueError("Quantity cannot be zero or negative")
        if position.price < 0:
            raise ValueError("Price cannot be negative")

        # if the position already exists, update the quantity and price
        if position.symbol in self.positions:
            existing_position = self.positions[position.symbol]
            existing_position.quantity += position.quantity
            existing_position.price = position.price
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

    def __str__(self) -> str:
        if not self.positions:
            return "Empty portfolio"
        lines = [str(pos) for pos in self.positions.values()]
        lines.append(f"Total value: {self.total_value():.2f}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Portfolio(positions={self.positions!r})"
