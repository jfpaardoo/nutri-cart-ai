# Arquitectura del Sistema (Clean Architecture & Hexagonal)

## 1. Visión General
El proyecto **NutriSuper Planner (Food Tracking)** sigue los principios de **Clean Architecture** (Arquitectura Limpia) y el patrón **Ports & Adapters (Hexagonal)**. El principio fundamental es la **Regla de Dependencia**: las capas internas (Dominio) no conocen los detalles de las capas externas (Infraestructura, APIs externas, frameworks web).

`
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
`

---

## 2. Descripción de las Capas

### A. Capa de Dominio (ackend/app/domain/)
Contiene la lógica esencial del negocio, independiente de frameworks:
- **entities.py**: Modelos inmutables y clases de datos (Product, Category, Recipe, DailyPlan, MealPlan, BasketItem, ShoppingBasket).
- **alue_objects.py**: Objetos de valor inmutables (Macros, MacroTargets) que encapsulan validación y operaciones matemáticas (suma de macros, escalado proporcional, comprobación de tolerancia).
- **exceptions.py**: Excepciones de dominio tipadas (SupermarketUnavailableException, ProductNotFoundException, etc.).

### B. Capa de Puertos (ackend/app/ports/)
Contiene las interfaces y contratos abstractos (Inversión de Dependencias - DIP de SOLID):
- **supermarket_port.py**: Interfaz abstracta SupermarketStrategy (search_products, get_categories, get_product_by_id).
- **
utrition_port.py**: Contrato NutritionHandler para la Cadena de Responsabilidad nutricional.
- **llm_port.py**: Contrato LLMStrategy para motores generativos de recetas.

### C. Capa de Infraestructura y Adaptadores (ackend/app/adapters/)
Implementaciones concretas de los puertos:
- **supermarkets/**:
  - mercadona/: MercadonaStrategy (consume API REST oficial de 	ienda.mercadona.es) y MercadonaProductAdapter.
  - ldi/: AldiStrategy y AldiProductAdapter.
  - ase.py: SupermarketFactory y CachedSupermarketProxy.
- **
utrition/**:
  - chain.py: Cadena de 4 eslabones (LocalCache ➔ WholeFoodsReference ➔ OpenFoodFactsEan ➔ Fallback).
- **llm/**:
  - strategy.py: RuleBasedLLMStrategy y conector extensible para Gemini/OpenAI.
- **
epositories/**:
  - meal_plan_repo.py: Persistencia en memoria o base de datos relacional.

### D. Capa de Aplicación / Casos de Uso (ackend/app/use_cases/)
Orquesta el flujo de negocio:
- **meal_plan_builder.py**: Constructor del plan semanal con raciones exactas y balance calórico.
- **asket_optimizer.py**: Optimización de la lista de la compra calculando unidades de compra según formatos de venta y costes en EUR.

### E. Capa de Transporte (ackend/app/api/)
Controladores FastAPI:
- **
outers/supermarkets.py**: Endpoints para explorar y buscar en supermercados.
- **
outers/menus.py**: Endpoints para generar y consultar planes y cestas.
- **schemas.py**: DTOs de validación con Pydantic.