/**
 * UI Rendering Module
 * Responsible for constructing DOM elements for metrics, recipes, ingredients, basket, and product modal.
 */

import { registerProduct } from "./state.js";

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
            let matchedTag = `<span class="matched-pending">Generico</span>`;

            if (ing.matched_product) {
              registerProduct(ing.matched_product);
              matchedTag = `
                <button type="button" class="matched-product-badge clickable" onclick="openProductModal('${ing.matched_product.id}')" title="Ver detalles de ${ing.matched_product.name}">
                  <span class="store-tag">${ing.matched_product.brand || ing.matched_product.supermarket}</span>
                  <span class="product-title">${ing.matched_product.name}</span>
                  <span class="product-price">${ing.matched_product.price.toFixed(2)} EUR</span>
                </button>
              `;
            }

            const macroBreakdown = ing.computed_macros
              ? `<span class="ing-macros-sub">
                   ${ing.computed_macros.calories} kcal | ${ing.computed_macros.protein}g P | ${ing.computed_macros.carbs}g C | ${ing.computed_macros.fat}g G
                 </span>`
              : "";

            return `
              <div class="ingredient-card-item">
                <div class="ing-qty-pill" title="Cantidad necesaria">
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
              <summary>Pasos de preparacion (${meal.instructions.length})</summary>
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
    registerProduct(product);

    const card = document.createElement("article");
    card.className = "basket-item-tile clickable";
    card.setAttribute("tabindex", "0");
    card.setAttribute("role", "button");
    card.title = "Pulsar para ver ficha tecnica del producto";
    card.onclick = () => window.openProductModal(product.id);
    card.onkeydown = (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        window.openProductModal(product.id);
      }
    };

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
      registerProduct(product);

      const img = product.image_url
        ? `<img src="${product.image_url}" alt="${product.name}" />`
        : `<span class="feed-item-placeholder">Item</span>`;

      return `
        <div class="feed-item clickable" role="button" tabindex="0" onclick="openProductModal('${product.id}')" onkeydown="if(event.key==='Enter'||event.key===' ') openProductModal('${product.id}')" title="Ver detalles de ${product.name}">
          <div class="feed-item-left">
            ${img}
            <div class="feed-text-col">
              <span class="feed-name" title="${product.name}">${product.name}</span>
              <span class="feed-sub">${product.brand || product.supermarket} | ${product.package_format}</span>
            </div>
          </div>
          <span class="feed-price">${product.price.toFixed(2)} EUR</span>
        </div>
      `;
    })
    .join("");
}

/**
 * Builds and renders detailed modal content for a product.
 */
export function renderProductModal(product) {
  const modalBody = document.getElementById("productModalBody");
  if (!modalBody || !product) return;

  const isMercadona = (product.supermarket || "").toLowerCase() === "mercadona";
  const storeClass = isMercadona ? "mercadona" : "aldi";
  const storeName = isMercadona ? "Mercadona" : "Aldi";

  const imgHtml = product.image_url
    ? `<img src="${product.image_url}" alt="${product.name}" />`
    : `<div class="modal-img-placeholder">Sin imagen disponible</div>`;

  const refPriceText = product.reference_price
    ? `${product.reference_price.toFixed(2)} EUR / ${product.reference_format || "kg"}`
    : "Precio por unidad";

  const netWeightText = product.net_weight_grams
    ? `${product.net_weight_grams} gramos`
    : (product.package_format || "Unidad estandar");

  // Nutritional values
  const macros = product.macros_100g || null;
  const nutriHtml = macros
    ? `
      <div class="modal-nutrition-block">
        <div class="nutrition-heading">
          <span>Valores Nutricionales</span>
          <small>Por cada 100g de producto</small>
        </div>
        <div class="nutrition-grid">
          <div class="nutri-box nutri-cal">
            <span class="nutri-num">${macros.calories || 0}</span>
            <span class="nutri-label">kcal</span>
          </div>
          <div class="nutri-box nutri-prot">
            <span class="nutri-num">${macros.protein || 0}g</span>
            <span class="nutri-label">Proteina</span>
          </div>
          <div class="nutri-box nutri-carb">
            <span class="nutri-num">${macros.carbs || 0}g</span>
            <span class="nutri-label">Carbohidratos</span>
          </div>
          <div class="nutri-box nutri-fat">
            <span class="nutri-num">${macros.fat || 0}g</span>
            <span class="nutri-label">Grasas</span>
          </div>
        </div>
      </div>
    `
    : `
      <div class="modal-nutrition-block">
        <div class="nutrition-heading">
          <span>Valores Nutricionales</span>
          <small>Datos del proveedor</small>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-dim); margin-top: 0.25rem;">
          Este articulo se computa con las tablas nutricionales estándar integradas en el optimizador.
        </p>
      </div>
    `;

  modalBody.innerHTML = `
    <div class="modal-header-block">
      <div class="modal-badges-row">
        <span class="modal-store-chip ${storeClass}">${storeName}</span>
        ${product.brand ? `<span class="modal-brand-pill">${product.brand}</span>` : ""}
      </div>
      <h3 class="modal-title" id="modalProductTitle">${product.name}</h3>
    </div>

    <div class="modal-content-layout">
      <div class="modal-img-card">
        ${imgHtml}
      </div>

      <div class="modal-info-col">
        <div class="modal-price-banner">
          <div>
            <span class="modal-main-price">${product.price.toFixed(2)} EUR</span>
          </div>
          <div class="modal-ref-price">${refPriceText}</div>
        </div>

        <div class="modal-details-list">
          <div class="detail-row">
            <span>Formato:</span>
            <strong>${product.package_format || "Estándar"}</strong>
          </div>
          <div class="detail-row">
            <span>Peso / Contenido:</span>
            <strong>${netWeightText}</strong>
          </div>
          <div class="detail-row">
            <span>Codigo EAN:</span>
            <strong>${product.ean || "No especificado"}</strong>
          </div>
          <div class="detail-row">
            <span>Disponibilidad:</span>
            <strong style="color: var(--primary-light);">En Stock Local</strong>
          </div>
        </div>
      </div>
    </div>

    ${nutriHtml}
  `;
}
