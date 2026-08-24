from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from risk_calculator.domain.exceptions import (
    DomainError,
    InvalidPositionError,
    InvalidStressScenarioError,
    StressScenarioAlreadyExistsError,
    UnknownInstrumentError,
    UnknownStressScenarioError,
    UnknownSymbolsError,
)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UnknownInstrumentError)
    async def unknown_instrument_handler(request: Request, exc: UnknownInstrumentError):
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(UnknownSymbolsError)
    async def unknown_symbols_handler(request: Request, exc: UnknownSymbolsError):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(InvalidPositionError)
    async def invalid_position_handler(request: Request, exc: InvalidPositionError):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(InvalidStressScenarioError)
    async def invalid_stress_scenario_handler(request: Request, exc: InvalidStressScenarioError):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(UnknownStressScenarioError)
    async def unknown_stress_scenario_handler(request: Request, exc: UnknownStressScenarioError):
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(StressScenarioAlreadyExistsError)
    async def stress_scenario_already_exists_handler(
        request: Request, exc: StressScenarioAlreadyExistsError
    ):
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(status_code=400, content={"detail": exc.message})
