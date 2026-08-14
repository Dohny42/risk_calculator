from typing import Protocol

from risk_calculator.domain.instrument import Instrument
from risk_calculator.domain.portfolio import Portfolio


class PortfolioRepository(Protocol):
    def get(self) -> Portfolio: ...

    def save(self, portfolio: Portfolio) -> None: ...


class InstrumentRepository(Protocol):
    def get(self, symbol: str) -> Instrument | None: ...

    def get_all(self) -> list[Instrument]: ...

    def save(self, instrument: Instrument) -> None: ...

    def save_all(self, instruments: list[Instrument]) -> None: ...
