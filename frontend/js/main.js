/**
 * Main Application Orchestrator
 * Bootstraps event listeners, reactive UI updates, and user interactions.
 */

import { state, calculateBalancedMacros, computeMacroPercentages } from "./state.js";
import { generateMealPlanApi, searchCatalogApi } from "./api.js";
import { renderHeroMetrics, renderMeals, renderBasket, renderSearchResults } from "./ui-render.js";

// DOM Elements
const kcalRange = document.getElementById("kcalRange");
const kcalDisplay = document.getElementById("kcalDisplay");
const proteinInput = document.getElementById("proteinInput");
const carbsInput = document.getElementById("carbsInput");
const fatInput = document.getElementById("fatInput");
const proteinKcalDisplay = document.getElementById("proteinKcalDisplay");
const carbsKcalDisplay = document.getElementById("carbsKcalDisplay");
const fatKcalDisplay = document.getElementById("fatKcalDisplay");
const postalCodeInput = document.getElementById("postalCodeInput");
const btnMercadona = document.getElementById("btnMercadona");
const btnAldi = document.getElementById("btnAldi");
const currentStrategyName = document.getElementById("currentStrategyName");
const btnGenerate = document.getElementById("btnGenerate");
const generateSpinner = document.getElementById("generateSpinner");

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  updateMacroBars();
});

function setupEventListeners() {
  if (kcalRange) {
    kcalRange.addEventListener("input", (e) => {
      state.targetCalories = Number.parseInt(e.target.value, 10);
      kcalDisplay.innerHTML = `${state.targetCalories.toLocaleString()} <small>kcal</small>`;
      applyAutoBalancedMacros();
      updateMacroBars();
    });
  }

  [proteinInput, carbsInput, fatInput].forEach((input) => {
    if (input) {
      input.addEventListener("input", () => {
        state.targetProtein = Number.parseInt(proteinInput.value, 10) || 0;
        state.targetCarbs = Number.parseInt(carbsInput.value, 10) || 0;
        state.targetFat = Number.parseInt(fatInput.value, 10) || 0;
        updateMacroBars();
      });
    }
  });

  if (postalCodeInput) {
    postalCodeInput.addEventListener("change", (e) => {
      state.postalCode = e.target.value.trim() || "46001";
    });
  }
}

function applyAutoBalancedMacros() {
  const balanced = calculateBalancedMacros(state.targetCalories);
  state.targetProtein = balanced.protein;
  state.targetCarbs = balanced.carbs;
  state.targetFat = balanced.fat;

  if (proteinInput) proteinInput.value = state.targetProtein;
  if (carbsInput) carbsInput.value = state.targetCarbs;
  if (fatInput) fatInput.value = state.targetFat;
}

export function setKcalPreset(kcal) {
  state.targetCalories = kcal;
  if (kcalRange) kcalRange.value = kcal;
  if (kcalDisplay) kcalDisplay.innerHTML = `${kcal.toLocaleString()} <small>kcal</small>`;

  document.querySelectorAll(".preset-chip").forEach((btn) => {
    btn.classList.toggle("active", btn.textContent.includes(kcal.toLocaleString()));
  });

  applyAutoBalancedMacros();
  updateMacroBars();
}

function updateMacroBars() {
  const breakdown = computeMacroPercentages(state.targetProtein, state.targetCarbs, state.targetFat);

  if (proteinKcalDisplay) proteinKcalDisplay.textContent = `${breakdown.pKcal} kcal`;
  if (carbsKcalDisplay) carbsKcalDisplay.textContent = `${breakdown.cKcal} kcal`;
  if (fatKcalDisplay) fatKcalDisplay.textContent = `${breakdown.fKcal} kcal`;

  const barProt = document.getElementById("barProt");
  const barCarb = document.getElementById("barCarb");
  const barFat = document.getElementById("barFat");

  if (barProt) barProt.style.width = `${breakdown.pPct}%`;
  if (barCarb) barCarb.style.width = `${breakdown.cPct}%`;
  if (barFat) barFat.style.width = `${breakdown.fPct}%`;

  const protPctEl = document.getElementById("protPct");
  const carbPctEl = document.getElementById("carbPct");
  const fatPctEl = document.getElementById("fatPct");

  if (protPctEl) protPctEl.textContent = `${breakdown.pPct}% P`;
  if (carbPctEl) carbPctEl.textContent = `${breakdown.cPct}% C`;
  if (fatPctEl) fatPctEl.textContent = `${breakdown.fPct}% G`;
}

export function selectSupermarket(name) {
  state.supermarket = name;
  if (btnMercadona && btnAldi && currentStrategyName) {
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
}

export function setDays(days, btn) {
  state.daysCount = days;
  btn.parentElement.querySelectorAll(".opt-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
}

export function setMeals(meals, btn) {
  state.mealsPerDay = meals;
  btn.parentElement.querySelectorAll(".opt-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
}

export async function generateMealPlan() {
  if (!btnGenerate || !generateSpinner) return;
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

    const data = await generateMealPlanApi(payload);
    state.currentMealPlan = data.meal_plan;
    state.currentBasket = data.shopping_basket;

    displayPlanResults();
  } catch (error) {
    alert(`Error al generar el menu: ${error.message}`);
  } finally {
    btnGenerate.disabled = false;
    generateSpinner.style.display = "none";
  }
}

function displayPlanResults() {
  const welcomeCard = document.getElementById("welcomeCard");
  const metricsRow = document.getElementById("metricsRow");
  const viewTabs = document.getElementById("viewTabs");

  if (welcomeCard) welcomeCard.style.display = "none";
  if (metricsRow) metricsRow.style.display = "grid";
  if (viewTabs) viewTabs.style.display = "flex";

  renderHeroMetrics(state.currentMealPlan, state.currentBasket, state.daysCount, state.supermarket);
  renderMeals(state.currentMealPlan, state.currentFilterDay);
  renderBasket(state.currentBasket);
  switchTab(state.activeTab);
}

export function filterDay(dayName, btn) {
  state.currentFilterDay = dayName;
  document.querySelectorAll(".day-chip").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");

  document.querySelectorAll(".day-panel").forEach((panel) => {
    if (dayName === "all" || panel.dataset.dayName === dayName) {
      panel.style.display = "block";
    } else {
      panel.style.display = "none";
    }
  });
}

export function switchTab(tab) {
  state.activeTab = tab;
  const mealsContainer = document.getElementById("mealsContainer");
  const basketContainer = document.getElementById("basketContainer");
  const tabMeals = document.getElementById("tabMeals");
  const tabBasket = document.getElementById("tabBasket");
  const dayFilterGroup = document.getElementById("dayFilterGroup");

  if (tab === "meals") {
    if (mealsContainer) mealsContainer.style.display = "flex";
    if (basketContainer) basketContainer.style.display = "none";
    if (tabMeals) tabMeals.classList.add("active");
    if (tabBasket) tabBasket.classList.remove("active");
    if (dayFilterGroup) dayFilterGroup.style.display = "flex";
  } else {
    if (mealsContainer) mealsContainer.style.display = "none";
    if (basketContainer) basketContainer.style.display = "block";
    if (tabMeals) tabMeals.classList.remove("active");
    if (tabBasket) tabBasket.classList.add("active");
    if (dayFilterGroup) dayFilterGroup.style.display = "none";
  }
}

export function copyShoppingList() {
  if (!state.currentBasket || !state.currentBasket.items) return;

  const lines = [
    `LISTA DE COMPRA - ${state.supermarket.toUpperCase()} (CP: ${state.postalCode})`,
    `Total estimado: ${state.currentBasket.total_cost.toFixed(2)} EUR`,
    "--------------------------------------------------",
  ];

  state.currentBasket.items.forEach((item) => {
    lines.push(`[ ] ${item.units_to_buy}x ${item.product.name} (${item.total_cost.toFixed(2)} EUR) - Necesarios: ${item.grams_needed}g`);
  });

  navigator.clipboard.writeText(lines.join("\n")).then(() => {
    alert("Lista de compra copiada al portapapeles con casillas de verificacion [ ].");
  }).catch(() => {
    alert("No se pudo copiar automaticamente. Por favor copia manualmente.");
  });
}

export function quickSearch(term) {
  const searchInput = document.getElementById("liveSearchInput");
  if (searchInput) {
    searchInput.value = term;
    searchLiveCatalog();
  }
}

export async function searchLiveCatalog() {
  const searchInput = document.getElementById("liveSearchInput");
  const resultsDiv = document.getElementById("liveSearchResults");
  if (!searchInput || !resultsDiv) return;

  const query = searchInput.value.trim();
  if (!query) return;

  resultsDiv.innerHTML = `<span class="feed-message">Consultando catalogo de ${state.supermarket}...</span>`;

  try {
    const data = await searchCatalogApi(query, state.supermarket, state.postalCode, 6);
    renderSearchResults(data.products, query, resultsDiv);
  } catch (err) {
    resultsDiv.innerHTML = `<span class="feed-message error">Error: ${err.message}</span>`;
  }
}

// Attach functions to window object for declarative HTML onclick handlers
window.setKcalPreset = setKcalPreset;
window.selectSupermarket = selectSupermarket;
window.setDays = setDays;
window.setMeals = setMeals;
window.generateMealPlan = generateMealPlan;
window.filterDay = filterDay;
window.switchTab = switchTab;
window.copyShoppingList = copyShoppingList;
window.quickSearch = quickSearch;
window.searchLiveCatalog = searchLiveCatalog;
