from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from risk_calculator.api.routes.portfolio import router as portfolio_router
from risk_calculator.repositories.sqlite.db_schema import create_schema

app = FastAPI(title="Risk Calculator API")
app.include_router(portfolio_router)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema(Path("portfolio.db"))
    yield


app = FastAPI(title="Risk Calculator API", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Risk Calculator API", "docs": "/docs"}
