from backend.services.nutrition_calculator import aggregate_parsed_ingredients

def test_aggregate_parsed_ingredients():
    mock_data = [
        {
            "name": "apple",
            "amount": 1.0,
            "unit": "",
            "image": "apple.jpg",
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 95.0, "unit": "kcal", "percentOfDailyNeeds": 4.75},
                    {"name": "Protein", "amount": 0.5, "unit": "g", "percentOfDailyNeeds": 1.0},
                    {"name": "Carbohydrates", "amount": 25.0, "unit": "g", "percentOfDailyNeeds": 8.33},
                    {"name": "Fat", "amount": 0.3, "unit": "g", "percentOfDailyNeeds": 0.46},
                    {"name": "Vitamin C", "amount": 8.4, "unit": "mg", "percentOfDailyNeeds": 14.0}
                ]
            }
        },
        {
            "name": "banana",
            "amount": 1.0,
            "unit": "",
            "image": "banana.jpg",
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 105.0, "unit": "kcal", "percentOfDailyNeeds": 5.25},
                    {"name": "Protein", "amount": 1.3, "unit": "g", "percentOfDailyNeeds": 2.6},
                    {"name": "Carbohydrates", "amount": 27.0, "unit": "g", "percentOfDailyNeeds": 9.0},
                    {"name": "Fat", "amount": 0.4, "unit": "g", "percentOfDailyNeeds": 0.61},
                    {"name": "Vitamin C", "amount": 10.3, "unit": "mg", "percentOfDailyNeeds": 17.17}
                ]
            }
        }
    ]

    result = aggregate_parsed_ingredients(mock_data)
    
    assert result["calories"] == 200.0
    assert result["protein"] == 1.8
    assert result["carbs"] == 52.0
    assert result["fat"] == 0.7
    assert len(result["ingredients"]) == 2
    assert result["ingredients"][0]["name"] == "Apple"
    assert result["ingredients"][0]["image"] == "https://spoonacular.com/cdn/ingredients_100x100/apple.jpg"
    assert "Vitamin C" in result["micronutrients"]
    assert result["micronutrients"]["Vitamin C"]["amount"] == 18.7
    assert result["micronutrients"]["Vitamin C"]["percentOfDailyNeeds"] == 31.17

