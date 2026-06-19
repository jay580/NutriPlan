from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date as date_type

# User Profile
class UserProfileBase(BaseModel):
    age: int
    gender: str
    weight: float  # in kg
    height: float  # in cm
    activity_level: str
    goal: str  # lose, maintain, gain

class UserProfileCreate(UserProfileBase):
    name: Optional[str] = "Default Profile"

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None

class UserProfileResponse(UserProfileBase):
    id: int
    name: Optional[str] = "Default Profile"
    target_calories: int
    target_protein: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Target Calculation Response
class TargetCalculationResponse(BaseModel):
    recommended_calories: int
    recommended_protein: int

# Meal Analysis
class MealAnalysisRequest(BaseModel):
    query: str

class IngredientDetail(BaseModel):
    name: str
    amount: float
    unit: str
    image: Optional[str] = None
    calories: Optional[float] = 0.0
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fat: Optional[float] = 0.0

class NutrientInfo(BaseModel):
    name: str
    amount: float
    unit: str
    percentOfDailyNeeds: Optional[float] = None

class MealAnalysisResponse(BaseModel):
    id: Optional[int] = None
    query: str
    calories: float
    protein: float
    carbs: float
    fat: float
    ingredients: List[IngredientDetail]
    micronutrients: Dict[str, NutrientInfo]
    timestamp: datetime

    class Config:
        from_attributes = True

# Food Database
class FoodItemResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    diet: Optional[str] = None
    serving: Optional[str] = None
    calories: float
    protein: float
    carbs: float
    fat: float

    class Config:
        from_attributes = True

# Meal Plans
class MealPlanResponse(BaseModel):
    plan_type: str
    meals: List[str]

# Calorie Tracker
class CalorieLogCreate(BaseModel):
    profile_id: int
    meal_description: str
    meal_label: Optional[str] = "snack"  # breakfast, lunch, dinner, snack
    date: Optional[date_type] = None  # defaults to today on server

class CalorieLogResponse(BaseModel):
    id: int
    profile_id: int
    date: date_type
    meal_description: str
    meal_label: Optional[str] = None
    calories: float
    protein: float
    carbs: float
    fat: float
    timestamp: datetime

    class Config:
        from_attributes = True

class DailySummary(BaseModel):
    date: date_type
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meal_count: int

class DailyDetailResponse(BaseModel):
    date: date_type
    logs: List[CalorieLogResponse]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
