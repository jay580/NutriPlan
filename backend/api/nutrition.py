import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models, schemas
from backend.services.spoonacular_service import SpoonacularService
from backend.services.nutrition_calculator import aggregate_parsed_ingredients

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])

@router.post("/analyze", response_model=schemas.MealAnalysisResponse)
def analyze_meal(payload: schemas.MealAnalysisRequest, db: Session = Depends(get_db)):
    spoonacular = SpoonacularService()
    try:
        raw_data = spoonacular.parse_ingredients(payload.query)
        result = aggregate_parsed_ingredients(raw_data)
        
        # Save log to database
        db_log = models.MealAnalysisLog(
            query=payload.query,
            calories=result["calories"],
            protein=result["protein"],
            carbs=result["carbs"],
            fat=result["fat"],
            micronutrients_json=json.dumps(result["micronutrients"]),
            ingredients_json=json.dumps(result["ingredients"]),
            timestamp=datetime.utcnow()
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        
        return schemas.MealAnalysisResponse(
            id=db_log.id,
            query=db_log.query,
            calories=db_log.calories,
            protein=db_log.protein,
            carbs=db_log.carbs,
            fat=db_log.fat,
            ingredients=result["ingredients"],
            micronutrients=result["micronutrients"],
            timestamp=db_log.timestamp
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

