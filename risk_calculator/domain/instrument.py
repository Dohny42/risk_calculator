from dataclasses import dataclass
from typing import Literal

InstrumentType = Literal["equity", "future"]


@dataclass
class Instrument:
    symbol: str
    instrument_type: InstrumentType
    margin_rate: float
    name: str | None = None

    def __post_init__(self) -> None:
        self.symbol = self.symbol.upper()
        if self.margin_rate < 0 or self.margin_rate > 1:
            raise ValueError("margin_rate must be between 0 and 1")
