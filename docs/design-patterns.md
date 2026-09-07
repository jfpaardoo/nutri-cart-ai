# Catálogo de Patrones de Diseño de Software (GoF)

Este proyecto aplica de forma deliberada 7 patrones de diseño de software para resolver problemas específicos de integración, resiliencia y desacoplamiento.

---

## 1. Patrón Strategy (Comportamiento)
- **Problema**: Cada supermercado (Mercadona, Aldi, Carrefour, Día, etc.) dispone de un protocolo de acceso, estructura de URLs, autenticación y esquema JSON diferente. Incluir lógica condicional en los casos de uso violaría el principio Open/Closed (OCP).
- **Solución**: Se define una interfaz común `SupermarketStrategy` en `app/ports/supermarket_port.py`. Cada supermercado implementa este contrato.
- **Componentes**:
  - `SupermarketStrategy`: Interfaz abstracta.
  - `MercadonaStrategy`: Conexión directa a la API REST interna de Mercadona.
  - `AldiStrategy`: Conexión al catálogo estructurado de Aldi España.

```python
class SupermarketStrategy(ABC):
    @abstractmethod
    def search_products(self, query: str, postal_code: str, limit: int = 20) -> List[Product]: ...
    @abstractmethod
    def get_categories(self, postal_code: str) -> List[Category]: ...
    @abstractmethod
    def get_product_by_id(self, product_id: str, postal_code: str) -> Optional[Product]: ...
```

---

## 2. Patrón Factory Method (Creación)
- **Problema**: Los controladores REST y casos de uso no deben conocer la instanciación ni configuración técnica de las estrategias de supermercado.
- **Solución**: `SupermarketFactory.get_strategy(supermarket: str)` centraliza la creación y resolución dinámica. Permite registrar nuevas estrategias en tiempo de ejecución mediante `register_strategy`.
- **Ubicación**: `app/adapters/supermarkets/base.py`.

---

## 3. Patrón Adapter / Normalizer (Estructural)
- **Problema**: Mercadona estructura los productos con campos como `display_name`, `price_instructions.unit_price` y `reference_format`. Aldi u otros proveedores utilizan claves distintas.
- **Solución**: Los adaptadores (`MercadonaProductAdapter`, `AldiProductAdapter`) convierten las respuestas externas en la entidad de dominio unificada `Product`.
- **Ubicación**:
  - `app/adapters/supermarkets/mercadona/adapter.py`
  - `app/adapters/supermarkets/aldi/adapter.py`

---

## 4. Patrón Proxy / Decorator (Estructural)
- **Problema**: Las llamadas frecuentes a servicios externos pueden generar bloqueos o límites de tasa (rate limits).
- **Solución**: `CachedSupermarketProxy` implementa la misma interfaz `SupermarketStrategy` decorando la estrategia real con un mecanismo de caché en memoria con TTL (Time-To-Live, 3600 segundos por defecto).
- **Ubicación**: `app/adapters/supermarkets/base.py`.

---

## 5. Patrón Chain of Responsibility (Comportamiento)
- **Problema**: Ninguna base de datos de nutrición cubre el 100% de los alimentos. Un código EAN puede no existir en Open Food Facts, o un producto a granel (pechuga fresca, verduras) no incluye código de barras.
- **Solución**: Una secuencia ordenada de eslabones donde cada uno intenta resolver los macronutrientes por 100g y, si no lo logra, delega en el siguiente.
- **Eslabones**:
  1. `LocalCacheNutritionHandler`: Consulta caché en memoria para respuestas inmediatas.
  2. `WholeFoodsReferenceHandler`: Diccionario de referencia para alimentos frescos sin procesar (arroz, pollo, huevos, salmón, avena, verduras).
  3. `OpenFoodFactsEanHandler`: Consulta a la API pública de Open Food Facts por código de barras.
  4. `FallbackMacroHandler`: Retorna una aproximación equilibrada segura para garantizar la continuidad del flujo.
- **Ubicación**: `app/adapters/nutrition/chain.py`.

---

## 6. Patrón Builder (Creación)
- **Problema**: La creación de un plan de comidas semanal requiere una secuencia coordinada de pasos: generar la estructura de platos, mapear ingredientes con productos reales en stock, calcular y escalar los gramos a los objetivos nutricionales y comprobar que el balance diario se mantenga dentro del margen de tolerancia.
- **Solución**: `MealPlanBuilder` encapsula la construcción progresiva y validación del objeto inmutable `MealPlan`.
- **Ubicación**: `app/use_cases/meal_plan_builder.py`.

---

## 7. Patrón Repository (Persistencia)
- **Problema**: Los casos de uso no deben acoplarse al motor de base de datos específico (memoria, SQLite, PostgreSQL).
- **Solución**: `MealPlanRepository` expone métodos abstractos de almacenamiento (`save`, `get_by_id`, `list_all`) permitiendo cambiar la tecnología de persistencia sin alterar la lógica de negocio.
- **Ubicación**: `app/adapters/repositories/meal_plan_repo.py`.
