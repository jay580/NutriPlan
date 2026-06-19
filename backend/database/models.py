from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Date, ForeignKey
from datetime import datetime
from backend.database.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True, default="Default Profile")
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    weight = Column(Float, nullable=True)  # in kg
    height = Column(Float, nullable=True)  # in cm
    activity_level = Column(String(50), nullable=True)
    goal = Column(String(20), nullable=True)  # lose, maintain, gain
    target_calories = Column(Integer, nullable=True)
    target_protein = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MealAnalysisLog(Base):
    __tablename__ = "meal_analysis_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    micronutrients_json = Column(Text, nullable=True)  # Store micros as a JSON string
    ingredients_json = Column(Text, nullable=True)    # Store parsed ingredients as a JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

class DietPlanLog(Base):
    __tablename__ = "diet_plan_logs"

    id = Column(Integer, primary_key=True, index=True)
    target_calories = Column(Integer, nullable=False)
    target_protein = Column(Integer, nullable=False)
    diet = Column(String(50), nullable=True)
    meals_json = Column(Text, nullable=False)  # Store list of meals as a JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=True)   # breakfast, lunch, snack, dinner, ingredient
    diet = Column(String(50), nullable=True)        # vegan, vegetarian, eggetarian, nonveg
    serving = Column(String(100), nullable=True)
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_type = Column(String(50), nullable=False)  # weight_gain_muscle, weight_loss, maintenance, vegan, etc.
    meal_index = Column(Integer, default=0)         # ordering within the plan
    meal_text = Column(Text, nullable=False)         # e.g. "Breakfast: High Protein Oats + Whole Milk + Banana"

class CalorieLog(Base):
    __tablename__ = "calorie_logs"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    date = Column(Date, nullable=False)
    meal_description = Column(Text, nullable=False)
    meal_label = Column(String(50), nullable=True)  # breakfast, lunch, dinner, snack
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
