from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models, schemas

router = APIRouter(prefix="/api/meal-planner", tags=["Meal Planner"])

# Goal → plan type mapping
GOAL_PLAN_MAP = {
    "lose": ["weight_loss", "high_protein_low_carb"],
    "gain": ["weight_gain_muscle", "high_protein_low_carb"],
    "maintain": ["maintenance"],
}


@router.get("/plans", response_model=List[schemas.MealPlanResponse])
def get_all_plans(db: Session = Depends(get_db)):
    """Returns all meal plans grouped by plan_type."""
    rows = db.query(models.MealPlan).order_by(models.MealPlan.plan_type, models.MealPlan.meal_index).all()

    grouped: dict = {}
    for row in rows:
        grouped.setdefault(row.plan_type, []).append(row.meal_text)

    return [
        schemas.MealPlanResponse(plan_type=pt, meals=meals)
        for pt, meals in grouped.items()
    ]


@router.get("/plans/{plan_type}", response_model=schemas.MealPlanResponse)
def get_plan_by_type(plan_type: str, db: Session = Depends(get_db)):
    """Returns a specific meal plan by type."""
    rows = (
        db.query(models.MealPlan)
        .filter(models.MealPlan.plan_type == plan_type)
        .order_by(models.MealPlan.meal_index)
        .all()
    )
    meals = [r.meal_text for r in rows]
    return schemas.MealPlanResponse(plan_type=plan_type, meals=meals)


@router.get("/recommend", response_model=List[schemas.MealPlanResponse])
def recommend_plans(
    goal: str = Query(..., description="User goal: lose, gain, or maintain"),
    diet: Optional[str] = Query(None, description="Optional diet filter: vegan, vegetarian, eggetarian"),
    db: Session = Depends(get_db),
):
    """Recommends meal plans based on goal and optional diet preference."""
    plan_types = GOAL_PLAN_MAP.get(goal.lower(), ["maintenance"])

    # If a diet is specified, also include the diet-specific plan
    if diet and diet.lower() not in plan_types:
        plan_types.append(diet.lower())

    rows = (
        db.query(models.MealPlan)
        .filter(models.MealPlan.plan_type.in_(plan_types))
        .order_by(models.MealPlan.plan_type, models.MealPlan.meal_index)
        .all()
    )

    grouped: dict = {}
    for row in rows:
        grouped.setdefault(row.plan_type, []).append(row.meal_text)

    return [
        schemas.MealPlanResponse(plan_type=pt, meals=meals)
        for pt, meals in grouped.items()
    ]


@router.get("/foods", response_model=List[schemas.FoodItemResponse])
def get_foods(
    category: Optional[str] = None,
    diet: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Returns foods from the database with optional filters."""
    query = db.query(models.FoodItem)
    if category:
        query = query.filter(models.FoodItem.category == category.lower())
    if diet:
        query = query.filter(models.FoodItem.diet == diet.lower())
    if search:
        query = query.filter(models.FoodItem.name.ilike(f"%{search}%"))
    return query.order_by(models.FoodItem.name).all()
