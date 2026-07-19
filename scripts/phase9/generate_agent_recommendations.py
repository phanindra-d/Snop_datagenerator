"""Phase 9, Step 9.1: Generate Agent Recommendations"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid, random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, AgentRecommendation, User

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_agent_recommendations():
    session = Session()
    users = session.query(User).all()
    recs = []
    for i in range(50):
        recs.append(AgentRecommendation(id=uuid.uuid4(), recommendation_code=f"REC-{i+1:03d}", user_id=random.choice(users).id, recommendation_type="order", recommendation_text="Order 500kg API-PARA", confidence_score=random.uniform(75.0,99.0), generated_at=datetime.utcnow()-timedelta(days=random.randint(1,60)), created_by="generate_agent_recommendations.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(recs)
    session.commit()
    print(f"✓ Inserted {len(recs)} recommendations")
    session.close()

if __name__ == "__main__":
    try: generate_agent_recommendations()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
