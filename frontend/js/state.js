/**
 * State Management Module
 * Encapsulates application state, nutritional ratios, and macro math.
 */

export const state = {
  supermarket: "mercadona",
  postalCode: "46001",
  targetCalories: 2100,
  targetProtein: 145,
  targetCarbs: 210,
  targetFat: 65,
  daysCount: 7,
  mealsPerDay: 3,
  activeTab: "meals",
  currentFilterDay: "all",
  currentMealPlan: null,
  currentBasket: null,
  productsById: {},
};

/**
 * Registers a product in the global lookup map for fast retrieval by ID.
 */
export function registerProduct(product) {
  if (product && product.id) {
    state.productsById[product.id] = product;
  }
}

/**
 * Retrieves a registered product by its ID.
 */
export function getProductById(productId) {
  return state.productsById[productId] || null;
}

/**
 * Calculates balanced macros proportionally to target calories.
 * Default split: 28% Protein, 42% Carbohydrates, 30% Healthy Fats.
 */
export function calculateBalancedMacros(calories) {
  const protKcal = calories * 0.28;
  const carbKcal = calories * 0.42;
  const fatKcal = calories * 0.30;

  return {
    protein: Math.round(protKcal / 4),
    carbs: Math.round(carbKcal / 4),
    fat: Math.round(fatKcal / 9),
    protKcal: Math.round(protKcal),
    carbKcal: Math.round(carbKcal),
    fatKcal: Math.round(fatKcal),
  };
}

/**
 * Computes percentage breakdown for protein, carbs, and fat.
 */
export function computeMacroPercentages(proteinGrams, carbsGrams, fatGrams) {
  const pKcal = proteinGrams * 4;
  const cKcal = carbsGrams * 4;
  const fKcal = fatGrams * 9;
  const totalKcal = pKcal + cKcal + fKcal || 1;

  const pPct = Math.round((pKcal / totalKcal) * 100);
  const cPct = Math.round((cKcal / totalKcal) * 100);
  const fPct = Math.max(0, 100 - pPct - cPct);

  return {
    pPct,
    cPct,
    fPct,
    pKcal,
    cKcal,
    fKcal,
    totalKcal,
  };
}
