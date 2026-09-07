from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class Macros:
    """Represents macronutrients and calorie density."""
    calories: float       # kcal
    protein: float        # grams
    carbs: float          # grams
    fat: float            # grams
    fiber: float = 0.0    # grams

    def __post_init__(self):
        if self.calories < 0 or self.protein < 0 or self.carbs < 0 or self.fat < 0:
            raise ValueError("Macronutrients and calories cannot be negative values.")

    def scale(self, factor: float) -> Macros:
        """Returns new scaled macros by a factor (e.g. amount_grams / 100)."""
        return Macros(
            calories=round(self.calories * factor, 1),
            protein=round(self.protein * factor, 1),
            carbs=round(self.carbs * factor, 1),
            fat=round(self.fat * factor, 1),
            fiber=round(self.fiber * factor, 1),
        )

    def add(self, other: Macros) -> Macros:
        """Returns the sum of two macro sets."""
        return Macros(
            calories=round(self.calories + other.calories, 1),
            protein=round(self.protein + other.protein, 1),
            carbs=round(self.carbs + other.carbs, 1),
            fat=round(self.fat + other.fat, 1),
            fiber=round(self.fiber + other.fiber, 1),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "fiber": self.fiber,
        }

    @classmethod
    def empty(cls) -> Macros:
        return cls(calories=0.0, protein=0.0, carbs=0.0, fat=0.0, fiber=0.0)


@dataclass(frozen=True)
class MacroTargets:
    """Target daily nutrition goals for the user."""
    target_calories: int
    target_protein: int
    target_carbs: int
    target_fat: int
    tolerance_pct: float = 0.08  # Default 8% tolerance window

    def is_within_tolerance(self, current: Macros) -> bool:
        low_cal = self.target_calories * (1.0 - self.tolerance_pct)
        high_cal = self.target_calories * (1.0 + self.tolerance_pct)
        return low_cal <= current.calories <= high_cal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_calories": self.target_calories,
            "target_protein": self.target_protein,
            "target_carbs": self.target_carbs,
            "target_fat": self.target_fat,
            "tolerance_pct": self.tolerance_pct,
        }
