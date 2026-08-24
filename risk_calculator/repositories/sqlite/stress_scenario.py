import json
import sqlite3
from datetime import datetime
from pathlib import Path

from risk_calculator.domain.stress import StressScenario
from risk_calculator.repositories.protocols import StressScenarioRepository


class SQLiteStressScenarioRepository(StressScenarioRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get(self, name: str) -> StressScenario | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT name, price_changes, description, created_at FROM stress_scenarios WHERE name = ?",
                (name,),
            ).fetchone()
            if row:
                return StressScenario(
                    name=row[0],
                    price_changes=json.loads(row[1]),
                    description=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                )
            return None

    def get_all(self) -> list[StressScenario]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT name, price_changes, description, created_at FROM stress_scenarios"
            ).fetchall()
            return [
                StressScenario(
                    name=row[0],
                    price_changes=json.loads(row[1]),
                    description=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                )
                for row in rows
            ]

    def save(self, stress_scenario: StressScenario) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stress_scenarios (name, price_changes, description, created_at) VALUES (?, ?, ?, ?)",
                (
                    stress_scenario.name,
                    json.dumps(stress_scenario.price_changes),
                    stress_scenario.description,
                    stress_scenario.created_at.isoformat(),
                ),
            )
            conn.commit()

    def save_all(self, stress_scenarios: list[StressScenario]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for stress_scenario in stress_scenarios:
                cursor.execute(
                    "INSERT INTO stress_scenarios (name, price_changes, description, created_at) VALUES (?, ?, ?, ?)",
                    (
                        stress_scenario.name,
                        json.dumps(stress_scenario.price_changes),
                        stress_scenario.description,
                        stress_scenario.created_at.isoformat(),
                    ),
                )
            conn.commit()

    def update(self, stress_scenario: StressScenario) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE stress_scenarios SET price_changes = ?, description = ? WHERE name = ?",
                (
                    json.dumps(stress_scenario.price_changes),
                    stress_scenario.description,
                    stress_scenario.name,
                ),
            )
            conn.commit()
