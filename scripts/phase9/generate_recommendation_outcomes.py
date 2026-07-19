"""Phase 9, Step 9.2: Generate Recommendation Outcomes"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid, random
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, RecommendationOutcome, AgentRecommendation, OutcomeStatus

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_recommendation_outcomes():
    session = Session()
    recs = session.query(AgentRecommendation).limit(35).all()
    outcomes = []
    for rec in recs:
        outcomes.append(RecommendationOutcome(id=uuid.uuid4(), recommendation_id=rec.id, outcome_status=random.choice([OutcomeStatus.ACCEPTED, OutcomeStatus.REJECTED]), action_taken="Order placed" if random.random()>0.5 else "Rejected", actual_result="Stockout prevented", outcome_date=datetime.utcnow(), created_by="generate_recommendation_outcomes.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(outcomes)
    session.commit()
    print(f"✓ Inserted {len(outcomes)} outcomes")
    session.close()

if __name__ == "__main__":
    try: generate_recommendation_outcomes()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
