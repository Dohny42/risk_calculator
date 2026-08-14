from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from risk_calculator.domain.exceptions import (
    DomainError,
    InvalidPositionError,
    UnknownInstrumentError,
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

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(status_code=400, content={"detail": exc.message})
