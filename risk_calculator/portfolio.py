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
        self.positions: list[Position] = []

    def add_position(self, position: Position):
        if position.quantity == 0:
            raise ValueError("Quantity cannot be zero")
        if position.price < 0:
            raise ValueError("Price cannot be negative")
        self.positions.append(position)

    def total_value(self) -> float:
        """Calculate the total value of the portfolio."""
        return sum(position.value() for position in self.positions)

    def __str__(self) -> str:
        if not self.positions:
            return "Empty portfolio"
        lines = [str(pos) for pos in self.positions]
        lines.append(f"Total value: {self.total_value():.2f}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Portfolio(positions={self.positions!r})"
