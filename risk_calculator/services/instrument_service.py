from risk_calculator.domain.instrument import Instrument, InstrumentType
from risk_calculator.repositories.protocols import InstrumentRepository


class InstrumentService:
    def __init__(self, instrument_repository: InstrumentRepository):
        self.instrument_repository = instrument_repository

    def create_instrument(
        self,
        symbol: str,
        instrument_type: InstrumentType,
        margin_rate: float,
        name: str | None = None,
    ) -> Instrument:
        instrument = Instrument(
            symbol=symbol,
            instrument_type=instrument_type,
            margin_rate=margin_rate,
            name=name,
        )
        self.instrument_repository.save(instrument)
        return instrument

    def get_instrument(self, symbol: str) -> Instrument:
        instrument = self.instrument_repository.get(symbol)
        if instrument is None:
            raise ValueError(f"Instrument with symbol '{symbol}' not found.")
        return instrument

    def list_instruments(self) -> list[Instrument]:
        return self.instrument_repository.get_all()
