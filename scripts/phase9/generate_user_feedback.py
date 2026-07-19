"""Phase 9, Step 9.3: Generate User Feedback"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid, random
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserFeedback, AgentRecommendation, User, FeedbackSentiment

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_user_feedback():
    session = Session()
    recs = session.query(AgentRecommendation).all()
    users = session.query(User).all()
    feedback = []
    for _ in range(55):
        feedback.append(UserFeedback(id=uuid.uuid4(), recommendation_id=random.choice(recs).id, user_id=random.choice(users).id, sentiment=random.choice([FeedbackSentiment.POSITIVE, FeedbackSentiment.NEUTRAL, FeedbackSentiment.NEGATIVE]), rating=random.randint(1,5), comment="Good recommendation", feedback_date=datetime.utcnow(), created_by="generate_user_feedback.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(feedback)
    session.commit()
    print(f"✓ Inserted {len(feedback)} feedback records")
    session.close()

if __name__ == "__main__":
    try: generate_user_feedback()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
