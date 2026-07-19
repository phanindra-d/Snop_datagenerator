"""
Phase 7, Step 7.1: Generate Service Level Goals
Creates 4 service level goals
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ServiceLevelGoal

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_service_level_goals():
    session = Session()

    goals = []
    GOALS_DATA = [
        ("SL-001", "On-Time Delivery", 95.0, "All regions"),
        ("SL-002", "In-Stock Availability", 98.0, "All regions"),
        ("SL-003", "Order Fill Rate", 97.0, "All regions"),
        ("SL-004", "Perfect Order Rate", 90.0, "All regions"),
    ]

    for code, name, target, scope in GOALS_DATA:
        goals.append(ServiceLevelGoal(
            id=uuid.uuid4(), goal_code=code, goal_name=name,
            target_pct=target, scope=scope,
            created_by="generate_service_level_goals.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(goals)
    session.commit()
    print(f"✓ Inserted {len(goals)} service level goals")
    session.close()

if __name__ == "__main__":
    try:
        generate_service_level_goals()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
