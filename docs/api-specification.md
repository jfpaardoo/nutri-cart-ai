# Especificación de la API REST (FastAPI)

La API corre por defecto en `http://127.0.0.1:8000`. Incluye documentación interactiva OpenAPI en `/docs` (Swagger UI) y `/redoc`.

---

## 1. Endpoints de Supermercados

### GET /api/supermarkets
Devuelve la lista de estrategias de supermercados soportadas en el sistema.

**Respuesta (200 OK):**
```json
{
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
```

---

### GET /api/products/search
Ejecuta una búsqueda de productos invocando la estrategia del supermercado elegido.

**Parámetros Query:**
- `q` (string, requerido): Texto a buscar (ej: `pollo`, `arroz`, `avena`).
- `supermarket` (string, opcional): `mercadona` (default) o `aldi`.
- `postal_code` (string, opcional): Código postal español de 5 dígitos (default: `46001`).
- `limit` (int, opcional): Máximo de productos a retornar (default: 15).

**Respuesta (200 OK):**
```json
{
  "query": "pollo",
  "supermarket": "mercadona",
  "postal_code": "46001",
  "total_found": 12,
  "products": [
    {
      "id": "12501",
      "supermarket": "mercadona",
      "name": "Pechuga de pollo entera Hacendado",
      "price": 3.95,
      "reference_price": 7.90,
      "reference_format": "kg",
      "package_format": "Bandeja",
      "image_url": "https://prod-mercadona.imgix.net/images/...",
      "ean": "8480000125012",
      "brand": "Hacendado",
      "net_weight_grams": 500.0,
      "macros_100g": null
    }
  ]
}
```

---

## 2. Endpoints de Planificación Nutricional y Cesta

### POST /api/menus/generate
Genera un plan semanal completo adaptado a los macros objetivo, vinculando cada ingrediente a productos reales del supermercado y calculando la cesta de la compra.

**Cuerpo de la Petición (JSON):**
```json
{
  "supermarket": "mercadona",
  "postal_code": "46001",
  "target_calories": 2100,
  "target_protein": 145,
  "target_carbs": 210,
  "target_fat": 65,
  "days_count": 7,
  "meals_per_day": 3,
  "dietary_preferences": ["mediterranea"]
}
```

**Respuesta (200 OK):**
Devuelve el objeto `meal_plan` con cada día, raciones en gramos, pasos e instrucciones, y el objeto `shopping_basket` con unidades a comprar y coste total en euros.

---

### GET /api/menus/{id}
Consulta un menú previamente generado mediante su identificador único.

### GET /api/menus/{id}/basket
Devuelve el desglose de compra para el plan indicado.
