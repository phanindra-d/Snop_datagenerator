"""
Phase 7, Step 7.2: Generate Inventory Goals
Creates 5 inventory goals
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, InventoryGoal, SKUCategory, LocationType

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_inventory_goals():
    session = Session()

    goals = []
    GOALS_DATA = [
        ("INV-GOAL-001", "Max FAST SKU Inventory", 30, SKUCategory.FAST, None),
        ("INV-GOAL-002", "Max SLOW SKU Inventory", 60, SKUCategory.SLOW, None),
        ("INV-GOAL-003", "RM Safety Stock", 5, None, LocationType.WAREHOUSE_PLANT),
        ("INV-GOAL-004", "FAST FG Safety Stock", 15, SKUCategory.FAST, None),
        ("INV-GOAL-005", "SLOW FG Safety Stock", 5, SKUCategory.SLOW, None),
    ]

    for code, name, days, category, loc_type in GOALS_DATA:
        goals.append(InventoryGoal(
            id=uuid.uuid4(), goal_code=code, goal_name=name,
            target_days_supply=days, applies_to_category=category,
            applies_to_location_type=loc_type,
            created_by="generate_inventory_goals.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(goals)
    session.commit()
    print(f"✓ Inserted {len(goals)} inventory goals")
    session.close()

if __name__ == "__main__":
    try:
        generate_inventory_goals()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
