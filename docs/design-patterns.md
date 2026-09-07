# Catálogo Detallado de Patrones de Diseño (GoF)

Este proyecto aplica de forma deliberada 7 patrones de diseño clásicos para resolver problemas reales de integración de software, resiliencia y desacoplamiento.

---

## 1. Patrón Strategy (Comportamiento)
- **Problema**: Cada supermercado (Mercadona, Aldi, Carrefour, Día, etc.) tiene un protocolo de acceso, estructura de URLs, autenticación y esquema JSON radicalmente diferente. Si la lógica de negocio incluyese condicionales if supermarket == 'mercadona', el código se volvería inmanejable y violaría el principio Open/Closed (OCP).
- **Solución**: Se define una interfaz común SupermarketStrategy en pp/ports/supermarket_port.py. Cada supermercado implementa esta interfaz.
- **Participantes**:
  - SupermarketStrategy (Estrategia abstracta)
  - MercadonaStrategy (Estrategia concreta que consulta https://tienda.mercadona.es/api/)
  - AldiStrategy (Estrategia concreta con catálogo Aldi)

`python
class SupermarketStrategy(ABC):
    @abstractmethod
    def search_products(self, query: str, postal_code: str, limit: int = 20) -> List[Product]: ...
    @abstractmethod
    def get_categories(self, postal_code: str) -> List[Category]: ...
    @abstractmethod
    def get_product_by_id(self, product_id: str, postal_code: str) -> Optional[Product]: ...
`

---

## 2. Patrón Factory Method (Creación)
- **Problema**: Los controladores REST y los casos de uso no deben conocer cómo se instancian ni configuran las estrategias de supermercado.
- **Solución**: SupermarketFactory.get_strategy(supermarket: str) centraliza la creación y resolución dinámica. Permite además registrar nuevas estrategias en tiempo de ejecución mediante 
egister_strategy.
- **Ubicación**: pp/adapters/supermarkets/base.py.

---

## 3. Patrón Adapter / Normalizer (Estructural)
- **Problema**: Mercadona nombra los productos como display_name, el precio como price_instructions.unit_price y la unidad de referencia en 
eference_format. Aldi u otros proveedores utilizan claves distintas como 	itle, cost o pricing.
- **Solución**: Los adaptadores (MercadonaProductAdapter, AldiProductAdapter) convierten las respuestas externas en la entidad unificada de dominio Product.
- **Ubicación**: 
  - pp/adapters/supermarkets/mercadona/adapter.py
  - pp/adapters/supermarkets/aldi/adapter.py

---

## 4. Patrón Proxy / Decorator (Estructural)
- **Problema**: Las APIs de supermercados aplican *rate limiting* o bloqueos por IP si se repiten consultas continuamente.
- **Solución**: CachedSupermarketProxy implementa la misma interfaz SupermarketStrategy envolviendo a cualquier estrategia concreta. Si una búsqueda o consulta de producto ya se realizó para ese código postal dentro del TTL (Time-To-Live, por defecto 3600 segundos), se responde directamente desde memoria sin emitir tráfico de red.
- **Ubicación**: pp/adapters/supermarkets/base.py.

---

## 5. Patrón Chain of Responsibility (Comportamiento)
- **Problema**: Ninguna base de datos de nutrición individual cubre todos los alimentos. Un código EAN puede no estar en Open Food Facts, o un producto a granel (ej. pechuga fresca) no tiene código de barras.
- **Solución**: Una cadena de eslabones donde cada eslabón intenta resolver los macronutrientes por 100g y, si no puede, delega en el siguiente.
- **Eslabones**:
  1. LocalCacheNutritionHandler: Consulta caché en memoria para respuestas ultra-rápidas.
  2. WholeFoodsReferenceHandler: Diccionario maestro de alta precisión para alimentos frescos esenciales (arroz, pollo, huevos, salmón, avena, verduras).
  3. OpenFoodFactsEanHandler: Consulta HTTP a la API oficial de Open Food Facts usando el código EAN.
  4. FallbackMacroHandler: Retorna una aproximación equilibrada segura para evitar fallos de ejecución.
- **Ubicación**: pp/adapters/nutrition/chain.py.

---

## 6. Patrón Builder (Creación)
- **Problema**: Construir un plan de comidas semanal requiere una secuencia compleja de pasos: generar la estructura de menús con IA, buscar productos equivalentes en el supermercado activo, calcular y escalar los gramos a los macros objetivo y validar que el balance calórico diario cumpla con la tolerancia (±8%).
- **Solución**: MealPlanBuilder encapsula la construcción paso a paso del objeto inmutable MealPlan.
- **Ubicación**: pp/use_cases/meal_plan_builder.py.

---

## 7. Patrón Repository (Persistencia)
- **Problema**: Los casos de uso no deben estar acoplados a SQLite, PostgreSQL o almacenamiento en memoria.
- **Solución**: MealPlanRepository expone métodos de alto nivel (save, get_by_id, list_all) permitiendo cambiar el motor de persistencia sin tocar la lógica de negocio.
- **Ubicación**: pp/adapters/repositories/meal_plan_repo.py.