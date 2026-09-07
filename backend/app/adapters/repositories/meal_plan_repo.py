from typing import Optional, Dict
from app.domain.entities import MealPlan


class MealPlanRepository:
    """
    REPOSITORY PATTERN (Architectural / Persistence)
    Decouples storage of MealPlans from application use cases.
    Can easily be swapped for SQLite, PostgreSQL, or DynamoDB.
    """

    def __init__(self):
        self._storage: Dict[str, MealPlan] = {}

    def save(self, meal_plan: MealPlan) -> MealPlan:
        self._storage[meal_plan.id] = meal_plan
        return meal_plan

    def get_by_id(self, plan_id: str) -> Optional[MealPlan]:
        return self._storage.get(plan_id)

    def list_all(self) -> list[MealPlan]:
        return list(self._storage.values())
