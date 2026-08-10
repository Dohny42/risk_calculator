from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException

from risk_calculator.portfolio import Portfolio, Position
from risk_calculator.schemas import (
    PortfolioResponse,
    PositionCreateRequest,
    PositionResponse,
    StressRequest,
)
from risk_calculator.service import PortfolioService

app = FastAPI(title="Risk Calculator API")


def get_portfolio_service() -> PortfolioService:
    """Default dependency. In tests we will override this."""
    from risk_calculator.repository import SQLitePortfolioRepository

    repository = SQLitePortfolioRepository(db_path=Path("portfolio.db"))
    return PortfolioService(repository)


def to_portfolio_response(portfolio: Portfolio) -> PortfolioResponse:
    positions = [
        PositionResponse(
            symbol=p.symbol,
            quantity=p.quantity,
            price=p.price,
            instrument_type=p.instrument_type,
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


@app.get("/")
def root():
    return {"message": "Risk Calculator API", "docs": "/docs"}


@app.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio(
    service: PortfolioService = Depends(get_portfolio_service),
):
    portfolio = service.get_portfolio()
    return to_portfolio_response(portfolio)


@app.post("/positions", response_model=PortfolioResponse)
def add_position(
    position: PositionCreateRequest,
    service: PortfolioService = Depends(get_portfolio_service),
):
    try:
        pos = Position(
            symbol=position.symbol,
            quantity=position.quantity,
            price=position.price,
            instrument_type=position.instrument_type,
        )
        portfolio = service.add_position(pos)
        return to_portfolio_response(portfolio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/stress", response_model=PortfolioResponse)
def run_stress(
    request: StressRequest,
    service: PortfolioService = Depends(get_portfolio_service),
):
    try:
        stressed = service.apply_stress(request.price_changes)
        return to_portfolio_response(stressed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
