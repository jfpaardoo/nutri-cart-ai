from pydantic import BaseModel, Field
from typing import List, Optional


class GeneratePlanRequest(BaseModel):
    supermarket: str = Field(default="mercadona", description="Supermarket identifier ('mercadona' or 'aldi')")
    postal_code: str = Field(default="46001", description="5-digit Spanish Postal Code")
    target_calories: int = Field(default=2000, ge=1000, le=5000, description="Daily calorie goal in kcal")
    target_protein: int = Field(default=140, ge=30, le=350, description="Daily protein goal in grams")
    target_carbs: int = Field(default=200, ge=20, le=600, description="Daily carbohydrates goal in grams")
    target_fat: int = Field(default=65, ge=15, le=200, description="Daily fat goal in grams")
    days_count: int = Field(default=7, ge=1, le=14, description="Number of days to plan")
    meals_per_day: int = Field(default=3, ge=2, le=5, description="Number of meals per day")
    dietary_preferences: Optional[List[str]] = Field(default_factory=list, description="Dietary filters")


class ProductSearchResponse(BaseModel):
    query: str
    supermarket: str
    postal_code: str
    total_found: int
    products: List[dict]
