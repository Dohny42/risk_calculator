from pydantic import BaseModel, Field

from risk_calculator.domain.instrument import InstrumentType


class InstrumentCreate(BaseModel):
    symbol: str
    instrument_type: InstrumentType
    margin_rate: float = Field(ge=0, le=1)
    name: str | None = None


class InstrumentResponse(BaseModel):
    symbol: str
    instrument_type: InstrumentType
    margin_rate: float
    name: str | None = None


class PositionCreateRequest(BaseModel):
    symbol: str
    quantity: float
    price: float = Field(gt=0)


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
