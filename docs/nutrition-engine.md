# Motor Nutricional y Cadena de Responsabilidad

El motor nutricional resuelve la densidad de macronutrientes (calorías, proteínas, carbohidratos y grasas por cada 100 gramos) para cada ingrediente utilizado en las recetas.

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
Las recetas especifican raciones precisas en gramos (por ejemplo: 160g de salmón, 80g de arroz). El valor nutricional final se calcula mediante la fórmula de escalado encapsulada en el Value Object `Macros`:

- Factor = amount_grams / 100.0
- Calorías_ración = Calorías_100g * Factor
- Proteína_ración = Proteína_100g * Factor
- Carbohidratos_ración = Carbohidratos_100g * Factor
- Grasas_ración = Grasas_100g * Factor

---

## 3. Integración con Open Food Facts API
Para productos empaquetados con código de barras (EAN), se realiza una consulta HTTP al endpoint público:
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
