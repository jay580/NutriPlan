import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models, schemas

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("/meals", response_model=List[schemas.MealAnalysisResponse])
def get_meal_history(limit: int = 20, db: Session = Depends(get_db)):
    logs = db.query(models.MealAnalysisLog).order_by(models.MealAnalysisLog.timestamp.desc()).limit(limit).all()
    result = []
    for log in logs:
        # Load ingredients and micronutrients
        ingredients = json.loads(log.ingredients_json or "[]")
        micronutrients = json.loads(log.micronutrients_json or "{}")
        
        result.append(schemas.MealAnalysisResponse(
            id=log.id,
            query=log.query,
            calories=log.calories,
            protein=log.protein,
            carbs=log.carbs,
            fat=log.fat,
            ingredients=ingredients,
            micronutrients=micronutrients,
            timestamp=log.timestamp
        ))
    return result
