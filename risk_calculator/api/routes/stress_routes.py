from fastapi import APIRouter, Depends

from risk_calculator.api.dependencies import get_portfolio_service, get_stress_scenario_service
from risk_calculator.api.routes.portfolio_routes import to_portfolio_response
from risk_calculator.api.schemas import (
    PortfolioResponse,
    StressScenarioCreateRequest,
    StressScenarioResponse,
    StressScenarioUpdateRequest,
)
from risk_calculator.domain.stress import StressScenario
from risk_calculator.services.portfolio_service import PortfolioService
from risk_calculator.services.stress_service import StressScenarioService

router = APIRouter()


def to_stress_scenario_response(stress_scenario: StressScenario) -> StressScenarioResponse:
    return StressScenarioResponse(
        name=stress_scenario.name,
        price_changes=stress_scenario.price_changes,
        description=stress_scenario.description,
    )


@router.get("/stress-scenarios", response_model=list[StressScenarioResponse])
def get_stress_scenarios(
    service: StressScenarioService = Depends(get_stress_scenario_service),
):
    stress_scenarios = service.get_all()
    return [to_stress_scenario_response(s) for s in stress_scenarios]


@router.get("/stress-scenarios/{name}", response_model=StressScenarioResponse)
def get_stress_scenario(
    name: str,
    service: StressScenarioService = Depends(get_stress_scenario_service),
):
    stress_scenario = service.get(name)
    return to_stress_scenario_response(stress_scenario)


@router.post("/stress-scenarios", response_model=StressScenarioResponse)
def add_stress_scenario(
    stress_scenario: StressScenarioCreateRequest,
    service: StressScenarioService = Depends(get_stress_scenario_service),
):
    created_scenario = service.save(
        stress_scenario.name, stress_scenario.price_changes, stress_scenario.description
    )
    return to_stress_scenario_response(created_scenario)


@router.post("/stress-scenarios/{name}/apply", response_model=PortfolioResponse)
def apply_stress_scenario(
    name: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    stress_service: StressScenarioService = Depends(get_stress_scenario_service),
):
    stressed_portfolio = stress_service.apply(name, portfolio_service.get_portfolio())
    return to_portfolio_response(stressed_portfolio)


@router.put("/stress-scenarios/{name}", response_model=StressScenarioResponse)
def update_stress_scenario(
    name: str,
    stress_scenario: StressScenarioUpdateRequest,
    service: StressScenarioService = Depends(get_stress_scenario_service),
):
    updated_scenario = service.update(
        name, stress_scenario.price_changes, stress_scenario.description
    )
    return to_stress_scenario_response(updated_scenario)
