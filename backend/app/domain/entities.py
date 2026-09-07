from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.domain.value_objects import Macros, MacroTargets


@dataclass
class Product:
    """Unified domain model representing a supermarket item."""
    id: str
    supermarket: str               # e.g., 'mercadona', 'aldi'
    name: str
    price: float                   # Current unit price (EUR)
    reference_price: float         # Price per reference unit (e.g. per kg or L)
    reference_format: str          # 'kg', 'l', 'ud', 'g'
    package_format: str            # e.g., 'Bandeja', 'Bolsa', 'Botella'
    image_url: Optional[str] = None
    ean: Optional[str] = None      # Barcode / EAN code
    category_id: Optional[str] = None
    brand: Optional[str] = None
    net_weight_grams: Optional[float] = None
    macros_100g: Optional[Macros] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "supermarket": self.supermarket,
            "name": self.name,
            "price": self.price,
            "reference_price": self.reference_price,
            "reference_format": self.reference_format,
            "package_format": self.package_format,
            "image_url": self.image_url,
            "ean": self.ean,
            "brand": self.brand,
            "net_weight_grams": self.net_weight_grams,
            "macros_100g": self.macros_100g.to_dict() if self.macros_100g else None
        }


@dataclass
class Category:
    """Supermarket category classification."""
    id: str
    name: str
    supermarket: str
    parent_id: Optional[str] = None
    subcategories: List[Category] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "supermarket": self.supermarket,
            "parent_id": self.parent_id,
            "subcategories": [sub.to_dict() for sub in self.subcategories]
        }


@dataclass
class RecipeIngredient:
    """An ingredient needed for a recipe, tied to a target weight."""
    name: str
    amount_grams: float
    matched_product: Optional[Product] = None
    computed_macros: Optional[Macros] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "amount_grams": self.amount_grams,
            "matched_product": self.matched_product.to_dict() if self.matched_product else None,
            "computed_macros": self.computed_macros.to_dict() if self.computed_macros else None
        }


@dataclass
class Recipe:
    """Single dish recipe with preparation steps and total macros."""
    id: str
    title: str
    meal_type: str                 # 'Desayuno', 'Comida', 'Cena', 'Snack'
    prep_time_minutes: int
    instructions: List[str]
    ingredients: List[RecipeIngredient]
    macros: Macros

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "meal_type": self.meal_type,
            "prep_time_minutes": self.prep_time_minutes,
            "instructions": self.instructions,
            "ingredients": [i.to_dict() for i in self.ingredients],
            "macros": self.macros.to_dict()
        }


@dataclass
class DailyPlan:
    """Daily schedule of meals."""
    day_name: str                  # 'Lunes', 'Martes', ...
    meals: List[Recipe]
    total_macros: Macros

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day_name": self.day_name,
            "meals": [m.to_dict() for m in self.meals],
            "total_macros": self.total_macros.to_dict()
        }


@dataclass
class MealPlan:
    """Full weekly meal plan."""
    id: str
    supermarket: str
    postal_code: str
    target_macros: MacroTargets
    days: List[DailyPlan]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "supermarket": self.supermarket,
            "postal_code": self.postal_code,
            "target_macros": self.target_macros.to_dict(),
            "days": [d.to_dict() for d in self.days],
            "created_at": self.created_at.isoformat()
        }


@dataclass
class BasketItem:
    """An item to purchase in the supermarket, consolidated for the week."""
    product: Product
    grams_needed: float
    units_to_buy: int
    total_cost: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product": self.product.to_dict(),
            "grams_needed": round(self.grams_needed, 1),
            "units_to_buy": self.units_to_buy,
            "total_cost": round(self.total_cost, 2)
        }


@dataclass
class ShoppingBasket:
    """Consolidated shopping basket for the entire week."""
    supermarket: str
    postal_code: str
    items: List[BasketItem]
    total_cost: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supermarket": self.supermarket,
            "postal_code": self.postal_code,
            "items": [item.to_dict() for item in self.items],
            "total_cost": round(self.total_cost, 2),
            "items_count": len(self.items)
        }
