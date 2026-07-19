"""
Phase 6, Step 6.3: Generate Manual Adjustments
Creates 20 manual adjustment records
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ManualAdjustment

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_manual_adjustments():
    session = Session()

    adjustments = []

    for i in range(20):
        adjustments.append(ManualAdjustment(
            id=uuid.uuid4(), target_table="current_inventory", target_id=uuid.uuid4(),
            field_name="quantity_on_hand", old_value=str(random.randint(1000, 5000)),
            new_value=str(random.randint(1000, 5000)),
            adjustment_reason="Manual count correction", adjusted_by=f"user_{random.randint(1,5)}",
            adjustment_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            created_by="generate_manual_adjustments.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(adjustments)
    session.commit()
    print(f"✓ Inserted {len(adjustments)} manual adjustments")
    session.close()

if __name__ == "__main__":
    try:
        generate_manual_adjustments()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
