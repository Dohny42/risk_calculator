from fastapi import APIRouter, Depends, HTTPException

from risk_calculator.api.dependencies import get_instrument_service
from risk_calculator.api.schemas import (
    InstrumentCreate,
    InstrumentResponse,
)
from risk_calculator.services.instrument_service import InstrumentService

router = APIRouter()


@router.post("/instruments", response_model=InstrumentResponse)
def create_instrument(
    instrument: InstrumentCreate,
    instrument_service: InstrumentService = Depends(get_instrument_service),
):
    try:
        return instrument_service.create_instrument(
            symbol=instrument.symbol,
            instrument_type=instrument.instrument_type,
            margin_rate=instrument.margin_rate,
            name=instrument.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/instruments/{symbol}", response_model=InstrumentResponse)
def get_instrument(
    symbol: str,
    instrument_service: InstrumentService = Depends(get_instrument_service),
):
    try:
        return instrument_service.get_instrument(symbol=symbol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/instruments", response_model=list[InstrumentResponse])
def list_instruments(
    instrument_service: InstrumentService = Depends(get_instrument_service),
):
    return instrument_service.list_instruments()
