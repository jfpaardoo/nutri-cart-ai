from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.domain.value_objects import MacroTargets


class LLMStrategy(ABC):
    """
    STRATEGY PATTERN (Behavioral)
    Interface for AI engines that generate recipes and weekly plans.
    """

    @abstractmethod
    def generate_menu_structure(
        self,
        macro_targets: MacroTargets,
        days_count: int = 7,
        meals_per_day: int = 3,
        dietary_preferences: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates structured daily meal descriptions with ingredients, amounts in grams,
        and step-by-step instructions.
        """
        pass
