from typing import List, Optional
from app.ports.supermarket_port import SupermarketStrategy
from app.domain.entities import Product, Category
from app.adapters.supermarkets.aldi.adapter import AldiProductAdapter


class AldiStrategy(SupermarketStrategy):
    """
    STRATEGY PATTERN (Concrete Implementation)
    Connects to the Aldi España product catalog.
    """

    def __init__(self):
        self.adapter = AldiProductAdapter()
        # Seed Aldi catalog for staple goods with real Spanish Aldi brands (Gut Bio, El Mercado, Milsani)
        self._seed_data = [
            {
                "id": "aldi-101",
                "name": "Pechuga de pollo entera El Mercado",
                "price": 3.89,
                "reference_price": 7.78,
                "reference_format": "kg",
                "package_format": "Bandeja 500g",
                "image_url": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=300",
                "ean": "8430001001015",
                "brand": "El Mercado de Aldi",
                "net_weight_grams": 500.0,
                "category_id": "aldi-carniceria"
            },
            {
                "id": "aldi-102",
                "name": "Huevos camperos Clase M/L El Mercado",
                "price": 2.45,
                "reference_price": 0.20,
                "reference_format": "ud",
                "package_format": "Docena",
                "image_url": "https://images.unsplash.com/photo-1516448620398-c5f44bf9f441?w=300",
                "ean": "8430001001022",
                "brand": "El Mercado de Aldi",
                "net_weight_grams": 650.0,
                "category_id": "aldi-huevos"
            },
            {
                "id": "aldi-103",
                "name": "Arroz redondo La Tabla de Aldi",
                "price": 1.29,
                "reference_price": 1.29,
                "reference_format": "kg",
                "package_format": "Paquete 1kg",
                "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300",
                "ean": "8430001001039",
                "brand": "La Tabla",
                "net_weight_grams": 1000.0,
                "category_id": "aldi-despensa"
            },
            {
                "id": "aldi-104",
                "name": "Copos de avena suaves Gut Bio",
                "price": 0.99,
                "reference_price": 1.98,
                "reference_format": "kg",
                "package_format": "Bolsa 500g",
                "image_url": "https://images.unsplash.com/photo-1584947986877-3e81313e6488?w=300",
                "ean": "8430001001046",
                "brand": "Gut Bio",
                "net_weight_grams": 500.0,
                "category_id": "aldi-bio"
            },
            {
                "id": "aldi-105",
                "name": "Aceite de oliva virgen extra Olisone",
                "price": 7.95,
                "reference_price": 7.95,
                "reference_format": "l",
                "package_format": "Botella 1L",
                "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=300",
                "ean": "8430001001053",
                "brand": "Olisone",
                "net_weight_grams": 916.0,
                "category_id": "aldi-despensa"
            },
            {
                "id": "aldi-106",
                "name": "Lomos de salmón fresco sin espinas El Mercado",
                "price": 5.49,
                "reference_price": 18.30,
                "reference_format": "kg",
                "package_format": "Bandeja 300g",
                "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=300",
                "ean": "8430001001060",
                "brand": "El Mercado de Aldi",
                "net_weight_grams": 300.0,
                "category_id": "aldi-pescaderia"
            },
            {
                "id": "aldi-107",
                "name": "Brócoli fresco El Mercado",
                "price": 1.15,
                "reference_price": 2.30,
                "reference_format": "kg",
                "package_format": "Pieza 500g",
                "image_url": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=300",
                "ean": "8430001001077",
                "brand": "El Mercado de Aldi",
                "net_weight_grams": 500.0,
                "category_id": "aldi-verduras"
            },
            {
                "id": "aldi-108",
                "name": "Yogur natural cremoso Milsani",
                "price": 1.35,
                "reference_price": 2.70,
                "reference_format": "kg",
                "package_format": "Pack 4x125g",
                "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=300",
                "ean": "8430001001084",
                "brand": "Milsani",
                "net_weight_grams": 500.0,
                "category_id": "aldi-lacteos"
            }
        ]

    @property
    def supermarket_name(self) -> str:
        return "aldi"

    def search_products(self, query: str, postal_code: str, limit: int = 20) -> List[Product]:
        q = query.lower().strip()
        results = [
            self.adapter.to_product(raw)
            for raw in self._seed_data
            if q in raw["name"].lower() or q in raw["brand"].lower()
        ]
        return results[:limit]

    def get_categories(self, postal_code: str) -> List[Category]:
        return [
            Category(id="aldi-carniceria", name="Carnicería y Aves", supermarket="aldi"),
            Category(id="aldi-pescaderia", name="Pescadería", supermarket="aldi"),
            Category(id="aldi-verduras", name="Frutas y Verduras", supermarket="aldi"),
            Category(id="aldi-despensa", name="Despensa y Aceites", supermarket="aldi"),
            Category(id="aldi-lacteos", name="Lácteos y Huevos", supermarket="aldi"),
            Category(id="aldi-bio", name="Productos Bio Gut Bio", supermarket="aldi"),
        ]

    def get_product_by_id(self, product_id: str, postal_code: str) -> Optional[Product]:
        for raw in self._seed_data:
            if raw["id"] == product_id:
                return self.adapter.to_product(raw)
        return None

    def get_products_by_category(self, category_id: str, postal_code: str) -> List[Product]:
        return [
            self.adapter.to_product(raw)
            for raw in self._seed_data
            if raw.get("category_id") == category_id
        ]
