from contextlib import asynccontextmanager

from fastapi import FastAPI

from risk_calculator.api.exception_handlers import add_exception_handlers
from risk_calculator.api.middleware import RequestContextMiddleware
from risk_calculator.api.routes.instruments_routes import router as instruments_router
from risk_calculator.api.routes.portfolio_routes import router as portfolio_router
from risk_calculator.api.routes.snapshot_routes import router as snapshot_router
from risk_calculator.api.routes.stress_routes import router as stress_router
from risk_calculator.config import get_settings, setup_logging
from risk_calculator.repositories.sqlite.db_schema import create_schema


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema(get_settings().db_path)
    setup_logging(get_settings())
    yield


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
add_exception_handlers(app)

# routers
app.include_router(instruments_router)
app.include_router(portfolio_router)
app.include_router(stress_router)
app.include_router(snapshot_router)

# middleware
app.add_middleware(RequestContextMiddleware)


@app.get("/")
def root():
    return {"message": get_settings().app_name, "docs": "/docs"}
