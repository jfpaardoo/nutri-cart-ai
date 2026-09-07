import pytest
from unittest.mock import MagicMock
from app.ports.supermarket_port import SupermarketStrategy
from app.adapters.supermarkets.base import SupermarketFactory, CachedSupermarketProxy
from app.adapters.supermarkets.mercadona.adapter import MercadonaProductAdapter
from app.adapters.supermarkets.aldi.adapter import AldiProductAdapter
from app.domain.entities import Product, Category, Recipe, RecipeIngredient, DailyPlan, MealPlan
from app.domain.value_objects import Macros, MacroTargets
from app.domain.exceptions import SupermarketNotSupportedException
from app.adapters.nutrition.chain import NutritionResolutionService, LocalCacheNutritionHandler, WholeFoodsReferenceHandler
from app.adapters.llm.strategy import RuleBasedLLMStrategy
from app.use_cases.meal_plan_builder import MealPlanBuilder
from app.use_cases.basket_optimizer import BasketOptimizerUseCase


class DummyStrategy(SupermarketStrategy):
    """Mock strategy for isolation testing."""
    def __init__(self):
        self.call_count = 0

    @property
    def supermarket_name(self) -> str:
        return "dummy"

    def search_products(self, query: str, postal_code: str, limit: int = 20):
        self.call_count += 1
        return [
            Product(
                id="dummy-1",
                supermarket="dummy",
                name=f"{query} Dummy",
                price=2.50,
                reference_price=2.50,
                reference_format="kg",
                package_format="Pack",
                net_weight_grams=500.0
            )
        ]

    def get_categories(self, postal_code: str):
        return [Category(id="cat-1", name="Test Category", supermarket="dummy")]

    def get_product_by_id(self, product_id: str, postal_code: str):
        return None

    def get_products_by_category(self, category_id: str, postal_code: str):
        return []


def test_strategy_and_factory_pattern():
    """Validates that SupermarketFactory instantiates conforming SupermarketStrategy instances."""
    mercadona = SupermarketFactory.get_strategy("mercadona")
    assert isinstance(mercadona, SupermarketStrategy)
    assert mercadona.supermarket_name == "mercadona"

    aldi = SupermarketFactory.get_strategy("aldi")
    assert isinstance(aldi, SupermarketStrategy)
    assert aldi.supermarket_name == "aldi"

    with pytest.raises(SupermarketNotSupportedException):
        SupermarketFactory.get_strategy("carrefour_unregistered")


def test_proxy_cache_pattern():
    """Validates that CachedSupermarketProxy caches queries and avoids redundant calls."""
    raw_dummy = DummyStrategy()
    proxy = CachedSupermarketProxy(raw_dummy, ttl_seconds=60)

    # First call: hits underlying strategy
    res1 = proxy.search_products("arroz", "46001")
    assert raw_dummy.call_count == 1
    assert len(res1) == 1

    # Second identical call: served from cache!
    res2 = proxy.search_products("arroz", "46001")
    assert raw_dummy.call_count == 1  # No new call
    assert res1[0].name == res2[0].name


def test_adapter_pattern_normalization():
    """Validates that different supermarket payload structures adapt into uniform Product models."""
    mercadona_raw = {
        "id": "12345",
        "display_name": "Pechuga de pollo Hacendado",
        "price_instructions": {
            "unit_price": "3.80",
            "reference_price": "7.60",
            "reference_format": "kg"
        },
        "packaging": "Bandeja",
        "ean": "8480000123456",
        "brand": "Hacendado"
    }
    p_merc = MercadonaProductAdapter.to_product(mercadona_raw)
    assert p_merc.id == "12345"
    assert p_merc.supermarket == "mercadona"
    assert p_merc.price == 3.80
    assert p_merc.reference_format == "kg"
    assert p_merc.net_weight_grams == 500.0  # 3.8 / 7.6 * 1000 = 500g

    aldi_raw = {
        "id": "aldi-99",
        "name": "Pechuga de pavo Gut Bio",
        "price": 2.99,
        "reference_price": 9.96,
        "reference_format": "kg",
        "package_format": "Bandeja 300g",
        "net_weight_grams": 300.0,
        "brand": "Gut Bio"
    }
    p_aldi = AldiProductAdapter.to_product(aldi_raw)
    assert p_aldi.id == "aldi-99"
    assert p_aldi.supermarket == "aldi"
    assert p_aldi.price == 2.99
    assert p_aldi.net_weight_grams == 300.0


def test_chain_of_responsibility_nutrition():
    """Validates the multi-link Chain of Responsibility for nutrition resolution."""
    service = NutritionResolutionService()

    # Link 2 (WholeFoodsReferenceHandler) handles standard foods
    chicken_macros = service.resolve_macros_for_ingredient("Pechuga de pollo")
    assert chicken_macros.protein >= 30.0
    assert chicken_macros.calories > 150.0

    # Test that subsequent lookup is stored in Link 1 (LocalCache)
    cached_macros = service.resolve_macros_for_ingredient("Pechuga de pollo")
    assert cached_macros == chicken_macros

    # Link 4 (Fallback) handles completely unknown foods safely
    unknown_macros = service.resolve_macros_for_ingredient("Hierba mágica del monte desconocido")
    assert unknown_macros.calories > 0


def test_builder_pattern_meal_plan():
    """Validates the MealPlanBuilder constructing a full week with real nutrition."""
    dummy_strategy = DummyStrategy()
    nutrition = NutritionResolutionService()
    llm = RuleBasedLLMStrategy()

    builder = MealPlanBuilder(
        supermarket_strategy=dummy_strategy,
        nutrition_service=nutrition,
        llm_strategy=llm
    )

    targets = MacroTargets(
        target_calories=2000,
        target_protein=140,
        target_carbs=200,
        target_fat=65
    )

    plan = builder.build_plan(
        target_macros=targets,
        postal_code="46001",
        days_count=7,
        meals_per_day=3
    )

    assert plan.supermarket == "dummy"
    assert len(plan.days) == 7
    for day in plan.days:
        assert len(day.meals) == 3
        assert day.total_macros.calories > 1000


def test_basket_optimizer():
    """Validates that BasketOptimizerUseCase computes weekly totals and unit quantities."""
    dummy_product = Product(
        id="prod-1",
        supermarket="dummy",
        name="Arroz",
        price=1.25,
        reference_price=1.25,
        reference_format="kg",
        package_format="Paquete 1kg",
        net_weight_grams=1000.0
    )

    ing1 = RecipeIngredient(name="Arroz", amount_grams=400.0, matched_product=dummy_product)
    ing2 = RecipeIngredient(name="Arroz", amount_grams=800.0, matched_product=dummy_product)

    recipe1 = Recipe(
        id="r1", title="Arroz almuerzo", meal_type="Comida", prep_time_minutes=20,
        instructions=["Cocer"], ingredients=[ing1], macros=Macros(300, 5, 60, 1)
    )
    recipe2 = Recipe(
        id="r2", title="Arroz cena", meal_type="Cena", prep_time_minutes=20,
        instructions=["Cocer"], ingredients=[ing2], macros=Macros(600, 10, 120, 2)
    )

    day1 = DailyPlan(day_name="Lunes", meals=[recipe1], total_macros=recipe1.macros)
    day2 = DailyPlan(day_name="Martes", meals=[recipe2], total_macros=recipe2.macros)

    meal_plan = MealPlan(
        id="plan-1",
        supermarket="dummy",
        postal_code="46001",
        target_macros=MacroTargets(2000, 140, 200, 65),
        days=[day1, day2]
    )

    optimizer = BasketOptimizerUseCase()
    basket = optimizer.execute(meal_plan)

    # 400g + 800g = 1200g needed. Since package is 1000g, 2 packs are required!
    assert len(basket.items) == 1
    item = basket.items[0]
    assert item.grams_needed == 1200.0
    assert item.units_to_buy == 2
    assert item.total_cost == 2.50  # 2 * 1.25
    assert basket.total_cost == 2.50
