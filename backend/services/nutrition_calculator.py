from typing import Dict, Any, List, Tuple
import math

def calculate_tdee(age: int, gender: str, weight: float, height: float, activity_level: str) -> float:
    """
    Calculates the Total Daily Energy Expenditure (TDEE) using the Mifflin-St Jeor Equation.
    weight: float (kg)
    height: float (cm)
    age: int (years)
    gender: str ('male' or 'female')
    activity_level: str ('sedentary', 'light', 'moderate', 'active', 'very active')
    """
    # Calculate Basal Metabolic Rate (BMR)
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity level multiplier
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "lightly_active": 1.375,
        "moderate": 1.55,
        "moderately_active": 1.55,
        "active": 1.725,
        "very_active": 1.725,
        "very active": 1.9,
        "extra_active": 1.9
    }
    
    activity_factor = multipliers.get(activity_level.lower(), 1.2)
    return bmr * activity_factor

def adjust_targets_for_goal(tdee: float, weight: float, goal: str) -> Tuple[int, int]:
    """
    Adjusts the daily calories and protein targets based on the user's goal.
    goal: str ('lose', 'maintain', 'gain')
    Returns (calories, protein_grams)
    """
    # Calorie Adjustment
    if goal.lower() == "lose":
        calories = tdee - 500
        # Set a healthy lower limit floor of 1200 calories
        calories = max(calories, 1200.0)
    elif goal.lower() == "gain":
        calories = tdee + 500
    else:
        calories = tdee

    # Protein Recommendation (g / kg of body weight)
    if goal.lower() == "lose":
        protein = weight * 2.0  # High protein to maintain muscle in deficit
    elif goal.lower() == "gain":
        protein = weight * 2.0  # High protein for muscle building
    else:
        protein = weight * 1.8  # Maintenance protein

    # Ensure reasonable defaults if inputs are extreme
    calories = int(round(calories))
    protein = int(round(protein))
    
    # Cap protein at safe/realistic bounds (e.g. min 40g, max 250g)
    protein = max(40, min(protein, 250))

    return calories, protein

def aggregate_parsed_ingredients(parsed_ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates the nutrient profiles of individual parsed ingredients from Spoonacular.
    """
    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    
    micronutrients: Dict[str, Dict[str, Any]] = {}
    ingredients_list: List[Dict[str, Any]] = []

    for item in parsed_ingredients:
        name = item.get("name", "Unknown food").title()
        amount = item.get("amount", 1.0)
        unit = item.get("unit", "")
        img_file = item.get("image", "")
        img_url = f"https://spoonacular.com/cdn/ingredients_100x100/{img_file}" if img_file else None

        nutrition = item.get("nutrition", {})
        nutrients = nutrition.get("nutrients", [])

        ing_calories = 0.0
        ing_protein = 0.0
        ing_carbs = 0.0
        ing_fat = 0.0

        for n in nutrients:
            n_name = n.get("name")
            n_amount = n.get("amount", 0.0)
            n_unit = n.get("unit", "")
            n_daily = n.get("percentOfDailyNeeds", 0.0)

            if n_name == "Calories":
                total_calories += n_amount
                ing_calories += n_amount
            elif n_name == "Protein":
                total_protein += n_amount
                ing_protein += n_amount
            elif n_name == "Carbohydrates":
                total_carbs += n_amount
                ing_carbs += n_amount
            elif n_name == "Fat":
                total_fat += n_amount
                ing_fat += n_amount
            else:
                # Add to micronutrients / other nutrients
                if n_name not in micronutrients:
                    micronutrients[n_name] = {
                        "name": n_name,
                        "amount": 0.0,
                        "unit": n_unit,
                        "percentOfDailyNeeds": 0.0
                    }
                micronutrients[n_name]["amount"] += n_amount
                micronutrients[n_name]["percentOfDailyNeeds"] += n_daily
                
        ingredients_list.append({
            "name": name,
            "amount": amount,
            "unit": unit,
            "image": img_url,
            "calories": round(ing_calories, 1),
            "protein": round(ing_protein, 1),
            "carbs": round(ing_carbs, 1),
            "fat": round(ing_fat, 1)
        })

    # Clean up micronutrients by rounding and filtering very tiny trace values
    cleaned_micros = {}
    for k, v in micronutrients.items():
        v["amount"] = round(v["amount"], 2)
        v["percentOfDailyNeeds"] = round(v["percentOfDailyNeeds"], 2)
        if v["amount"] > 0:
            cleaned_micros[k] = v

    return {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1),
        "carbs": round(total_carbs, 1),
        "fat": round(total_fat, 1),
        "ingredients": ingredients_list,
        "micronutrients": cleaned_micros
    }

