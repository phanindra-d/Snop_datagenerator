"""
Phase 7, Step 7.4: Generate Operational Goals
Creates 3 operational goals
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, OperationalGoal

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_operational_goals():
    session = Session()

    goals = []
    GOALS_DATA = [
        ("OP-001", "Max Production Lead Time", 7.0, "days"),
        ("OP-002", "Min Batch Size", 10000.0, "units"),
        ("OP-003", "Max Order Cycle Time", 3.0, "days"),
    ]

    for code, name, value, unit in GOALS_DATA:
        goals.append(OperationalGoal(
            id=uuid.uuid4(), goal_code=code, goal_name=name,
            target_value=value, unit=unit,
            created_by="generate_operational_goals.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(goals)
    session.commit()
    print(f"✓ Inserted {len(goals)} operational goals")
    session.close()

if __name__ == "__main__":
    try:
        generate_operational_goals()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
