import pytest

from risk_calculator.domain.exceptions import InvalidInstrumentError
from risk_calculator.domain.instrument import Instrument


def test_instrument_valid():
    instrument = Instrument("AAPL", "equity", 0.3, "Apple Inc.")
    assert instrument.symbol == "AAPL"
    assert instrument.instrument_type == "equity"
    assert instrument.margin_rate == 0.3
    assert instrument.name == "Apple Inc."


def test_instrument_invalid_margin_rate():
    with pytest.raises(InvalidInstrumentError):
        Instrument("AAPL", "equity", -0.1, "Apple Inc.")
    with pytest.raises(InvalidInstrumentError):
        Instrument("AAPL", "equity", 1.1, "Apple Inc.")


def test_instrument_invalid_type():
    with pytest.raises(InvalidInstrumentError, match="Invalid instrument type: invalid_type"):
        _ = Instrument("AAPL", "invalid_type", 0.3, "Apple Inc.")  # ty: ignore[invalid-argument-type]
