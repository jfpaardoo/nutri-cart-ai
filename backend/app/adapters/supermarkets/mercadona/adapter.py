from typing import Dict, Any, Optional
from app.domain.entities import Product, Category


class MercadonaProductAdapter:
    """
    ADAPTER PATTERN (Structural)
    Converts Mercadona's JSON DTOs to the unified domain Product and Category entities.
    """

    @staticmethod
    def to_product(data: Dict[str, Any]) -> Product:
        price_instructions = data.get("price_instructions") or {}
        
        # Parse price safely
        raw_price = price_instructions.get("unit_price") or data.get("unit_price") or "0.0"
        try:
            price = float(raw_price)
        except (ValueError, TypeError):
            price = 0.0

        raw_ref_price = price_instructions.get("reference_price") or "0.0"
        try:
            reference_price = float(raw_ref_price)
        except (ValueError, TypeError):
            reference_price = price

        ref_format = price_instructions.get("reference_format") or "ud"
        packaging = data.get("packaging") or "Unidad"
        
        # Approximate net weight if available
        net_weight_grams = None
        if ref_format.lower() in ["kg", "l"] and reference_price > 0 and price > 0:
            # e.g., price 1.5€, ref_price 3.0€/kg -> 0.5kg -> 500g
            net_weight_grams = round((price / reference_price) * 1000.0, 1)

        # Photo selection
        thumbnail = data.get("thumbnail")
        if not thumbnail and data.get("photos"):
            photos = data.get("photos", [])
            if photos and isinstance(photos, list):
                thumbnail = photos[0].get("zoom") or photos[0].get("regular")

        return Product(
            id=str(data.get("id")),
            supermarket="mercadona",
            name=data.get("display_name") or data.get("name") or "Producto sin nombre",
            price=price,
            reference_price=reference_price,
            reference_format=ref_format,
            package_format=packaging,
            image_url=thumbnail,
            ean=data.get("ean"),
            brand=data.get("brand"),
            net_weight_grams=net_weight_grams,
        )

    @staticmethod
    def to_category(data: Dict[str, Any], parent_id: Optional[str] = None) -> Category:
        subcats = []
        raw_subcats = data.get("categories") or []
        cat_id = str(data.get("id"))
        for raw in raw_subcats:
            subcats.append(MercadonaProductAdapter.to_category(raw, parent_id=cat_id))

        return Category(
            id=cat_id,
            name=data.get("name", "Sin categoría"),
            supermarket="mercadona",
            parent_id=parent_id,
            subcategories=subcats
        )
