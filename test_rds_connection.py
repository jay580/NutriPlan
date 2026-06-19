import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Load environment variables
load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL not set in .env file.")
    sys.exit(1)

print(f"Attempting to connect to database URL: {db_url.split('@')[-1] if '@' in db_url else db_url} (hiding password)")

try:
    # Disable sqlite-specific connect args
    engine = create_engine(db_url)
    
    # Try to connect
    with engine.connect() as conn:
        print("[SUCCESS] Successfully connected to the database!")
        
        # Inspect tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"Found the following tables in the database:")
            for table in tables:
                # Count rows (using text() for SQLAlchemy 2.0 compatibility)
                res = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"  - {table}: {count} rows")
        else:
            print("[INFO] Connected, but NO tables were found in this database.")
            print("This means the tables have not been created yet. Run the FastAPI server to trigger table creation.")
            
except Exception as e:
    print("[ERROR] Failed to inspect the database.")
    print(f"Error details: {e}")
    print("\nTroubleshooting tips:")
    print("1. Did you run 'pip install psycopg2-binary'?")
    print("2. Is the host/endpoint spelling correct in your DATABASE_URL?")
    print("3. Check AWS RDS Security Group Inbound Rules: Ensure Port 5432 is open to your current IP address.")
    print("4. Check AWS RDS instance settings: Ensure 'Publicly accessible' is set to 'Yes' if running this locally.")


