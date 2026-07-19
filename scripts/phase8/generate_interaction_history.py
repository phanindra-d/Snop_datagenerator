"""Phase 8, Step 8.3: Generate Interaction History"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid, random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, InteractionHistory, User

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_interaction_history():
    session = Session()
    users = session.query(User).all()
    interactions = []
    for _ in range(75):
        user = random.choice(users)
        interactions.append(InteractionHistory(id=uuid.uuid4(), user_id=user.id, interaction_type="query", interaction_content="What is inventory?", response_content="Current: 50000 units", interaction_timestamp=datetime.utcnow()-timedelta(days=random.randint(1,30)), created_by="generate_interaction_history.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(interactions)
    session.commit()
    print(f"✓ Inserted {len(interactions)} interactions")
    session.close()

if __name__ == "__main__":
    try: generate_interaction_history()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
