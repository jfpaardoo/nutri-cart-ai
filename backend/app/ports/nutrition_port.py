from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from app.domain.value_objects import Macros
from app.domain.entities import Product


class NutritionHandler(ABC):
    """
    CHAIN OF RESPONSIBILITY PATTERN (Behavioral)
    Base link in the chain for resolving nutrition facts (macros per 100g).
    Each link either resolves the macros or delegates to the next link in the chain.
    """

    def __init__(self, next_handler: Optional[NutritionHandler] = None):
        self._next_handler = next_handler

    def set_next(self, handler: NutritionHandler) -> NutritionHandler:
        self._next_handler = handler
        return handler

    def resolve_macros(self, ingredient_name: str, product: Optional[Product] = None) -> Optional[Macros]:
        macros = self._handle(ingredient_name, product)
        if macros is not None:
            return macros
        if self._next_handler is not None:
            return self._next_handler.resolve_macros(ingredient_name, product)
        return None

    @abstractmethod
    def _handle(self, ingredient_name: str, product: Optional[Product] = None) -> Optional[Macros]:
        """Specific resolution logic for this chain link."""
        pass
