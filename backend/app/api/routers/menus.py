from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import GeneratePlanRequest
from app.domain.value_objects import MacroTargets
from app.adapters.supermarkets.base import SupermarketFactory
from app.adapters.nutrition.chain import NutritionResolutionService
from app.adapters.llm.strategy import LLMFactory
from app.use_cases.meal_plan_builder import MealPlanBuilder
from app.use_cases.basket_optimizer import BasketOptimizerUseCase
from app.adapters.repositories.meal_plan_repo import MealPlanRepository

router = APIRouter(prefix="/api/menus", tags=["Menus & Nutrition"])

# Shared singleton dependencies
_nutrition_service = NutritionResolutionService()
_meal_plan_repo = MealPlanRepository()
_basket_optimizer = BasketOptimizerUseCase()


@router.post("/generate")
def generate_weekly_menu(req: GeneratePlanRequest):
    """
    BUILDER & STRATEGY PATTERNS:
    1. Instantiates SupermarketStrategy via SupermarketFactory.
    2. Uses MealPlanBuilder with Chain of Responsibility nutrition resolution.
    3. Optimizes the shopping basket and calculates ticket cost.
    4. Persists the plan in MealPlanRepository.
    """
    try:
        supermarket_strategy = SupermarketFactory.get_strategy(req.supermarket)
        llm_strategy = LLMFactory.create_strategy()

        builder = MealPlanBuilder(
            supermarket_strategy=supermarket_strategy,
            nutrition_service=_nutrition_service,
            llm_strategy=llm_strategy,
        )

        target_macros = MacroTargets(
            target_calories=req.target_calories,
            target_protein=req.target_protein,
            target_carbs=req.target_carbs,
            target_fat=req.target_fat
        )

        meal_plan = builder.build_plan(
            target_macros=target_macros,
            postal_code=req.postal_code,
            days_count=req.days_count,
            meals_per_day=req.meals_per_day,
            dietary_preferences=req.dietary_preferences
        )

        # Save to repository
        _meal_plan_repo.save(meal_plan)

        # Compute shopping basket
        basket = _basket_optimizer.execute(meal_plan)

        return {
            "meal_plan": meal_plan.to_dict(),
            "shopping_basket": basket.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate menu: {str(e)}")


@router.get("/{plan_id}")
def get_meal_plan(plan_id: str):
    """Retrieves an existing meal plan by ID."""
    plan = _meal_plan_repo.get_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan.to_dict()


@router.get("/{plan_id}/basket")
def get_plan_basket(plan_id: str):
    """Retrieves or recalculates the shopping basket for a meal plan."""
    plan = _meal_plan_repo.get_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    basket = _basket_optimizer.execute(plan)
    return basket.to_dict()
