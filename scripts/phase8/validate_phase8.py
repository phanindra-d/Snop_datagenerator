"""Phase 8 Validation"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, UserPreference, InteractionHistory

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase8():
    session = Session()
    errors = []
    users = session.query(User).count()
    if users != 20: errors.append(f"Expected 20 users, got {users}")
    prefs = session.query(UserPreference).count()
    if prefs != 25: errors.append(f"Expected 25 prefs, got {prefs}")
    interactions = session.query(InteractionHistory).count()
    if interactions != 75: errors.append(f"Expected 75 interactions, got {interactions}")
    session.close()
    if errors:
        print("✗ Phase 8 validation FAILED")
        for error in errors: print(f"  - {error}")
        sys.exit(1)
    else: print(f"✓ Phase 8 validated\n  - {users+prefs+interactions} total records")

if __name__ == "__main__":
    try: validate_phase8()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
