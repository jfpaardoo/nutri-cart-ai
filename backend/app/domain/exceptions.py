class SupermarketPlannerException(Exception):
    """Base exception for the application domain."""
    pass


class SupermarketUnavailableException(SupermarketPlannerException):
    """Raised when an external supermarket service is unreachable or rate limited."""
    pass


class SupermarketNotSupportedException(SupermarketPlannerException):
    """Raised when an unsupported supermarket strategy is requested."""
    pass


class ProductNotFoundException(SupermarketPlannerException):
    """Raised when a specific product SKU or ID cannot be located."""
    pass


class NutritionResolutionException(SupermarketPlannerException):
    """Raised when nutrition data could not be resolved by any handler in the chain."""
    pass
