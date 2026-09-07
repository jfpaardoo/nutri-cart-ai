# Motor Nutricional y Cadena de Responsabilidad

El motor nutricional resuelve la densidad de macronutrientes (**calorías, proteínas, carbohidratos y grasas por cada 100 gramos**) para cada ingrediente utilizado en las recetas.

---

## 1. Cadena de Resolución (Chain of Responsibility)

```
[ Ingrediente: "Pechuga de pollo", 150g ]
                  │
                  ▼
   ┌──────────────────────────────┐
   │ 1. LocalCacheNutritionHandler│ ──(Encontrado en memoria)──► [ Retorna Macros ]
   └──────────────┬───────────────┘
                  │ (Miss)
                  ▼
   ┌──────────────────────────────┐
   │2. WholeFoodsReferenceHandler │ ──(Coincidencia directa)───► [ Retorna Macros ]
   └──────────────┬───────────────┘
                  │ (Miss)
                  ▼
   ┌──────────────────────────────┐
   │ 3. OpenFoodFactsEanHandler   │ ──(Consulta EAN v0 API)───► [ Retorna Macros ]
   └──────────────┬───────────────┘
                  │ (Miss)
                  ▼
   ┌──────────────────────────────┐
   │   4. FallbackMacroHandler    │ ──────────────────────────► [ Retorna Macros Base ]
   └──────────────────────────────┘
```

---

## 2. Cálculo Matemático de Macros en Raciones
Las recetas especifican raciones precisas en gramos (ej. 160g de salmón, 80g de arroz). El valor nutricional final se calcula mediante la fórmula de escalado encapsulada en el Value Object `Macros`:

$$\text{Factor} = \frac{\text{amount\_grams}}{100.0}$$
$$\text{Calorías}_{\text{ración}} = \text{Calorías}_{100g} \times \text{Factor}$$
$$\text{Proteína}_{\text{ración}} = \text{Proteína}_{100g} \times \text{Factor}$$
$$\text{Carbohidratos}_{\text{ración}} = \text{Carbohidratos}_{100g} \times \text{Factor}$$
$$\text{Grasas}_{\text{ración}} = \text{Grasas}_{100g} \times \text{Factor}$$

---

## 3. Integración con Open Food Facts API
Para productos empaquetados con código de barras (`EAN`), se realiza una consulta HTTP al endpoint público:
```http
GET https://world.openfoodfacts.org/api/v0/product/{ean}.json
User-Agent: SmartMealApp/1.0 (nutri@local.app)
```
Se extraen los campos de `product.nutriments`:
- `energy-kcal_100g`
- `proteins_100g`
- `carbohydrates_100g`
- `fat_100g`
- `fiber_100g`
