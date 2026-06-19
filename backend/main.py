import sys
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Allow running from the backend directory with `uvicorn main:app --reload`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.database import engine, Base, SessionLocal
from backend.api.nutrition import router as nutrition_router
from backend.api.diet import router as diet_router
from backend.api.history import router as history_router
from backend.api.meal_planner import router as meal_planner_router
from backend.api.calorie_tracker import router as calorie_tracker_router
from backend.database import models

from mangum import mangum
# Auto-create SQLite tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Food & Nutrition Analyzer API",
    description="API to analyze meal nutrients, plan meals, and track daily calories.",
    version="2.0.0"
)

handler = mangum(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount API Routers
app.include_router(nutrition_router)
app.include_router(diet_router)
app.include_router(history_router)
app.include_router(meal_planner_router)
app.include_router(calorie_tracker_router)


def seed_database():
    """Seeds the FoodItem and MealPlan tables from JSON files if they are empty."""
    db = SessionLocal()
    try:
        # Seed food items
        food_count = db.query(models.FoodItem).count()
        if food_count == 0:
            foods_path = PROJECT_ROOT / "foods_dataset.json"
            if foods_path.exists():
                with open(foods_path, "r", encoding="utf-8") as f:
                    foods = json.load(f)
                for food in foods:
                    db.add(models.FoodItem(
                        name=food["name"],
                        category=food.get("category"),
                        diet=food.get("diet"),
                        serving=food.get("serving"),
                        calories=food.get("calories", 0),
                        protein=food.get("protein", 0),
                        carbs=food.get("carbs", 0),
                        fat=food.get("fat", 0),
                    ))
                db.commit()
                print(f"✅ Seeded {len(foods)} food items from foods_dataset.json")
            else:
                print(f"⚠️  foods_dataset.json not found at {foods_path}")

        # Seed meal plans
        plan_count = db.query(models.MealPlan).count()
        if plan_count == 0:
            plans_path = PROJECT_ROOT / "meal_plans.json"
            if plans_path.exists():
                with open(plans_path, "r", encoding="utf-8") as f:
                    plans = json.load(f)
                total = 0
                for plan_type, meals in plans.items():
                    for idx, meal_text in enumerate(meals):
                        db.add(models.MealPlan(
                            plan_type=plan_type,
                            meal_index=idx,
                            meal_text=meal_text,
                        ))
                        total += 1
                db.commit()
                print(f"✅ Seeded {total} meal plan entries from meal_plans.json")
            else:
                print(f"⚠️  meal_plans.json not found at {plans_path}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()


# Run seeding on startup
seed_database()


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the Food & Nutrition Analyzer & Meal Planner API!"
    }
