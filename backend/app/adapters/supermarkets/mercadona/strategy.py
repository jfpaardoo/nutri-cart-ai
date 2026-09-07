import urllib.request
import urllib.parse
import json
import logging
from typing import List, Optional, Dict
from app.ports.supermarket_port import SupermarketStrategy
from app.domain.entities import Product, Category
from app.domain.exceptions import SupermarketUnavailableException, ProductNotFoundException
from app.adapters.supermarkets.mercadona.adapter import MercadonaProductAdapter

logger = logging.getLogger(__name__)


class MercadonaStrategy(SupermarketStrategy):
    """
    STRATEGY PATTERN (Concrete Implementation)
    Connects to the official internal REST API of Mercadona.
    """

    BASE_URL = "https://tienda.mercadona.es/api"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self.adapter = MercadonaProductAdapter()
        # In-memory index of products per postal code to allow fast local text search
        self._product_cache_by_cp: Dict[str, List[Product]] = {}

    @property
    def supermarket_name(self) -> str:
        return "mercadona"

    def _get_json(self, url: str) -> dict:
        req = urllib.request.Request(url, headers=self.HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status != 200:
                    raise SupermarketUnavailableException(f"Mercadona API responded with HTTP {response.status}")
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ProductNotFoundException(f"Resource not found at {url}")
            raise SupermarketUnavailableException(f"Mercadona API HTTP error: {e.code}")
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise SupermarketUnavailableException(f"Connection to Mercadona failed: {e}")

    def get_categories(self, postal_code: str) -> List[Category]:
        url = f"{self.BASE_URL}/categories/?postal_code={postal_code}"
        data = self._get_json(url)
        results = data.get("results", [])
        return [self.adapter.to_category(cat) for cat in results]

    def get_product_by_id(self, product_id: str, postal_code: str) -> Optional[Product]:
        url = f"{self.BASE_URL}/products/{product_id}/?postal_code={postal_code}"
        try:
            data = self._get_json(url)
            return self.adapter.to_product(data)
        except ProductNotFoundException:
            return None

    def get_products_by_category(self, category_id: str, postal_code: str) -> List[Product]:
        url = f"{self.BASE_URL}/categories/{category_id}/?postal_code={postal_code}"
        try:
            data = self._get_json(url)
        except ProductNotFoundException:
            return []

        products: List[Product] = []
        # Categories may have nested subcategories containing the products
        subcategories = data.get("categories", [])
        for sub in subcategories:
            for raw_prod in sub.get("products", []):
                products.append(self.adapter.to_product(raw_prod))

        # Some category endpoints return products directly at the root
        for raw_prod in data.get("products", []):
            products.append(self.adapter.to_product(raw_prod))

        return products

    def search_products(self, query: str, postal_code: str, limit: int = 20) -> List[Product]:
        """
        Searches products matching the query.
        Populates index on demand by querying representative categories.
        """
        query_lower = query.lower().strip()

        # Check if we already loaded an index for this CP
        if postal_code not in self._product_cache_by_cp:
            self._warm_up_popular_categories(postal_code)

        cached_products = self._product_cache_by_cp.get(postal_code, [])
        matches = [
            p for p in cached_products
            if query_lower in p.name.lower() or (p.brand and query_lower in p.brand.lower())
        ]

        # If not enough matches, try fetching more relevant categories
        if len(matches) < limit:
            self._load_more_categories_for_search(query_lower, postal_code)
            cached_products = self._product_cache_by_cp.get(postal_code, [])
            matches = [
                p for p in cached_products
                if query_lower in p.name.lower() or (p.brand and query_lower in p.brand.lower())
            ]

        return matches[:limit]

    def _warm_up_popular_categories(self, postal_code: str):
        """Preloads common staple food subcategories to provide instant search."""
        popular_subcat_ids = [
            "112", # Aceite, vinagre y sal
            "115", # Especias
            "118", # Arroz, legumbres y pasta
            "122", # Huevos
            "123", # Leche y bebidas vegetales
            "125", # Aves y pollo
            "126", # Carne vacuno y cerdo
            "128", # Pescado fresco
            "134", # Fruta
            "135", # Verdura
            "145", # Panadería y cereales
            "147", # Avena y cereales desayuno
            "161", # Atún y conservas de pescado
        ]
        all_prods: List[Product] = []
        for cat_id in popular_subcat_ids:
            try:
                prods = self.get_products_by_category(cat_id, postal_code)
                all_prods.extend(prods)
            except Exception:
                continue

        # Deduplicate by id
        seen = set()
        deduped = []
        for p in all_prods:
            if p.id not in seen:
                seen.add(p.id)
                deduped.append(p)

        self._product_cache_by_cp[postal_code] = deduped

    def _load_more_categories_for_search(self, query_lower: str, postal_code: str):
        """Loads additional subcategories if query might be in another section."""
        try:
            categories = self.get_categories(postal_code)
            for top_cat in categories:
                for sub in top_cat.subcategories:
                    # If category name matches roughly
                    sub_words = sub.name.lower().split()
                    if any(w in query_lower for w in sub_words) or any(query_lower in w for w in sub_words):
                        prods = self.get_products_by_category(sub.id, postal_code)
                        current = self._product_cache_by_cp.get(postal_code, [])
                        current.extend(prods)
                        self._product_cache_by_cp[postal_code] = current
        except Exception:
            pass
