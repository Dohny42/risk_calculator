from fastapi import APIRouter, Depends, HTTPException

from risk_calculator.api.dependencies import get_portfolio_service
from risk_calculator.api.schemas import (
    PortfolioResponse,
    PositionCreateRequest,
    PositionResponse,
)
from risk_calculator.domain.instrument import Instrument
from risk_calculator.domain.portfolio import Portfolio, Position
from risk_calculator.services.portfolio_service import PortfolioService

router = APIRouter()


def to_portfolio_response(portfolio: Portfolio) -> PortfolioResponse:
    positions = [
        PositionResponse(
            symbol=p.instrument.symbol,
            quantity=p.quantity,
            price=p.price,
            instrument_type=p.instrument.instrument_type,
            value=p.value(),
            margin=p.margin(),
        )
        for p in portfolio.positions.values()
    ]
    return PortfolioResponse(
        positions=positions,
        total_value=portfolio.total_value(),
        total_margin=portfolio.total_margin(),
    )


@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio(
    service: PortfolioService = Depends(get_portfolio_service),
):
    portfolio = service.get_portfolio()
    return to_portfolio_response(portfolio)


@router.post("/positions", response_model=PortfolioResponse)
def add_position(
    position: PositionCreateRequest,
    service: PortfolioService = Depends(get_portfolio_service),
):
    try:
        instrument = Instrument(
            symbol=position.symbol,
            instrument_type=position.instrument_type,
            margin_rate=0,  # Replace with actual margin rate if available
            name="",  # Replace with actual name if available
        )
        pos = Position(
            instrument=instrument,
            quantity=position.quantity,
            price=position.price,
        )
        portfolio = service.add_position(pos)
        return to_portfolio_response(portfolio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
