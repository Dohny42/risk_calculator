from fastapi import APIRouter, Depends, HTTPException

from risk_calculator.api.dependencies import get_portfolio_service
from risk_calculator.api.schemas import (
    PortfolioResponse,
    PositionCreateRequest,
    PositionResponse,
)
from risk_calculator.domain.portfolio import Portfolio
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
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    try:
        portfolio = portfolio_service.add_position(
            position.symbol, position.quantity, position.price
        )
        return to_portfolio_response(portfolio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
