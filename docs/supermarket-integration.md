# Guía de Integración de Nuevos Supermercados (Open/Closed Principle)

Gracias al patrón **Strategy** y al **Factory Method**, añadir un nuevo supermercado (ej: *Carrefour*, *Día*, *Eroski*, *Lidl*) **no requiere modificar ningún caso de uso existente**.

---

## Pasos para Integrar un Nuevo Supermercado

### Paso 1: Crear el Adaptador (`adapter.py`)
Crea una carpeta en `backend/app/adapters/supermarkets/<nuevo_super>/adapter.py` y define la función que transforma el JSON o HTML del supermercado a la entidad `Product` de dominio:

```python
from app.domain.entities import Product

class CarrefourProductAdapter:
    @staticmethod
    def to_product(raw_data: dict) -> Product:
        return Product(
            id=str(raw_data["sku"]),
            supermarket="carrefour",
            name=raw_data["title"],
            price=float(raw_data["price"]),
            reference_price=float(raw_data.get("price_per_unit", raw_data["price"])),
            reference_format=raw_data.get("unit", "kg"),
            package_format=raw_data.get("format", "1 ud"),
            image_url=raw_data.get("image_url"),
            ean=raw_data.get("ean")
        )
```

---

### Paso 2: Crear la Estrategia (`strategy.py`)
Implementa la interfaz abstracta `SupermarketStrategy`:

```python
from typing import List, Optional
from app.ports.supermarket_port import SupermarketStrategy
from app.domain.entities import Product, Category
from app.adapters.supermarkets.carrefour.adapter import CarrefourProductAdapter

class CarrefourStrategy(SupermarketStrategy):
    @property
    def supermarket_name(self) -> str:
        return "carrefour"

    def search_products(self, query: str, postal_code: str, limit: int = 20) -> List[Product]:
        # Lógica HTTP contra la API o scraper de Carrefour
        ...

    def get_categories(self, postal_code: str) -> List[Category]:
        ...

    def get_product_by_id(self, product_id: str, postal_code: str) -> Optional[Product]:
        ...

    def get_products_by_category(self, category_id: str, postal_code: str) -> List[Product]:
        ...
```

---

### Paso 3: Registrar la Estrategia en la Factoría (`base.py`)
En `backend/app/adapters/supermarkets/base.py`, añade la nueva estrategia al diccionario del `SupermarketFactory`:

```python
_registry = {
    "mercadona": MercadonaStrategy,
    "aldi": AldiStrategy,
    "carrefour": CarrefourStrategy,  # <-- Nueva estrategia
}
```

O regístrala dinámicamente en tiempo de ejecución:
```python
SupermarketFactory.register_strategy("carrefour", CarrefourStrategy)
```

A partir de este momento:
- Las llamadas a `/api/products/search?supermarket=carrefour` funcionarán inmediatamente.
- Los menús podrán generarse optimizando la cesta directamente con los precios de Carrefour.
- La caché transparente `CachedSupermarketProxy` protegerá las consultas de forma automática.
