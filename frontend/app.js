// State Management
const state = {
  supermarket: "mercadona",
  postalCode: "46001",
  targetCalories: 2100,
  targetProtein: 145,
  targetCarbs: 210,
  targetFat: 65,
  daysCount: 7,
  mealsPerDay: 3,
  activeTab: "meals",
  currentMealPlan: null,
  currentBasket: null,
};

// DOM Elements
const kcalRange = document.getElementById("kcalRange");
const kcalDisplay = document.getElementById("kcalDisplay");
const proteinInput = document.getElementById("proteinInput");
const carbsInput = document.getElementById("carbsInput");
const fatInput = document.getElementById("fatInput");
const postalCodeInput = document.getElementById("postalCodeInput");
const btnMercadona = document.getElementById("btnMercadona");
const btnAldi = document.getElementById("btnAldi");
const currentStrategyName = document.getElementById("currentStrategyName");
const btnGenerate = document.getElementById("btnGenerate");
const generateSpinner = document.getElementById("generateSpinner");

// Initialize Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  kcalRange.addEventListener("input", (e) => {
    state.targetCalories = parseInt(e.target.value);
    kcalDisplay.textContent = `${state.targetCalories.toLocaleString()} kcal`;
    autoBalanceMacros();
    updateMacroBars();
  });

  [proteinInput, carbsInput, fatInput].forEach((input) => {
    input.addEventListener("input", () => {
      state.targetProtein = parseInt(proteinInput.value) || 0;
      state.targetCarbs = parseInt(carbsInput.value) || 0;
      state.targetFat = parseInt(fatInput.value) || 0;
      updateMacroBars();
    });
  });

  postalCodeInput.addEventListener("change", (e) => {
    state.postalCode = e.target.value.trim() || "46001";
  });

  updateMacroBars();
});

// Auto-balance macros proportionally to calories
function autoBalanceMacros() {
  const protKcal = state.targetCalories * 0.28;
  const carbKcal = state.targetCalories * 0.42;
  const fatKcal = state.targetCalories * 0.30;

  state.targetProtein = Math.round(protKcal / 4);
  state.targetCarbs = Math.round(carbKcal / 4);
  state.targetFat = Math.round(fatKcal / 9);

  proteinInput.value = state.targetProtein;
  carbsInput.value = state.targetCarbs;
  fatInput.value = state.targetFat;
}

// Update Stacked Macro Bar
function updateMacroBars() {
  const pKcal = state.targetProtein * 4;
  const cKcal = state.targetCarbs * 4;
  const fKcal = state.targetFat * 9;
  const total = pKcal + cKcal + fKcal || 1;

  const pPct = Math.round((pKcal / total) * 100);
  const cPct = Math.round((cKcal / total) * 100);
  const fPct = 100 - pPct - cPct;

  document.getElementById("barProt").style.width = `${pPct}%`;
  document.getElementById("barCarb").style.width = `${cPct}%`;
  document.getElementById("barFat").style.width = `${fPct}%`;

  document.getElementById("protPct").textContent = `${pPct}%`;
  document.getElementById("carbPct").textContent = `${cPct}%`;
  document.getElementById("fatPct").textContent = `${fPct}%`;
}

// Supermarket Strategy Selection
function selectSupermarket(name) {
  state.supermarket = name;
  if (name === "mercadona") {
    btnMercadona.classList.add("active");
    btnAldi.classList.remove("active");
    currentStrategyName.textContent = "Mercadona";
  } else {
    btnAldi.classList.add("active");
    btnMercadona.classList.remove("active");
    currentStrategyName.textContent = "Aldi";
  }
}

function setDays(days, btn) {
  state.daysCount = days;
  btn.parentElement.querySelectorAll(".toggle-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
}

function setMeals(meals, btn) {
  state.mealsPerDay = meals;
  btn.parentElement.querySelectorAll(".toggle-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
}

// Generate Meal Plan API Call
async function generateMealPlan() {
  btnGenerate.disabled = true;
  generateSpinner.style.display = "inline-block";

  try {
    const payload = {
      supermarket: state.supermarket,
      postal_code: state.postalCode,
      target_calories: state.targetCalories,
      target_protein: state.targetProtein,
      target_carbs: state.targetCarbs,
      target_fat: state.targetFat,
      days_count: state.daysCount,
      meals_per_day: state.mealsPerDay,
    };

    const response = await fetch("/api/menus/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Error al generar el menu");
    }

    const data = await response.json();
    state.currentMealPlan = data.meal_plan;
    state.currentBasket = data.shopping_basket;

    renderResults();
  } catch (error) {
    alert(`Error: ${error.message}`);
  } finally {
    btnGenerate.disabled = false;
    generateSpinner.style.display = "none";
  }
}

// Render Results to UI
function renderResults() {
  document.getElementById("welcomeCard").style.display = "none";
  document.getElementById("metricsRow").style.display = "grid";
  document.getElementById("viewTabs").style.display = "flex";

  const totalCost = state.currentBasket.total_cost;
  const costPerDay = (totalCost / state.daysCount).toFixed(2);

  let totalKcal = 0;
  let totalProt = 0;
  state.currentMealPlan.days.forEach((d) => {
    totalKcal += d.total_macros.calories;
    totalProt += d.total_macros.protein;
  });
  const avgKcal = Math.round(totalKcal / state.daysCount);
  const avgProt = Math.round(totalProt / state.daysCount);

  document.getElementById("metricTotalCost").textContent = `${totalCost.toFixed(2)} EUR`;
  document.getElementById("metricCostPerDay").textContent = `${costPerDay} EUR / dia`;
  document.getElementById("metricAvgCalories").textContent = `${avgKcal} kcal`;
  document.getElementById("metricAvgProtein").textContent = `${avgProt}g proteina`;
  document.getElementById("metricSupermarket").textContent = state.supermarket.toUpperCase();
  document.getElementById("metricItemsCount").textContent = `${state.currentBasket.items.length} productos en cesta`;
  document.getElementById("basketCountBadge").textContent = state.currentBasket.items.length;

  renderMeals();
  renderBasket();
  switchTab(state.activeTab);
}

// Render Weekly Meals
function renderMeals() {
  const container = document.getElementById("mealsContainer");
  container.innerHTML = "";

  state.currentMealPlan.days.forEach((day) => {
    const daySection = document.createElement("div");
    daySection.className = "day-section";

    const mealsHtml = day.meals
      .map((meal) => {
        const ingredientsHtml = meal.ingredients
          .map((ing) => {
            const matchedBadge = ing.matched_product
              ? `<span class="ing-matched-badge">${ing.matched_product.name} (${ing.matched_product.price} EUR)</span>`
              : "";
            return `
              <li>
                <span>${ing.name} ${matchedBadge}</span>
                <strong>${ing.amount_grams}g</strong>
              </li>
            `;
          })
          .join("");

        const instructionsHtml = meal.instructions
          .map((step) => `<li>${step}</li>`)
          .join("");

        return `
          <div class="recipe-card">
            <div class="recipe-header">
              <span class="recipe-type">${meal.meal_type}</span>
              <span class="recipe-time">${meal.prep_time_minutes} min</span>
            </div>
            <h4 class="recipe-title">${meal.title}</h4>

            <div class="recipe-macros-bar">
              <span class="recipe-macro-chip chip-kcal">${meal.macros.calories} kcal</span>
              <span class="recipe-macro-chip chip-prot">${meal.macros.protein}g P</span>
              <span class="recipe-macro-chip chip-carb">${meal.macros.carbs}g C</span>
              <span class="recipe-macro-chip chip-fat">${meal.macros.fat}g G</span>
            </div>

            <ul class="recipe-ingredients-list">
              ${ingredientsHtml}
            </ul>

            <details class="recipe-instructions">
              <summary>Pasos de preparacion (${meal.instructions.length})</summary>
              <ol>${instructionsHtml}</ol>
            </details>
          </div>
        `;
      })
      .join("");

    daySection.innerHTML = `
      <div class="day-header">
        <div class="day-title">${day.day_name}</div>
        <div class="day-macros">
          <span>Kcal: <strong>${day.total_macros.calories}</strong></span>
          <span>Prot: <strong>${day.total_macros.protein}g</strong></span>
          <span>Carb: <strong>${day.total_macros.carbs}g</strong></span>
          <span>Grasa: <strong>${day.total_macros.fat}g</strong></span>
        </div>
      </div>
      <div class="meals-list">
        ${mealsHtml}
      </div>
    `;

    container.appendChild(daySection);
  });
}

// Render Shopping Basket Grid
function renderBasket() {
  const grid = document.getElementById("basketGrid");
  grid.innerHTML = "";

  state.currentBasket.items.forEach((item) => {
    const p = item.product;
    const card = document.createElement("div");
    card.className = "basket-card";

    const imgTag = p.image_url
      ? `<img src="${p.image_url}" alt="${p.name}" loading="lazy" />`
      : `<span style="font-size: 0.9rem; color: var(--text-dim);">Sin imagen</span>`;

    card.innerHTML = `
      <div class="basket-img-wrapper">
        ${imgTag}
      </div>
      <div class="basket-item-info">
        <span class="basket-item-brand">${p.brand || p.supermarket}</span>
        <h4 class="basket-item-name">${p.name}</h4>
        <span style="font-size: 0.75rem; color: var(--text-dim);">
          Requeridos: ${item.grams_needed}g · Formato: ${p.package_format}
        </span>
      </div>
      <div class="basket-item-pricing">
        <div class="basket-units">
          Comprar: <strong>${item.units_to_buy} ud(s)</strong> x ${p.price.toFixed(2)} EUR
        </div>
        <div class="basket-cost">${item.total_cost.toFixed(2)} EUR</div>
      </div>
    `;

    grid.appendChild(card);
  });
}

// Tab Switching
function switchTab(tab) {
  state.activeTab = tab;
  const mealsContainer = document.getElementById("mealsContainer");
  const basketContainer = document.getElementById("basketContainer");
  const tabMeals = document.getElementById("tabMeals");
  const tabBasket = document.getElementById("tabBasket");

  if (tab === "meals") {
    mealsContainer.style.display = "flex";
    basketContainer.style.display = "none";
    tabMeals.classList.add("active");
    tabBasket.classList.remove("active");
  } else {
    mealsContainer.style.display = "none";
    basketContainer.style.display = "block";
    tabMeals.classList.remove("active");
    tabBasket.classList.add("active");
  }
}

// Live Supermarket Strategy Search Tester
async function searchLiveCatalog() {
  const query = document.getElementById("liveSearchInput").value.trim();
  const resultsDiv = document.getElementById("liveSearchResults");

  if (!query) return;

  resultsDiv.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-dim);">Consultando catalogo de ${state.supermarket}...</span>`;

  try {
    const res = await fetch(
      `/api/products/search?q=${encodeURIComponent(query)}&supermarket=${state.supermarket}&postal_code=${state.postalCode}`
    );
    const data = await res.json();

    if (!data.products || data.products.length === 0) {
      resultsDiv.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-dim);">No se encontraron productos.</span>`;
      return;
    }

    resultsDiv.innerHTML = data.products
      .slice(0, 5)
      .map((p) => {
        const img = p.image_url ? `<img src="${p.image_url}" />` : `<span>[Item]</span>`;
        return `
          <div class="mini-product-item">
            <div class="mini-product-info">
              ${img}
              <span class="mini-product-name" title="${p.name}">${p.name}</span>
            </div>
            <span class="mini-product-price">${p.price.toFixed(2)} EUR</span>
          </div>
        `;
      })
      .join("");
  } catch (err) {
    resultsDiv.innerHTML = `<span style="font-size: 0.8rem; color: var(--accent-red);">Error: ${err.message}</span>`;
  }
}
