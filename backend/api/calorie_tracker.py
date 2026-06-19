import json
from datetime import datetime, date as date_type
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.database import get_db
from backend.database import models, schemas
from backend.services.spoonacular_service import SpoonacularService
from backend.services.nutrition_calculator import aggregate_parsed_ingredients

router = APIRouter(prefix="/api/tracker", tags=["Calorie Tracker"])


@router.post("/log", response_model=schemas.CalorieLogResponse)
def log_meal(payload: schemas.CalorieLogCreate, db: Session = Depends(get_db)):
    """
    Logs a meal for calorie tracking.
    Uses Spoonacular to analyze nutrition, then saves to DB.
    """
    # Verify profile exists
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    log_date = payload.date or date_type.today()

    # Use Spoonacular to get nutrition info
    spoonacular = SpoonacularService()
    try:
        raw_data = spoonacular.parse_ingredients(payload.meal_description)
        result = aggregate_parsed_ingredients(raw_data)
        calories = result["calories"]
        protein = result["protein"]
        carbs = result["carbs"]
        fat = result["fat"]
    except Exception:
        # If Spoonacular fails, save with zeros — user can still track
        calories = 0.0
        protein = 0.0
        carbs = 0.0
        fat = 0.0

    db_log = models.CalorieLog(
        profile_id=payload.profile_id,
        date=log_date,
        meal_description=payload.meal_description,
        meal_label=payload.meal_label or "snack",
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        timestamp=datetime.utcnow(),
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/daily", response_model=schemas.DailyDetailResponse)
def get_daily_logs(
    profile_id: int = Query(...),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format, defaults to today"),
    db: Session = Depends(get_db),
):
    """Returns all calorie logs for a profile on a specific date, plus totals."""
    if date:
        try:
            target_date = date_type.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        target_date = date_type.today()

    logs = (
        db.query(models.CalorieLog)
        .filter(
            models.CalorieLog.profile_id == profile_id,
            models.CalorieLog.date == target_date,
        )
        .order_by(models.CalorieLog.timestamp)
        .all()
    )

    total_cal = sum(log.calories for log in logs)
    total_pro = sum(log.protein for log in logs)
    total_carb = sum(log.carbs for log in logs)
    total_fat = sum(log.fat for log in logs)

    return schemas.DailyDetailResponse(
        date=target_date,
        logs=logs,
        total_calories=round(total_cal, 1),
        total_protein=round(total_pro, 1),
        total_carbs=round(total_carb, 1),
        total_fat=round(total_fat, 1),
    )


@router.get("/history", response_model=List[schemas.DailySummary])
def get_calorie_history(
    profile_id: int = Query(...),
    limit: int = Query(30, description="Number of days to return"),
    db: Session = Depends(get_db),
):
    """Returns grouped daily summaries for a profile."""
    rows = (
        db.query(
            models.CalorieLog.date,
            func.sum(models.CalorieLog.calories).label("total_calories"),
            func.sum(models.CalorieLog.protein).label("total_protein"),
            func.sum(models.CalorieLog.carbs).label("total_carbs"),
            func.sum(models.CalorieLog.fat).label("total_fat"),
            func.count(models.CalorieLog.id).label("meal_count"),
        )
        .filter(models.CalorieLog.profile_id == profile_id)
        .group_by(models.CalorieLog.date)
        .order_by(models.CalorieLog.date.desc())
        .limit(limit)
        .all()
    )

    return [
        schemas.DailySummary(
            date=row.date,
            total_calories=round(row.total_calories or 0, 1),
            total_protein=round(row.total_protein or 0, 1),
            total_carbs=round(row.total_carbs or 0, 1),
            total_fat=round(row.total_fat or 0, 1),
            meal_count=row.meal_count,
        )
        for row in rows
    ]


@router.delete("/log/{log_id}")
def delete_calorie_log(log_id: int, db: Session = Depends(get_db)):
    """Deletes a specific calorie log entry."""
    log = db.query(models.CalorieLog).filter(models.CalorieLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    db.delete(log)
    db.commit()
    return {"detail": "Log entry deleted"}
