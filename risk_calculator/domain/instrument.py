from dataclasses import dataclass
from typing import Literal

from risk_calculator.domain.exceptions import InvalidInstrumentError

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
            raise InvalidInstrumentError(f"Invalid margin rate: {self.margin_rate}")
        if self.instrument_type not in ("equity", "future"):
            raise InvalidInstrumentError(f"Invalid instrument type: {self.instrument_type}")
