import time
import logging
from typing import List, Optional, Dict, Tuple
from app.ports.supermarket_port import SupermarketStrategy
from app.domain.entities import Product, Category
from app.domain.exceptions import SupermarketNotSupportedException
from app.adapters.supermarkets.mercadona.strategy import MercadonaStrategy
from app.adapters.supermarkets.aldi.strategy import AldiStrategy

logger = logging.getLogger(__name__)


class CachedSupermarketProxy(SupermarketStrategy):
    """
    PROXY / DECORATOR PATTERN (Structural)
    Wraps any concrete SupermarketStrategy and provides a transparent TTL-based caching layer.
    Prevents duplicate calls to supermarket servers and protects against rate-limiting.
    """

    def __init__(self, inner_strategy: SupermarketStrategy, ttl_seconds: int = 3600):
        self._inner = inner_strategy
        self._ttl = ttl_seconds
        # Caches: (method_name, key_tuple) -> (timestamp, data)
        self._search_cache: Dict[Tuple[str, str, int], Tuple[float, List[Product]]] = {}
        self._categories_cache: Dict[str, Tuple[float, List[Category]]] = {}
        self._product_cache: Dict[Tuple[str, str], Tuple[float, Optional[Product]]] = {}

    @property
    def supermarket_name(self) -> str:
        return self._inner.supermarket_name

    def _is_expired(self, cached_at: float) -> bool:
        return (time.time() - cached_at) > self._ttl

    def search_products(self, query: str, postal_code: str, limit: int = 20) -> List[Product]:
        cache_key = (query.lower().strip(), postal_code, limit)
        if cache_key in self._search_cache:
            ts, data = self._search_cache[cache_key]
            if not self._is_expired(ts):
                logger.debug(f"[CACHE HIT] search_products({query}, {postal_code})")
                return data

        data = self._inner.search_products(query, postal_code, limit)
        self._search_cache[cache_key] = (time.time(), data)
        return data

    def get_categories(self, postal_code: str) -> List[Category]:
        if postal_code in self._categories_cache:
            ts, data = self._categories_cache[postal_code]
            if not self._is_expired(ts):
                logger.debug(f"[CACHE HIT] get_categories({postal_code})")
                return data

        data = self._inner.get_categories(postal_code)
        self._categories_cache[postal_code] = (time.time(), data)
        return data

    def get_product_by_id(self, product_id: str, postal_code: str) -> Optional[Product]:
        cache_key = (product_id, postal_code)
        if cache_key in self._product_cache:
            ts, data = self._product_cache[cache_key]
            if not self._is_expired(ts):
                logger.debug(f"[CACHE HIT] get_product_by_id({product_id})")
                return data

        data = self._inner.get_product_by_id(product_id, postal_code)
        self._product_cache[cache_key] = (time.time(), data)
        return data

    def get_products_by_category(self, category_id: str, postal_code: str) -> List[Product]:
        return self._inner.get_products_by_category(category_id, postal_code)


class SupermarketFactory:
    """
    FACTORY METHOD PATTERN (Creational)
    Instantiates the requested supermarket strategy wrapped in the caching proxy.
    Decouples application logic and controllers from concrete supermarket classes.
    """

    _registry = {
        "mercadona": MercadonaStrategy,
        "aldi": AldiStrategy,
    }

    _instances: Dict[str, SupermarketStrategy] = {}

    @classmethod
    def register_strategy(cls, name: str, strategy_class):
        """Allows dynamic registration of new supermarket strategies (Open/Closed Principle)."""
        cls._registry[name.lower()] = strategy_class

    @classmethod
    def get_strategy(cls, supermarket: str, use_cache: bool = True) -> SupermarketStrategy:
        supermarket_key = supermarket.lower().strip()
        if supermarket_key not in cls._registry:
            supported = ", ".join(cls._registry.keys())
            raise SupermarketNotSupportedException(
                f"Supermarket '{supermarket}' is not supported. Available: {supported}"
            )

        cache_instance_key = f"{supermarket_key}_{use_cache}"
        if cache_instance_key in cls._instances:
            return cls._instances[cache_instance_key]

        strategy_class = cls._registry[supermarket_key]
        raw_strategy: SupermarketStrategy = strategy_class()

        if use_cache:
            final_strategy = CachedSupermarketProxy(raw_strategy)
        else:
            final_strategy = raw_strategy

        cls._instances[cache_instance_key] = final_strategy
        return final_strategy
