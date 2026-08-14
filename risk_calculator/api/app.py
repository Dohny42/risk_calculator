from contextlib import asynccontextmanager

from fastapi import FastAPI

from risk_calculator.api.exception_handlers import add_exception_handlers
from risk_calculator.api.routes.instruments_routes import router as instruments_router
from risk_calculator.api.routes.portfolio_routes import router as portfolio_router
from risk_calculator.config import get_settings
from risk_calculator.repositories.sqlite.db_schema import create_schema


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema(get_settings().db_path)
    yield


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
add_exception_handlers(app)

# routers
app.include_router(instruments_router)
app.include_router(portfolio_router)


@app.get("/")
def root():
    return {"message": get_settings().app_name, "docs": "/docs"}
