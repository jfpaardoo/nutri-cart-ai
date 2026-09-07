import urllib.request
import urllib.parse
import json
import logging
from typing import Optional, Dict
from app.ports.nutrition_port import NutritionHandler
from app.domain.value_objects import Macros
from app.domain.entities import Product

logger = logging.getLogger(__name__)


class LocalCacheNutritionHandler(NutritionHandler):
    """Link 1: Checks in-memory cache for previously resolved items."""

    def __init__(self, next_handler: Optional[NutritionHandler] = None):
        super().__init__(next_handler)
        self._cache: Dict[str, Macros] = {}

    def _handle(self, ingredient_name: str, product: Optional[Product] = None) -> Optional[Macros]:
        key = ingredient_name.lower().strip()
        if key in self._cache:
            return self._cache[key]
        if product and product.ean and product.ean in self._cache:
            return self._cache[product.ean]
        return None

    def store(self, key: str, macros: Macros):
        self._cache[key.lower().strip()] = macros


class WholeFoodsReferenceHandler(NutritionHandler):
    """
    Link 2: Checks a high-accuracy reference table of staple foods.
    Essential for whole foods (meat, fish, eggs, grains, veggies) that might not be in OFF.
    """

    REFERENCE_TABLE: Dict[str, Macros] = {
        "pollo": Macros(calories=165.0, protein=31.0, carbs=0.0, fat=3.6),
        "pechuga de pollo": Macros(calories=165.0, protein=31.0, carbs=0.0, fat=3.6),
        "pavo": Macros(calories=135.0, protein=30.0, carbs=0.0, fat=1.5),
        "pechuga de pavo": Macros(calories=135.0, protein=30.0, carbs=0.0, fat=1.5),
        "arroz": Macros(calories=360.0, protein=7.0, carbs=78.0, fat=1.0),
        "arroz blanco": Macros(calories=360.0, protein=7.0, carbs=78.0, fat=1.0),
        "arroz integral": Macros(calories=350.0, protein=7.5, carbs=74.0, fat=2.5),
        "avena": Macros(calories=375.0, protein=13.5, carbs=60.0, fat=7.0),
        "copos de avena": Macros(calories=375.0, protein=13.5, carbs=60.0, fat=7.0),
        "huevo": Macros(calories=143.0, protein=13.0, carbs=1.0, fat=10.0),
        "huevos": Macros(calories=143.0, protein=13.0, carbs=1.0, fat=10.0),
        "claras de huevo": Macros(calories=52.0, protein=11.0, carbs=0.7, fat=0.2),
        "salmon": Macros(calories=208.0, protein=20.0, carbs=0.0, fat=13.0),
        "salmón": Macros(calories=208.0, protein=20.0, carbs=0.0, fat=13.0),
        "atun": Macros(calories=101.0, protein=23.0, carbs=0.0, fat=1.0),
        "atún": Macros(calories=101.0, protein=23.0, carbs=0.0, fat=1.0),
        "merluza": Macros(calories=82.0, protein=17.0, carbs=0.0, fat=1.5),
        "ternera": Macros(calories=145.0, protein=22.0, carbs=0.0, fat=6.0),
        "aceite de oliva": Macros(calories=884.0, protein=0.0, carbs=0.0, fat=100.0),
        "patata": Macros(calories=77.0, protein=2.0, carbs=17.0, fat=0.1),
        "patatas": Macros(calories=77.0, protein=2.0, carbs=17.0, fat=0.1),
        "boniato": Macros(calories=86.0, protein=1.6, carbs=20.0, fat=0.1),
        "pasta": Macros(calories=355.0, protein=12.5, carbs=72.0, fat=1.5),
        "lentejas": Macros(calories=350.0, protein=24.0, carbs=60.0, fat=1.0),
        "garbanzos": Macros(calories=360.0, protein=19.0, carbs=61.0, fat=6.0),
        "brocoli": Macros(calories=34.0, protein=2.8, carbs=7.0, fat=0.4),
        "brócoli": Macros(calories=34.0, protein=2.8, carbs=7.0, fat=0.4),
        "espinacas": Macros(calories=23.0, protein=2.9, carbs=3.6, fat=0.4),
        "tomate": Macros(calories=18.0, protein=0.9, carbs=3.9, fat=0.2),
        "cebolla": Macros(calories=40.0, protein=1.1, carbs=9.3, fat=0.1),
        "platano": Macros(calories=89.0, protein=1.1, carbs=23.0, fat=0.3),
        "plátano": Macros(calories=89.0, protein=1.1, carbs=23.0, fat=0.3),
        "manzana": Macros(calories=52.0, protein=0.3, carbs=14.0, fat=0.2),
        "yogur": Macros(calories=60.0, protein=4.0, carbs=5.0, fat=3.0),
        "yogur griego": Macros(calories=115.0, protein=9.0, carbs=4.0, fat=7.0),
        "queso fresco batido": Macros(calories=46.0, protein=8.5, carbs=3.5, fat=0.1),
        "pan integral": Macros(calories=247.0, protein=9.0, carbs=46.0, fat=2.5),
        "nueces": Macros(calories=654.0, protein=15.0, carbs=14.0, fat=65.0),
        "almendras": Macros(calories=579.0, protein=21.0, carbs=22.0, fat=50.0),
        "leche": Macros(calories=62.0, protein=3.2, carbs=4.8, fat=3.5),
        "leche desnatada": Macros(calories=34.0, protein=3.4, carbs=5.0, fat=0.1),
        "aguacate": Macros(calories=160.0, protein=2.0, carbs=8.5, fat=14.7),
    }

    def _handle(self, ingredient_name: str, product: Optional[Product] = None) -> Optional[Macros]:
        target = ingredient_name.lower().strip()
        # Direct key match
        if target in self.REFERENCE_TABLE:
            return self.REFERENCE_TABLE[target]

        # Partial substring match
        for key, macros in self.REFERENCE_TABLE.items():
            if key in target or target in key:
                return macros

        if product:
            p_name = product.name.lower()
            for key, macros in self.REFERENCE_TABLE.items():
                if key in p_name:
                    return macros

        return None


class OpenFoodFactsEanHandler(NutritionHandler):
    """Link 3: Queries Open Food Facts REST API by barcode (EAN)."""

    def _handle(self, ingredient_name: str, product: Optional[Product] = None) -> Optional[Macros]:
        if not product or not product.ean:
            return None

        url = f"https://world.openfoodfacts.org/api/v0/product/{product.ean}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "SmartMealApp/1.0 (nutri@local.app)"})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == 1:
                    nutriments = data.get("product", {}).get("nutriments", {})
                    kcal = float(nutriments.get("energy-kcal_100g") or 0.0)
                    prot = float(nutriments.get("proteins_100g") or 0.0)
                    carbs = float(nutriments.get("carbohydrates_100g") or 0.0)
                    fat = float(nutriments.get("fat_100g") or 0.0)
                    fiber = float(nutriments.get("fiber_100g") or 0.0)

                    if kcal > 0 or prot > 0 or carbs > 0 or fat > 0:
                        return Macros(calories=kcal, protein=prot, carbs=carbs, fat=fat, fiber=fiber)
        except Exception as e:
            logger.debug(f"OpenFoodFacts lookup failed for EAN {product.ean}: {e}")

        return None


class FallbackMacroHandler(NutritionHandler):
    """Link 4: Guaranteed fallback to ensure calculation never crashes."""

    def _handle(self, ingredient_name: str, product: Optional[Product] = None) -> Optional[Macros]:
        # Default average healthy balanced food macros per 100g: ~120 kcal, 6g prot, 14g carbs, 3g fat
        return Macros(calories=120.0, protein=6.0, carbs=14.0, fat=3.0, fiber=2.0)


class NutritionResolutionService:
    """
    FACADE / ASSEMBLER for the Chain of Responsibility.
    Instantiates and connects the links in order.
    """

    def __init__(self):
        self.cache_handler = LocalCacheNutritionHandler()
        self.ref_handler = WholeFoodsReferenceHandler()
        self.off_handler = OpenFoodFactsEanHandler()
        self.fallback_handler = FallbackMacroHandler()

        # Connect chain: Cache -> Reference Table -> Open Food Facts -> Fallback
        self.cache_handler.set_next(self.ref_handler)
        self.ref_handler.set_next(self.off_handler)
        self.off_handler.set_next(self.fallback_handler)

        self.root_handler = self.cache_handler

    def resolve_macros_for_ingredient(self, ingredient_name: str, product: Optional[Product] = None) -> Macros:
        macros = self.root_handler.resolve_macros(ingredient_name, product)
        if macros:
            self.cache_handler.store(ingredient_name, macros)
            return macros
        return self.fallback_handler._handle(ingredient_name, product)
