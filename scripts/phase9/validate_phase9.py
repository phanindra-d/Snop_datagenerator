"""Phase 9 Validation"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import AgentRecommendation, RecommendationOutcome, UserFeedback

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase9():
    session = Session()
    errors = []
    recs = session.query(AgentRecommendation).count()
    if recs != 50: errors.append(f"Expected 50 recommendations, got {recs}")
    outcomes = session.query(RecommendationOutcome).count()
    if outcomes != 35: errors.append(f"Expected 35 outcomes, got {outcomes}")
    feedback = session.query(UserFeedback).count()
    if feedback != 55: errors.append(f"Expected 55 feedback, got {feedback}")
    session.close()
    if errors:
        print("✗ Phase 9 validation FAILED")
        for error in errors: print(f"  - {error}")
        sys.exit(1)
    else: print(f"✓ Phase 9 validated\n  - {recs+outcomes+feedback} total records")

if __name__ == "__main__":
    try: validate_phase9()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
