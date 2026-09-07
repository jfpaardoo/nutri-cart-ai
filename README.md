# ComeYCuadra

Sistema de planificación nutricional y generación de menús semanales adaptados a objetivos calóricos y de macronutrientes, con integración en tiempo real de catálogos y precios de supermercados en España (Mercadona y Aldi) y cálculo optimizado de la cesta de la compra.

---

## Documentación Técnica (/docs)

El proyecto dispone de documentación modular y detallada en el directorio `docs`:

- [Arquitectura del Sistema (docs/architecture.md)](docs/architecture.md): Principios de Clean Architecture, puertos y adaptadores (Hexagonal).
- [Catálogo de Patrones de Diseño (docs/design-patterns.md)](docs/design-patterns.md): Análisis técnico de los 7 patrones GoF implementados (Strategy, Factory, Adapter, Proxy/Cache, Chain of Responsibility, Builder, Repository).
- [Especificación de la API REST (docs/api-specification.md)](docs/api-specification.md): Detalle de endpoints, parámetros query y contratos de datos JSON.
- [Guía de Integración de Nuevos Supermercados (docs/supermarket-integration.md)](docs/supermarket-integration.md): Procedimiento para incorporar nuevas cadenas (Carrefour, Día, Lidl) respetando el principio Open/Closed.
- [Motor Nutricional y Resolución de Macros (docs/nutrition-engine.md)](docs/nutrition-engine.md): Flujo de resolución en cascada (Caché local, tabla de referencia y Open Food Facts API).

---

## Patrones de Diseño de Software Implementados

| Patrón (GoF) | Categoría | Implementación en el Proyecto |
| :--- | :--- | :--- |
| Strategy | Comportamiento | `SupermarketStrategy` define el contrato común (`search_products`, `get_categories`, `get_product_by_id`). Implementaciones: `MercadonaStrategy` (API REST interna) y `AldiStrategy`. |
| Factory Method | Creación | `SupermarketFactory.get_strategy("mercadona" | "aldi")` resuelve e instancia dinámicamente la estrategia sin acoplar los casos de uso. |
| Adapter / Normalizer | Estructural | `MercadonaProductAdapter` y `AldiProductAdapter` transforman los DTOs de cada proveedor en una entidad de dominio unificada: `Product`. |
| Proxy / Decorator | Estructural | `CachedSupermarketProxy` envuelve cualquier estrategia aplicando caché con TTL en memoria para evitar saturación de red y rate limiting. |
| Chain of Responsibility | Comportamiento | `NutritionResolutionService`: Cadena de eslabones en cascada para resolver los macronutrientes por 100g de cada ingrediente (Caché Local ➔ Tabla Maestra de Alimentos Básicos ➔ Open Food Facts API por EAN ➔ Fallback Seguro). |
| Builder | Creación | `MealPlanBuilder` orquesta la construcción del menú semanal, escala raciones a los objetivos calóricos y asocia ingredientes a productos reales del catálogo. |
| Repository | Persistencia | `MealPlanRepository` desacopla el almacenamiento de los menús generados de la lógica de negocio. |

---

## Estructura del Repositorio

```
food-tracking/
├── docs/
│   ├── architecture.md
│   ├── design-patterns.md
│   ├── api-specification.md
│   ├── supermarket-integration.md
│   └── nutrition-engine.md
├── backend/
│   ├── app/
│   │   ├── domain/
│   │   │   ├── entities.py
│   │   │   ├── value_objects.py
│   │   │   └── exceptions.py
│   │   ├── ports/
│   │   │   ├── supermarket_port.py
│   │   │   ├── nutrition_port.py
│   │   │   └── llm_port.py
│   │   ├── adapters/
│   │   │   ├── supermarkets/
│   │   │   │   ├── base.py
│   │   │   │   ├── mercadona/
│   │   │   │   └── aldi/
│   │   │   ├── nutrition/
│   │   │   ├── llm/
│   │   │   └── repositories/
│   │   ├── use_cases/
│   │   │   ├── meal_plan_builder.py
│   │   │   └── basket_optimizer.py
│   │   ├── api/
│   │   │   ├── routers/
│   │   │   └── schemas.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_patterns.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## Puesta en Marcha

### 1. Requisitos Previos
- Python 3.11 o superior
- Navegador web moderno

### 2. Configuración del Entorno Virtual
Abrir una terminal en el directorio `backend`:
```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 3. Ejecución de Pruebas Unitarias
```bash
.venv\Scripts\python -m pytest -v
```

### 4. Inicio del Servidor
```bash
.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Acceso al cliente web:
http://127.0.0.1:8000
