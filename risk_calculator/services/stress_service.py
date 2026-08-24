from risk_calculator.domain.exceptions import (
    StressScenarioAlreadyExistsError,
    UnknownStressScenarioError,
)
from risk_calculator.domain.portfolio import Portfolio, apply_stress_scenario
from risk_calculator.domain.stress import StressScenario
from risk_calculator.repositories.sqlite.stress_scenario import SQLiteStressScenarioRepository


class StressScenarioService:
    def __init__(self, stress_scenario_repository: SQLiteStressScenarioRepository):
        self.stress_scenario_repository = stress_scenario_repository

    def get_all(self) -> list[StressScenario]:
        return self.stress_scenario_repository.get_all()

    def get(self, name: str) -> StressScenario:
        stress_scenario = self.stress_scenario_repository.get(name)
        if stress_scenario is None:
            raise UnknownStressScenarioError(name)
        return stress_scenario

    def save(self, name: str, price_changes: dict[str, float], description: str | None = None):
        stress_scenario = self.stress_scenario_repository.get(name)
        if stress_scenario is not None:
            raise StressScenarioAlreadyExistsError(name)

        stress_scenario = StressScenario(
            name=name,
            price_changes=price_changes,
            description=description,
        )
        self.stress_scenario_repository.save(stress_scenario)
        return stress_scenario

    def update(self, name: str, price_changes: dict[str, float], description: str | None = None):
        stress_scenario = self.stress_scenario_repository.get(name)
        if stress_scenario is None:
            raise UnknownStressScenarioError(name)

        stress_scenario.price_changes = price_changes
        stress_scenario.description = description
        self.stress_scenario_repository.update(stress_scenario)
        return stress_scenario

    def apply(self, name: str, portfolio: Portfolio) -> Portfolio:
        stress_scenario = self.get(name)
        return apply_stress_scenario(portfolio, stress_scenario.price_changes)
