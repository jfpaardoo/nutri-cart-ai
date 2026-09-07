# NutriSuper Planner (Food Tracking & Supermarket Optimizer) 🥗

Sistema de planificación nutricional y menús semanales adaptados a objetivos calóricos y de macronutrientes, con integración en tiempo real de precios y catálogos de supermercados españoles (**Mercadona** y **Aldi**) y cálculo automatizado de la cesta de la compra.

---

## 📚 Documentación Técnica (`/docs`)

El proyecto cuenta con documentación modular y detallada:

- 🏗️ [**Arquitectura del Sistema (`docs/architecture.md`)**](docs/architecture.md): Principios de Clean Architecture, puertos y adaptadores (Hexagonal).
- 🧩 [**Catálogo de Patrones de Diseño (`docs/design-patterns.md`)**](docs/design-patterns.md): Explicación técnica de los 7 patrones GoF implementados (*Strategy, Factory, Adapter, Proxy/Cache, Chain of Responsibility, Builder, Repository*).
- 🔌 [**Especificación de la API REST (`docs/api-specification.md`)**](docs/api-specification.md): Detalle de endpoints, parámetros query y payloads JSON de respuesta.
- 🛒 [**Guía de Integración de Nuevos Supermercados (`docs/supermarket-integration.md`)**](docs/supermarket-integration.md): Tutorial paso a paso para añadir nuevas cadenas (Carrefour, Día, Eroski, Lidl) respetando el principio Open/Closed.
- 🔬 [**Motor Nutricional y Resolución de Macros (`docs/nutrition-engine.md`)**](docs/nutrition-engine.md): Flujo de resolución en cascada (Caché, USDA/Básicos, Open Food Facts API por EAN).

---

## 🏛️ Patrones de Diseño de Software Implementados

| Patrón (GoF) | Categoría | Implementación en el Proyecto |
| :--- | :--- | :--- |
| **Strategy** | Comportamiento | `SupermarketStrategy` define la interfaz estándar (`search_products`, `get_categories`, `get_product_by_id`). Implementaciones: `MercadonaStrategy` (API oficial REST interna) y `AldiStrategy`. |
| **Factory Method** | Creación | `SupermarketFactory.get_strategy("mercadona" | "aldi")` resuelve e instancia dinámicamente la estrategia sin acoplar los casos de uso. |
| **Adapter / Normalizer** | Estructural | `MercadonaProductAdapter` y `AldiProductAdapter` transforman los DTOs heterogéneos de cada supermercado en una entidad de dominio unificada e inmutable: `Product`. |
| **Proxy / Decorator** | Estructural | `CachedSupermarketProxy` envuelve cualquier estrategia aplicando un caché con TTL en memoria para evitar saturación y proteger contra bloqueos o rate-limiting. |
| **Chain of Responsibility** | Comportamiento | `NutritionResolutionService`: Cadena de eslabones en cascada para resolver los macros por 100g de cualquier ingrediente (`Caché Local` ➔ `Tabla Maestra de Alimentos Básicos` ➔ `Open Food Facts API por EAN` ➔ `Fallback Seguro`). |
| **Builder** | Creación | `MealPlanBuilder` orquesta la generación del menú semanal, vincula ingredientes con productos reales del supermercado y valida la coherencia de macros. |
| **Repository** | Persistencia | `MealPlanRepository` desacopla el almacenamiento de los menús generados de los casos de uso de la aplicación. |

---

## 📂 Estructura del Repositorio

```
food-tracking/
├── docs/                                   # Documentación técnica modular
│   ├── architecture.md                     # Clean Architecture & Ports & Adapters
│   ├── design-patterns.md                  # Explicación detallada de patrones GoF
│   ├── api-specification.md                # Especificación Swagger/OpenAPI de endpoints
│   ├── supermarket-integration.md          # Guía para extender nuevos supermercados
│   └── nutrition-engine.md                 # Cadena de resolución nutricional y OFF
├── backend/
│   ├── app/
│   │   ├── domain/                         # Entidades de dominio puras y value objects
│   │   │   ├── entities.py                 # Product, Category, Recipe, MealPlan, BasketItem
│   │   │   ├── value_objects.py            # Macros (suma, escalado, validación), MacroTargets
│   │   │   └── exceptions.py
│   │   ├── ports/                          # Interfaces / Contratos abstractos
│   │   │   ├── supermarket_port.py         # SupermarketStrategy (Interface)
│   │   │   ├── nutrition_port.py           # NutritionHandler (Interface)
│   │   │   └── llm_port.py                 # LLMStrategy (Interface)
│   │   ├── adapters/                       # Infraestructura y servicios externos
│   │   │   ├── supermarkets/
│   │   │   │   ├── base.py                 # Factory y CachedSupermarketProxy
│   │   │   │   ├── mercadona/              # MercadonaStrategy y Adapter
│   │   │   │   └── aldi/                   # AldiStrategy y Adapter
│   │   │   ├── nutrition/                  # Cadena de resolución nutricional (OFF, USDA)
│   │   │   ├── llm/                        # RuleBasedLLMStrategy y GeminiStrategy
│   │   │   └── repositories/               # MealPlanRepository
│   │   ├── use_cases/                      # Casos de uso de negocio
│   │   │   ├── meal_plan_builder.py        # Constructor del menú semanal equilibrado
│   │   │   └── basket_optimizer.py         # Optimización de unidades y coste total (€)
│   │   ├── api/                            # API REST FastAPI
│   │   │   ├── routers/
│   │   │   │   ├── supermarkets.py         # /api/supermarkets, /api/products/search
│   │   │   │   └── menus.py                # /api/menus/generate, /api/menus/{id}
│   │   │   └── schemas.py                  # DTOs de validación Pydantic
│   │   └── main.py                         # Punto de entrada de la aplicación
│   ├── tests/
│   │   └── test_patterns.py                # Test suite completo de patrones de diseño
│   └── requirements.txt
├── frontend/                               # Dashboard web interactivo
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .env.example                            # Plantilla de variables de entorno
├── .gitignore                              # Reglas de exclusión para Git
├── CONTRIBUTING.md                         # Guía para contribuidores
├── LICENSE                                 # Licencia MIT
└── README.md
```

---

## 🚀 Puesta en Marcha

### 1. Requisitos Previos
- Python 3.11+
- Navegador web moderno

### 2. Configurar el Entorno Virtual
Abre una terminal en `backend/`:
```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 3. Ejecutar los Tests de Patrones
```bash
.venv\Scripts\python -m pytest -v
```

### 4. Iniciar el Servidor Web
```bash
.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abre en tu navegador:
👉 **http://127.0.0.1:8000**
