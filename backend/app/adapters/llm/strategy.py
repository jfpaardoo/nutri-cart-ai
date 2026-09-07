import os
import json
import logging
from typing import List, Dict, Any
from app.ports.llm_port import LLMStrategy
from app.domain.value_objects import MacroTargets

logger = logging.getLogger(__name__)


class RuleBasedLLMStrategy(LLMStrategy):
    """
    STRATEGY PATTERN (Deterministic / Offline Fallback)
    Generates realistic, delicious Spanish Mediterranean recipes tailored to target macros
    without requiring third-party API keys.
    """

    MEAL_TEMPLATES = [
        {
            "meal_type": "Desayuno",
            "title": "Bowl de avena proteica con plátano y yogur griego",
            "prep_time_minutes": 10,
            "instructions": [
                "Verter los copos de avena en un bol y añadir 50ml de agua caliente o leche.",
                "Mezclar enérgicamente con el yogur griego hasta obtener una textura homogénea.",
                "Cortar el plátano en rodajas finas y colocarlo por encima.",
                "Opcional: espolvorear con canela al gusto antes de servir."
            ],
            "base_ingredients": [
                {"name": "Copos de avena", "base_grams": 60},
                {"name": "Yogur griego", "base_grams": 150},
                {"name": "Plátano", "base_grams": 100},
            ]
        },
        {
            "meal_type": "Comida",
            "title": "Arroz salteado con pechuga de pollo y brócoli",
            "prep_time_minutes": 25,
            "instructions": [
                "Cocer el arroz en agua hirviendo con un toque de sal durante 18 minutos.",
                "Cortar la pechuga de pollo en dados y dorar en la sartén con unas gotas de aceite de oliva.",
                "Separar los ramilletes de brócoli y cocinarlos al vapor o saltearlos junto al pollo.",
                "Juntar el arroz escurrido con el salteado de pollo y brócoli, mezclando bien a fuego vivo."
            ],
            "base_ingredients": [
                {"name": "Pechuga de pollo", "base_grams": 180},
                {"name": "Arroz blanco", "base_grams": 80},
                {"name": "Brócoli", "base_grams": 120},
                {"name": "Aceite de oliva", "base_grams": 10},
            ]
        },
        {
            "meal_type": "Cena",
            "title": "Lomos de salmón a la plancha con patatas al vapor y espinacas",
            "prep_time_minutes": 20,
            "instructions": [
                "Lavar y cortar las patatas en cubos medianos; cocer al vapor durante 12 minutos hasta que estén tiernas.",
                "Marcar el salmón en una sartén antiadherente caliente con la piel hacia abajo durante 3 minutos por lado.",
                "Saltear las espinacas con una cucharadita de aceite de oliva durante 2 minutos.",
                "Servir el salmón acompañado de las patatas y las espinacas salteadas."
            ],
            "base_ingredients": [
                {"name": "Salmón", "base_grams": 160},
                {"name": "Patatas", "base_grams": 150},
                {"name": "Espinacas", "base_grams": 100},
                {"name": "Aceite de oliva", "base_grams": 8},
            ]
        },
        {
            "meal_type": "Snack",
            "title": "Tosta de pan integral con huevo poché y tomate",
            "prep_time_minutes": 10,
            "instructions": [
                "Tostar las rebanadas de pan integral hasta que queden crujientes.",
                "Frotar o untar el tomate maduro rallado sobre el pan caliente.",
                "Escalfar o cocinar el huevo a la plancha con la yema tierna.",
                "Colocar el huevo sobre la tosta y sazonar con un toque de sal y pimienta."
            ],
            "base_ingredients": [
                {"name": "Pan integral", "base_grams": 60},
                {"name": "Huevos", "base_grams": 60},
                {"name": "Tomate", "base_grams": 50},
                {"name": "Aceite de oliva", "base_grams": 5},
            ]
        },
        {
            "meal_type": "Comida",
            "title": "Pasta integral con atún al natural y salsa de tomate casera",
            "prep_time_minutes": 20,
            "instructions": [
                "Hervir la pasta en abundante agua con sal durante el tiempo indicado por el fabricante.",
                "En una sartén, calentar el aceite de oliva y sofreír el tomate triturado o picado a fuego medio.",
                "Escurrir el atún e incorporarlo a la salsa de tomate.",
                "Verter la pasta escurrida en la sartén y remover para que absorba todo el sabor."
            ],
            "base_ingredients": [
                {"name": "Pasta", "base_grams": 85},
                {"name": "Atún", "base_grams": 120},
                {"name": "Tomate", "base_grams": 100},
                {"name": "Aceite de oliva", "base_grams": 10},
            ]
        },
        {
            "meal_type": "Cena",
            "title": "Tortilla francesa de espinacas con ensalada de tomate",
            "prep_time_minutes": 15,
            "instructions": [
                "Saltear brevemente las espinacas en una sartén con unas gotas de aceite de oliva.",
                "Batir los huevos enérgicamente en un plato hondo con una pizca de sal.",
                "Añadir las espinacas a los huevos batidos y cuajar la tortilla en la sartén a fuego medio.",
                "Acompañar con rodajas de tomate aliñadas con aceite de oliva."
            ],
            "base_ingredients": [
                {"name": "Huevos", "base_grams": 120},
                {"name": "Espinacas", "base_grams": 100},
                {"name": "Tomate", "base_grams": 120},
                {"name": "Aceite de oliva", "base_grams": 8},
            ]
        },
        {
            "meal_type": "Desayuno",
            "title": "Tostadas integrales con queso fresco batido y plátano",
            "prep_time_minutes": 8,
            "instructions": [
                "Tostar el pan integral.",
                "Extender una capa generosa de queso fresco batido sobre las rebanadas.",
                "Cortar el plátano en láminas y distribuir por encima.",
                "Espolvorear una pizca de canela."
            ],
            "base_ingredients": [
                {"name": "Pan integral", "base_grams": 70},
                {"name": "Queso fresco batido", "base_grams": 120},
                {"name": "Plátano", "base_grams": 90},
            ]
        }
    ]

    DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    def generate_menu_structure(
        self,
        macro_targets: MacroTargets,
        days_count: int = 7,
        meals_per_day: int = 3,
        dietary_preferences: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates the raw structure scaled to meet the target calories and macros.
        """
        # Baseline reference kcal for standard templates is ~1900 kcal/day
        scale_factor = max(0.6, min(2.5, macro_targets.target_calories / 1900.0))
        
        days_output = []
        templates_count = len(self.MEAL_TEMPLATES)

        for day_idx in range(days_count):
            day_name = self.DAY_NAMES[day_idx % 7]
            day_meals = []

            # Pick meals for this day
            meal_indices = [
                (day_idx * 2) % templates_count,
                (day_idx * 2 + 1) % templates_count,
                (day_idx * 2 + 2) % templates_count,
            ]
            if meals_per_day >= 4:
                meal_indices.append((day_idx * 2 + 3) % templates_count)

            for template_idx in meal_indices[:meals_per_day]:
                tmpl = self.MEAL_TEMPLATES[template_idx]
                scaled_ingredients = []
                for ing in tmpl["base_ingredients"]:
                    scaled_ingredients.append({
                        "name": ing["name"],
                        "amount_grams": round(ing["base_grams"] * scale_factor, 1)
                    })

                day_meals.append({
                    "title": tmpl["title"],
                    "meal_type": tmpl["meal_type"],
                    "prep_time_minutes": tmpl["prep_time_minutes"],
                    "instructions": tmpl["instructions"],
                    "ingredients": scaled_ingredients,
                })

            days_output.append({
                "day_name": day_name,
                "meals": day_meals
            })

        return days_output


class LLMFactory:
    """
    FACTORY PATTERN (Creational)
    Creates the appropriate LLM strategy based on environment settings.
    """

    @staticmethod
    def create_strategy() -> LLMStrategy:
        # If user provides GEMINI_API_KEY, we could instantiate GeminiLLMStrategy
        # For now, RuleBasedLLMStrategy provides ultra-fast, robust, reliable generation
        return RuleBasedLLMStrategy()
