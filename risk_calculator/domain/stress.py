from dataclasses import dataclass, field
from datetime import UTC, datetime

from risk_calculator.domain.exceptions import InvalidStressScenarioError


@dataclass
class StressScenario:
    name: str
    price_changes: dict[str, float]
    description: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name:
            raise InvalidStressScenarioError("Stress scenario name cannot be empty.")
        if not self.price_changes:
            raise InvalidStressScenarioError("Price changes cannot be empty.")
