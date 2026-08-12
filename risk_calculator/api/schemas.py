from pydantic import BaseModel, Field

from risk_calculator.domain.instrument import InstrumentType


class PositionCreateRequest(BaseModel):
    symbol: str
    quantity: float
    price: float = Field(gt=0)
    instrument_type: InstrumentType = "equity"


class StressRequest(BaseModel):
    price_changes: dict[str, float]


class PositionResponse(BaseModel):
    symbol: str
    quantity: float
    price: float
    instrument_type: str
    value: float
    margin: float


class PortfolioResponse(BaseModel):
    positions: list[PositionResponse]
    total_value: float
    total_margin: float
