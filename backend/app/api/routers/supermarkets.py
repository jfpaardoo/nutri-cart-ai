from fastapi import APIRouter, Query, HTTPException
from app.adapters.supermarkets.base import SupermarketFactory
from app.domain.exceptions import SupermarketPlannerException

router = APIRouter(prefix="/api", tags=["Supermarkets"])


@router.get("/supermarkets")
def list_supermarkets():
    """Returns available supermarket providers supported via Strategy Pattern."""
    return {
        "available_supermarkets": [
            {
                "id": "mercadona",
                "name": "Mercadona",
                "status": "active",
                "features": ["Live REST API", "Official photos", "Stock by Postal Code", "Unit and reference pricing"]
            },
            {
                "id": "aldi",
                "name": "Aldi",
                "status": "active",
                "features": ["Catalog Strategy", "Gut Bio / El Mercado brands", "Unit and reference pricing"]
            }
        ],
        "default": "mercadona"
    }


@router.get("/products/search")
def search_products(
    q: str = Query(..., description="Ingredient or product name to search"),
    supermarket: str = Query("mercadona", description="Supermarket identifier ('mercadona' or 'aldi')"),
    postal_code: str = Query("46001", description="5-digit postal code"),
    limit: int = Query(15, ge=1, le=50)
):
    """
    STRATEGY PATTERN IN ACTION:
    Delegates search directly to the configured SupermarketStrategy.
    """
    try:
        strategy = SupermarketFactory.get_strategy(supermarket)
        products = strategy.search_products(q, postal_code=postal_code, limit=limit)
        return {
            "query": q,
            "supermarket": strategy.supermarket_name,
            "postal_code": postal_code,
            "total_found": len(products),
            "products": [p.to_dict() for p in products]
        }
    except SupermarketPlannerException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error querying {supermarket}: {str(e)}")


@router.get("/categories")
def get_categories(
    supermarket: str = Query("mercadona"),
    postal_code: str = Query("46001")
):
    """Retrieves product categories for the chosen supermarket strategy."""
    try:
        strategy = SupermarketFactory.get_strategy(supermarket)
        categories = strategy.get_categories(postal_code=postal_code)
        return {
            "supermarket": strategy.supermarket_name,
            "postal_code": postal_code,
            "categories": [c.to_dict() for c in categories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
