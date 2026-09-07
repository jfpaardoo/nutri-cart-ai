/**
 * API Client Module
 * Handles all async network communication with the FastAPI backend.
 */

export async function generateMealPlanApi(payload) {
  const response = await fetch("/api/menus/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Error desconocido en el servidor" }));
    throw new Error(errorData.detail || `Error HTTP ${response.status}`);
  }

  return response.json();
}

export async function searchCatalogApi(query, supermarket, postalCode, limit = 6) {
  const params = new URLSearchParams({
    q: query,
    supermarket: supermarket,
    postal_code: postalCode,
    limit: limit.toString(),
  });

  const response = await fetch(`/api/products/search?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Error al consultar catalogo: HTTP ${response.status}`);
  }

  return response.json();
}
