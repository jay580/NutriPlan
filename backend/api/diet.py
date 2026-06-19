from datetime import datetime
from typing import List, Optional
import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models, schemas
from backend.services.nutrition_calculator import calculate_tdee, adjust_targets_for_goal

router = APIRouter(prefix="/api/diet", tags=["Profile Management"])


@router.get("/profiles", response_model=List[schemas.UserProfileResponse])
def get_all_profiles(db: Session = Depends(get_db)):
    """Returns all user profiles."""
    profiles = db.query(models.UserProfile).order_by(models.UserProfile.updated_at.desc()).all()
    return profiles


@router.get("/profile/{profile_id}", response_model=schemas.UserProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Returns a single profile by ID."""
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/profile", response_model=Optional[schemas.UserProfileResponse])
def get_latest_profile(db: Session = Depends(get_db)):
    """Returns the most recently updated profile (for backward compatibility)."""
    profile = db.query(models.UserProfile).order_by(models.UserProfile.updated_at.desc()).first()
    return profile


@router.post("/profile", response_model=schemas.UserProfileResponse)
def create_profile(payload: schemas.UserProfileCreate, db: Session = Depends(get_db)):
    """Creates a new user profile. Does NOT overwrite existing profiles."""
    try:
        tdee = calculate_tdee(
            age=payload.age,
            gender=payload.gender,
            weight=payload.weight,
            height=payload.height,
            activity_level=payload.activity_level,
        )
        calories, protein = adjust_targets_for_goal(tdee, payload.weight, payload.goal)

        profile = models.UserProfile(
            name=payload.name or "Default Profile",
            age=payload.age,
            gender=payload.gender,
            weight=payload.weight,
            height=payload.height,
            activity_level=payload.activity_level,
            goal=payload.goal,
            target_calories=calories,
            target_protein=protein,
            updated_at=datetime.utcnow(),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile/{profile_id}", response_model=schemas.UserProfileResponse)
def update_profile(profile_id: int, payload: schemas.UserProfileUpdate, db: Session = Depends(get_db)):
    """Updates an existing profile."""
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if payload.name is not None:
        profile.name = payload.name
    if payload.age is not None:
        profile.age = payload.age
    if payload.gender is not None:
        profile.gender = payload.gender
    if payload.weight is not None:
        profile.weight = payload.weight
    if payload.height is not None:
        profile.height = payload.height
    if payload.activity_level is not None:
        profile.activity_level = payload.activity_level
    if payload.goal is not None:
        profile.goal = payload.goal

    # Recalculate targets
    tdee = calculate_tdee(
        age=profile.age,
        gender=profile.gender,
        weight=profile.weight,
        height=profile.height,
        activity_level=profile.activity_level,
    )
    calories, protein = adjust_targets_for_goal(tdee, profile.weight, profile.goal)
    profile.target_calories = calories
    profile.target_protein = protein
    profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/profile/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Deletes a profile and its associated calorie logs."""
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Delete associated calorie logs
    db.query(models.CalorieLog).filter(models.CalorieLog.profile_id == profile_id).delete()
    db.delete(profile)
    db.commit()
    return {"detail": f"Profile '{profile.name}' deleted"}
