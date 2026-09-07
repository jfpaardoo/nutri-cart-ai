# Arquitectura del Sistema (Clean Architecture & Hexagonal)

## 1. Visión General
El proyecto ComeYCuadra sigue los principios de Clean Architecture (Arquitectura Limpia) y el patrón Ports & Adapters (Hexagonal). El principio fundamental es la Regla de Dependencia: las capas internas (Dominio) no conocen los detalles de las capas externas (Infraestructura, APIs externas, frameworks web).

```
   ┌───────────────────────────────────────────────────────────────┐
   │                  INFRAESTRUCTURA / ADAPTERS                   │
   │  ┌─────────────────────────────────────────────────────────┐  │
   │  │                    APLICACIÓN / USE CASES               │  │
   │  │  ┌───────────────────────────────────────────────────┐  │  │
   │  │  │                      DOMINIO                      │  │  │
   │  │  │   - Entities (Product, Recipe, MealPlan, Basket)  │  │  │
   │  │  │   - Value Objects (Macros, MacroTargets)          │  │  │
   │  │  │   - Exceptions                                    │  │  │
   │  │  └───────────────────────────────────────────────────┘  │  │
   │  │   - MealPlanBuilder                                     │  │
   │  │   - BasketOptimizerUseCase                              │  │
   │  └─────────────────────────────────────────────────────────┘  │
   │   - MercadonaStrategy, AldiStrategy (HTTP / APIs)             │
   │   - Nutrition Chain of Responsibility (Open Food Facts, USDA)  │
   │   - FastAPI Controllers, Static Files                          │
   └───────────────────────────────────────────────────────────────┘
```

---

## 2. Descripción de las Capas

### A. Capa de Dominio (`backend/app/domain/`)
Contiene la lógica esencial del negocio, independiente de cualquier framework o librería externa:
- `entities.py`: Clases de datos del negocio (`Product`, `Category`, `Recipe`, `DailyPlan`, `MealPlan`, `BasketItem`, `ShoppingBasket`).
- `value_objects.py`: Objetos de valor inmutables (`Macros`, `MacroTargets`) con validación y operaciones matemáticas (suma de macros, escalado proporcional, comprobación de tolerancia).
- `exceptions.py`: Excepciones de dominio tipadas (`SupermarketUnavailableException`, `ProductNotFoundException`, etc.).

### B. Capa de Puertos (`backend/app/ports/`)
Contiene las interfaces y contratos abstractos (Inversión de Dependencias - DIP de SOLID):
- `supermarket_port.py`: Interfaz abstracta `SupermarketStrategy` (`search_products`, `get_categories`, `get_product_by_id`, `get_products_by_category`).
- `nutrition_port.py`: Contrato `NutritionHandler` para la Cadena de Responsabilidad nutricional.
- `llm_port.py`: Contrato `LLMStrategy` para motores generativos de recetas.

### C. Capa de Infraestructura y Adaptadores (`backend/app/adapters/`)
Implementaciones técnicas de los puertos definidos en la capa central:
- `supermarkets/`:
  - `mercadona/`: `MercadonaStrategy` (consume la API REST de `tienda.mercadona.es`) y `MercadonaProductAdapter`.
  - `aldi/`: `AldiStrategy` y `AldiProductAdapter`.
  - `base.py`: `SupermarketFactory` y `CachedSupermarketProxy`.
- `nutrition/`:
  - `chain.py`: Cadena de 4 eslabones (`LocalCache` -> `WholeFoodsReference` -> `OpenFoodFactsEan` -> `Fallback`).
- `llm/`:
  - `strategy.py`: `RuleBasedLLMStrategy` y conector extensible para Gemini/OpenAI.
- `repositories/`:
  - `meal_plan_repo.py`: Persistencia desacoplada para planes de comida.

### D. Capa de Aplicación / Casos de Uso (`backend/app/use_cases/`)
Orquesta el flujo de negocio:
- `meal_plan_builder.py`: Constructor del plan semanal con raciones exactas y balance calórico.
- `basket_optimizer.py`: Optimización de la lista de la compra calculando unidades de compra según formatos de venta y costes en euros.

### E. Capa de Transporte (`backend/app/api/`)
Puntos de entrada HTTP con FastAPI:
- `routers/supermarkets.py`: Endpoints para explorar y buscar en supermercados.
- `routers/menus.py`: Endpoints para generar y consultar planes y cestas.
- `schemas.py`: DTOs de validación con Pydantic.
