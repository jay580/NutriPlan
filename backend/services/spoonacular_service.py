import requests
from typing import Dict, Any, List, Optional
from backend.config import settings

BASE_URL = "https://api.spoonacular.com"

class SpoonacularService:
    def __init__(self):
        self.api_key = settings.SPOONACULAR_API_KEY

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key
        }

    def parse_ingredients(self, ingredient_text: str) -> List[Dict[str, Any]]:
        """
        Parses text of ingredients and returns detailed list with nutritional breakdown.
        POST /recipes/parseIngredients
        """
        url = f"{BASE_URL}/recipes/parseIngredients"
        params = {
            "includeNutrition": "true"
        }
        data = {
            "ingredientList": ingredient_text,
            "servings": 1
        }
        
        headers = self._get_headers()
        try:
            response = requests.post(url, headers=headers, params=params, data=data)
            if response.status_code != 200:
                # Try query param fallback
                params["apiKey"] = self.api_key
                response = requests.post(url, params=params, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error parsing ingredients: {e}")
            raise

    def generate_basic_meal_plan(self, target_calories: int, diet: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates daily meal plan with 3 meals matching target calories and optional diet constraint.
        GET /mealplanner/generate
        """
        url = f"{BASE_URL}/mealplanner/generate"
        params = {
            "timeFrame": "day",
            "targetCalories": target_calories
        }
        if diet and diet.lower() != "any":
            params["diet"] = diet

        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                params["apiKey"] = self.api_key
                response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error generating basic meal plan: {e}")
            raise

    def search_recipes_by_nutrients(
        self,
        meal_type: str,
        min_cal: int,
        max_cal: int,
        min_protein: int,
        max_protein: int,
        diet: Optional[str] = None,
        cuisine: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches recipes matching a meal type and specific calorie/protein bounds.
        GET /recipes/complexSearch
        """
        url = f"{BASE_URL}/recipes/complexSearch"
        params = {
            "type": meal_type,
            "minCalories": min_cal,
            "maxCalories": max_cal,
            "minProtein": min_protein,
            "maxProtein": max_protein,
            "addRecipeNutrition": "true",
            "addRecipeInformation": "true",
            "number": 5
        }
        if diet and diet.lower() != "any":
            params["diet"] = diet
        if cuisine and cuisine.lower() != "any":
            params["cuisine"] = cuisine

        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                params["apiKey"] = self.api_key
                response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Error searching recipes by nutrients: {e}")
            raise

