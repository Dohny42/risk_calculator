from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from risk_calculator.api.routes.instruments_routes import router as instruments_router
from risk_calculator.api.routes.portfolio_routes import router as portfolio_router
from risk_calculator.repositories.sqlite.db_schema import create_schema


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema(Path("portfolio.db"))
    yield


app = FastAPI(title="Risk Calculator API", lifespan=lifespan)
app.include_router(instruments_router)
app.include_router(portfolio_router)


@app.get("/")
def root():
    return {"message": "Risk Calculator API", "docs": "/docs"}
