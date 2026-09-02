from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from risk_calculator.domain.portfolio import Portfolio


@dataclass
class PortfolioSnapshot:
    id: str
    timestamp: datetime
    positions: list[PositionSnapshot]
    total_value: float
    total_margin: float
    source: str = "live"
    label: str | None = None


@dataclass
class PositionSnapshot:
    symbol: str
    quantity: float
    price: float
    instrument_type: str
    margin_rate: float
    value: float
    margin: float


def create_portfolio_snapshot(
    portfolio: Portfolio, source: str = "live", label: str | None = None
) -> PortfolioSnapshot:
    positions_snapshot = [
        PositionSnapshot(
            symbol=position.instrument.symbol,
            quantity=position.quantity,
            price=position.price,
            instrument_type=position.instrument.instrument_type,
            margin_rate=position.instrument.margin_rate,
            value=position.value(),
            margin=position.margin(),
        )
        for position in portfolio.positions.values()
    ]

    return PortfolioSnapshot(
        id=str(uuid4()),
        timestamp=datetime.now(UTC),
        positions=positions_snapshot,
        total_value=portfolio.total_value(),
        total_margin=portfolio.total_margin(),
        source=source,
        label=label,
    )
