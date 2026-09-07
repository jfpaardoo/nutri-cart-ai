from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import Product, Category


class SupermarketStrategy(ABC):
    """
    STRATEGY PATTERN (Behavioral)
    Common interface for all supermarket data providers (Mercadona, Aldi, Carrefour, etc.).
    Consumers of this interface do not know or care how each supermarket implements retrieval.
    """

    @property
    @abstractmethod
    def supermarket_name(self) -> str:
        """Returns the canonical identifier of the supermarket (e.g. 'mercadona', 'aldi')."""
        pass

    @abstractmethod
    def search_products(self, query: str, postal_code: str, limit: int = 20) -> List[Product]:
        """Searches products matching the query for a specific postal code."""
        pass

    @abstractmethod
    def get_categories(self, postal_code: str) -> List[Category]:
        """Retrieves top-level and nested product categories."""
        pass

    @abstractmethod
    def get_product_by_id(self, product_id: str, postal_code: str) -> Optional[Product]:
        """Retrieves full product details by its unique identifier."""
        pass

    @abstractmethod
    def get_products_by_category(self, category_id: str, postal_code: str) -> List[Product]:
        """Retrieves all products published under a specific category."""
        pass
