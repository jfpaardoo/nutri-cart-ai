import math
from typing import Dict, List
from app.domain.entities import MealPlan, BasketItem, ShoppingBasket, Product


class BasketOptimizerUseCase:
    """
    APPLICATION USE CASE
    Consolidates ingredients across all meals and days in a MealPlan,
    calculates units to buy based on supermarket package sizes,
    and produces the optimized ShoppingBasket with total cost in EUR.
    """

    def execute(self, meal_plan: MealPlan) -> ShoppingBasket:
        # Group needed grams by matched product ID (or ingredient name if no product matched)
        aggregated: Dict[str, Dict] = {}

        for day in meal_plan.days:
            for meal in day.meals:
                for ing in meal.ingredients:
                    if ing.matched_product:
                        key = f"prod_{ing.matched_product.id}"
                        product = ing.matched_product
                    else:
                        # Fallback placeholder product
                        key = f"gen_{ing.name}"
                        product = Product(
                            id=key,
                            supermarket=meal_plan.supermarket,
                            name=ing.name,
                            price=1.50,
                            reference_price=1.50,
                            reference_format="ud",
                            package_format="1 ud",
                            net_weight_grams=250.0
                        )

                    if key not in aggregated:
                        aggregated[key] = {
                            "product": product,
                            "grams_needed": 0.0,
                        }
                    aggregated[key]["grams_needed"] += ing.amount_grams

        basket_items: List[BasketItem] = []
        total_cost = 0.0

        for key, item_data in aggregated.items():
            product: Product = item_data["product"]
            grams_needed: float = item_data["grams_needed"]

            # Calculate units to purchase
            package_weight = product.net_weight_grams or 500.0  # Default 500g assumption
            if package_weight <= 0:
                package_weight = 500.0

            units_to_buy = max(1, math.ceil(grams_needed / package_weight))
            item_cost = round(units_to_buy * product.price, 2)
            total_cost += item_cost

            basket_items.append(
                BasketItem(
                    product=product,
                    grams_needed=grams_needed,
                    units_to_buy=units_to_buy,
                    total_cost=item_cost
                )
            )

        # Sort basket items by highest total cost descending
        basket_items.sort(key=lambda x: x.total_cost, reverse=True)

        return ShoppingBasket(
            supermarket=meal_plan.supermarket,
            postal_code=meal_plan.postal_code,
            items=basket_items,
            total_cost=round(total_cost, 2)
        )
