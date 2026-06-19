import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL")

if not SPOONACULAR_API_KEY:
    print("Warning: SPOONACULAR_API_KEY is not set in environment or .env file.")

