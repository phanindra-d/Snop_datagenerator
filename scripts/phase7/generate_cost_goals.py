"""
Phase 7, Step 7.3: Generate Cost Goals
Creates 3 cost goals
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, CostGoal

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_cost_goals():
    session = Session()

    goals = []
    GOALS_DATA = [
        ("COST-001", "Max Production Cost Per Unit", 5.00, "USD/unit"),
        ("COST-002", "Max Transportation Cost Per Unit", 0.50, "USD/unit"),
        ("COST-003", "Inventory Carrying Cost", 15.00, "percent/year"),
    ]

    for code, name, value, unit in GOALS_DATA:
        goals.append(CostGoal(
            id=uuid.uuid4(), goal_code=code, goal_name=name,
            target_value=value, unit=unit,
            created_by="generate_cost_goals.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(goals)
    session.commit()
    print(f"✓ Inserted {len(goals)} cost goals")
    session.close()

if __name__ == "__main__":
    try:
        generate_cost_goals()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
