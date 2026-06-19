import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from backend.database.database import SessionLocal, Base, engine
from backend.database import models

print("Starting DB Operation Test...")
db = SessionLocal()

try:
    # 1. Test Querying
    print("Querying existing profiles...")
    profiles = db.query(models.UserProfile).all()
    print(f"Success! Found {len(profiles)} profiles.")
    
    print("Querying latest profile (reproducing /api/diet/profile endpoint)...")
    latest_profile = db.query(models.UserProfile).order_by(models.UserProfile.updated_at.desc()).first()
    print(f"Success! Latest profile: {latest_profile.name if latest_profile else 'None'}")

    
    # 2. Test Inserting
    print("Attempting to insert a test profile...")
    test_profile = models.UserProfile(
        name="Test Profile",
        age=30,
        gender="male",
        weight=80.0,
        height=180.0,
        activity_level="moderately_active",
        goal="maintain",
        target_calories=2500,
        target_protein=150,
        updated_at=datetime.utcnow()
    )
    db.add(test_profile)
    db.commit()
    db.refresh(test_profile)
    print(f"Success! Inserted profile with ID: {test_profile.id}")
    
    # 3. Clean up the test profile
    print("Deleting test profile to keep database clean...")
    db.delete(test_profile)
    db.commit()
    print("Success! Cleanup done.")

except Exception as e:
    db.rollback()
    print("\n❌ Error occurred during database operation:")
    import traceback
    traceback.print_exc()
finally:
    db.close()
