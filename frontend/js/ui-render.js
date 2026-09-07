/**
 * UI Rendering Module
 * Responsible for constructing DOM elements for metrics, recipes, ingredients, and basket.
 */

export function renderHeroMetrics(mealPlan, basket, daysCount, supermarket) {
  const totalCost = basket.total_cost;
  const costPerDay = (totalCost / daysCount).toFixed(2);

  let totalKcal = 0;
  let totalProt = 0;
  mealPlan.days.forEach((day) => {
    totalKcal += day.total_macros.calories;
    totalProt += day.total_macros.protein;
  });

  const avgKcal = Math.round(totalKcal / daysCount);
  const avgProt = Math.round(totalProt / daysCount);

  const costEl = document.getElementById("metricTotalCost");
  const costPerDayEl = document.getElementById("metricCostPerDay");
  const avgKcalEl = document.getElementById("metricAvgCalories");
  const avgProtEl = document.getElementById("metricAvgProtein");
  const superEl = document.getElementById("metricSupermarket");
  const itemsCountEl = document.getElementById("metricItemsCount");
  const badgeCountEl = document.getElementById("basketCountBadge");

  if (costEl) costEl.textContent = `${totalCost.toFixed(2)} EUR`;
  if (costPerDayEl) costPerDayEl.textContent = `${costPerDay} EUR / dia`;
  if (avgKcalEl) avgKcalEl.textContent = `${avgKcal} kcal`;
  if (avgProtEl) avgProtEl.textContent = `${avgProt}g proteina diaria`;
  if (superEl) superEl.textContent = supermarket.toUpperCase();
  if (itemsCountEl) itemsCountEl.textContent = `${basket.items.length} productos`;
  if (badgeCountEl) badgeCountEl.textContent = basket.items.length;
}

export function renderMeals(mealPlan, currentFilterDay) {
  const container = document.getElementById("mealsContainer");
  if (!container) return;
  container.innerHTML = "";

  mealPlan.days.forEach((day) => {
    const isHidden = currentFilterDay !== "all" && currentFilterDay !== day.day_name;
    const daySection = document.createElement("section");
    daySection.className = "day-panel";
    daySection.dataset.dayName = day.day_name;
    if (isHidden) daySection.style.display = "none";

    const mealsHtml = day.meals
      .map((meal) => {
        // Render structured ingredients table
        const ingredientsRows = meal.ingredients
          .map((ing) => {
            const matchedTag = ing.matched_product
              ? `<div class="matched-product-badge">
                   <span class="store-tag">${ing.matched_product.brand || ing.matched_product.supermarket}</span>
                   <span class="product-title" title="${ing.matched_product.name}">${ing.matched_product.name}</span>
                   <span class="product-price">${ing.matched_product.price.toFixed(2)} EUR</span>
                 </div>`
              : `<span class="matched-pending">Generico</span>`;

            const macroBreakdown = ing.computed_macros
              ? `<span class="ing-macros-sub">
                   ${ing.computed_macros.calories} kcal · ${ing.computed_macros.protein}g P · ${ing.computed_macros.carbs}g C · ${ing.computed_macros.fat}g G
                 </span>`
              : "";

            return `
              <div class="ingredient-card-item">
                <div class="ing-qty-pill">
                  <span class="qty-num">${ing.amount_grams}</span>
                  <span class="qty-unit">g</span>
                </div>
                <div class="ing-details">
                  <div class="ing-main-line">
                    <span class="ing-display-name">${ing.name}</span>
                    ${matchedTag}
                  </div>
                  ${macroBreakdown}
                </div>
              </div>
            `;
          })
          .join("");

        const instructionsHtml = meal.instructions
          .map((step, idx) => `
            <li class="step-item">
              <span class="step-badge">${idx + 1}</span>
              <span class="step-text">${step}</span>
            </li>
          `)
          .join("");

        return `
          <article class="recipe-box">
            <div class="recipe-meta-row">
              <span class="badge-meal-type">${meal.meal_type}</span>
              <span class="recipe-time-tag">${meal.prep_time_minutes} min</span>
            </div>

            <h4 class="recipe-heading">${meal.title}</h4>

            <div class="recipe-macros-strip">
              <span class="pill-macro pill-kcal">${meal.macros.calories} kcal</span>
              <span class="pill-macro pill-prot">${meal.macros.protein}g P</span>
              <span class="pill-macro pill-carb">${meal.macros.carbs}g C</span>
              <span class="pill-macro pill-fat">${meal.macros.fat}g G</span>
            </div>

            <div class="ingredients-section-wrapper">
              <div class="section-label-row">
                <span class="sec-title">Ingredientes y Cantidades:</span>
                <span class="sec-count">${meal.ingredients.length} items</span>
              </div>
              <div class="ingredients-deck">
                ${ingredientsRows}
              </div>
            </div>

            <details class="instructions-accordion">
              <summary>Ver pasos de preparacion (${meal.instructions.length})</summary>
              <ol class="steps-numbered-list">${instructionsHtml}</ol>
            </details>
          </article>
        `;
      })
      .join("");

    daySection.innerHTML = `
      <div class="day-panel-head">
        <div class="day-panel-title">${day.day_name}</div>
        <div class="day-macro-summary">
          <span>Kcal: <strong>${day.total_macros.calories}</strong></span>
          <span>Prot: <strong>${day.total_macros.protein}g</strong></span>
          <span>Carb: <strong>${day.total_macros.carbs}g</strong></span>
          <span>Grasa: <strong>${day.total_macros.fat}g</strong></span>
        </div>
      </div>
      <div class="meals-deck">
        ${mealsHtml}
      </div>
    `;

    container.appendChild(daySection);
  });
}

export function renderBasket(basket) {
  const grid = document.getElementById("basketGrid");
  if (!grid) return;
  grid.innerHTML = "";

  basket.items.forEach((item) => {
    const product = item.product;
    const card = document.createElement("article");
    card.className = "basket-item-tile";

    const imgElement = product.image_url
      ? `<img src="${product.image_url}" alt="${product.name}" loading="lazy" />`
      : `<div class="placeholder-graphic">Articulo Supermercado</div>`;

    card.innerHTML = `
      <div class="tile-media">
        ${imgElement}
      </div>
      <div class="tile-details">
        <span class="tile-brand">${product.brand || product.supermarket}</span>
        <h4 class="tile-name">${product.name}</h4>
        <div class="tile-meta-specs">
          <span>Requeridos: <strong>${item.grams_needed}g</strong></span>
          <span>Formato: ${product.package_format}</span>
        </div>
      </div>
      <div class="tile-pricing">
        <div class="tile-units">
          Comprar: <strong>${item.units_to_buy} ud(s)</strong> x ${product.price.toFixed(2)} EUR
        </div>
        <div class="tile-cost">${item.total_cost.toFixed(2)} EUR</div>
      </div>
    `;

    grid.appendChild(card);
  });
}

export function renderSearchResults(products, query, container) {
  if (!container) return;

  if (!products || products.length === 0) {
    container.innerHTML = `<span class="feed-message">No se encontraron productos para "${query}".</span>`;
    return;
  }

  container.innerHTML = products
    .slice(0, 6)
    .map((product) => {
      const img = product.image_url
        ? `<img src="${product.image_url}" alt="${product.name}" />`
        : `<span class="feed-item-placeholder">Item</span>`;

      return `
        <div class="feed-item">
          <div class="feed-item-left">
            ${img}
            <div class="feed-text-col">
              <span class="feed-name" title="${product.name}">${product.name}</span>
              <span class="feed-sub">${product.brand || product.supermarket} · ${product.package_format}</span>
            </div>
          </div>
          <span class="feed-price">${product.price.toFixed(2)} EUR</span>
        </div>
      `;
    })
    .join("");
}
