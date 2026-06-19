import os
from dotenv import load_dotenv

# Load environment variables (Streamlit automatically picks up .env from the working directory)
load_dotenv()

# Set default to localhost if not specified in environment
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
