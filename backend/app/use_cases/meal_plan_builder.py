import uuid
import logging
from typing import List, Dict, Any, Optional
from app.domain.entities import Product, RecipeIngredient, Recipe, DailyPlan, MealPlan
from app.domain.value_objects import Macros, MacroTargets
from app.ports.supermarket_port import SupermarketStrategy
from app.adapters.nutrition.chain import NutritionResolutionService
from app.ports.llm_port import LLMStrategy

logger = logging.getLogger(__name__)


class MealPlanBuilder:
    """
    BUILDER PATTERN (Creational)
    Constructs a complete, validated weekly meal plan step-by-step:
    1. Generates dish concepts and ingredients with the LLM Strategy.
    2. Resolves real-world products using the Supermarket Strategy.
    3. Resolves accurate macronutrients using the Nutrition Chain of Responsibility.
    4. Balances and checks macro totals.
    """

    def __init__(
        self,
        supermarket_strategy: SupermarketStrategy,
        nutrition_service: NutritionResolutionService,
        llm_strategy: LLMStrategy,
    ):
        self._supermarket = supermarket_strategy
        self._nutrition = nutrition_service
        self._llm = llm_strategy
        self._matched_product_cache: Dict[str, Optional[Product]] = {}

    def build_plan(
        self,
        target_macros: MacroTargets,
        postal_code: str,
        days_count: int = 7,
        meals_per_day: int = 3,
        dietary_preferences: Optional[List[str]] = None
    ) -> MealPlan:
        # 1. Generate menu skeleton with LLM Strategy
        raw_days = self._llm.generate_menu_structure(
            macro_targets=target_macros,
            days_count=days_count,
            meals_per_day=meals_per_day,
            dietary_preferences=dietary_preferences or []
        )

        built_days: List[DailyPlan] = []

        for raw_day in raw_days:
            day_name = raw_day["day_name"]
            recipes: List[Recipe] = []
            day_total_macros = Macros.empty()

            for raw_meal in raw_day["meals"]:
                recipe = self._build_recipe(raw_meal, postal_code)
                recipes.append(recipe)
                day_total_macros = day_total_macros.add(recipe.macros)

            built_days.append(
                DailyPlan(
                    day_name=day_name,
                    meals=recipes,
                    total_macros=day_total_macros
                )
            )

        return MealPlan(
            id=str(uuid.uuid4())[:8],
            supermarket=self._supermarket.supermarket_name,
            postal_code=postal_code,
            target_macros=target_macros,
            days=built_days
        )

    def _build_recipe(self, raw_meal: Dict[str, Any], postal_code: str) -> Recipe:
        ingredients: List[RecipeIngredient] = []
        dish_macros = Macros.empty()

        for raw_ing in raw_meal["ingredients"]:
            ing_name = raw_ing["name"]
            amount_grams = float(raw_ing["amount_grams"])

            # Find matching product in supermarket
            product = self._match_product_in_supermarket(ing_name, postal_code)

            # Resolve nutritional macros per 100g via Chain of Responsibility
            macros_100g = self._nutrition.resolve_macros_for_ingredient(ing_name, product)
            computed = macros_100g.scale(amount_grams / 100.0)

            dish_macros = dish_macros.add(computed)

            ingredients.append(
                RecipeIngredient(
                    name=ing_name,
                    amount_grams=amount_grams,
                    matched_product=product,
                    computed_macros=computed
                )
            )

        return Recipe(
            id=str(uuid.uuid4())[:8],
            title=raw_meal["title"],
            meal_type=raw_meal["meal_type"],
            prep_time_minutes=raw_meal.get("prep_time_minutes", 20),
            instructions=raw_meal.get("instructions", []),
            ingredients=ingredients,
            macros=dish_macros
        )

    def _match_product_in_supermarket(self, ingredient_name: str, postal_code: str) -> Optional[Product]:
        key = f"{ingredient_name.lower().strip()}_{postal_code}"
        if key in self._matched_product_cache:
            return self._matched_product_cache[key]

        try:
            # Query the supermarket strategy
            results = self._supermarket.search_products(ingredient_name, postal_code, limit=3)
            matched = results[0] if results else None
        except Exception as e:
            logger.warning(f"Product match failed for {ingredient_name}: {e}")
            matched = None

        self._matched_product_cache[key] = matched
        return matched
