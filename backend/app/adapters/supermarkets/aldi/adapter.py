from typing import Dict, Any, Optional
from app.domain.entities import Product, Category


class AldiProductAdapter:
    """
    ADAPTER PATTERN (Structural)
    Converts Aldi DTOs / scrapers to the unified domain Product entity.
    """

    @staticmethod
    def to_product(data: Dict[str, Any]) -> Product:
        raw_price = data.get("price") or 0.0
        try:
            price = float(raw_price)
        except (ValueError, TypeError):
            price = 0.0

        ref_price = data.get("reference_price") or price
        ref_format = data.get("reference_format") or "kg"
        packaging = data.get("package_format") or "Unidad"

        net_weight = data.get("net_weight_grams")
        if not net_weight and ref_format.lower() in ["kg", "l"] and ref_price > 0:
            net_weight = round((price / ref_price) * 1000.0, 1)

        return Product(
            id=str(data.get("id")),
            supermarket="aldi",
            name=data.get("name", "Producto Aldi"),
            price=price,
            reference_price=float(ref_price),
            reference_format=ref_format,
            package_format=packaging,
            image_url=data.get("image_url"),
            ean=data.get("ean"),
            brand=data.get("brand", "Aldi"),
            net_weight_grams=net_weight,
        )

    @staticmethod
    def to_category(data: Dict[str, Any], parent_id: Optional[str] = None) -> Category:
        subcats = [
            AldiProductAdapter.to_category(sub, parent_id=str(data.get("id")))
            for sub in data.get("subcategories", [])
        ]
        return Category(
            id=str(data.get("id")),
            name=data.get("name", "Categoría Aldi"),
            supermarket="aldi",
            parent_id=parent_id,
            subcategories=subcats
        )
