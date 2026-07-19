"""
Phase 7 Validation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceLevelGoal, InventoryGoal, CostGoal, OperationalGoal

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase7():
    session = Session()
    errors = []

    sl = session.query(ServiceLevelGoal).count()
    if sl != 4:
        errors.append(f"Expected 4 service level goals, got {sl}")

    inv = session.query(InventoryGoal).count()
    if inv != 5:
        errors.append(f"Expected 5 inventory goals, got {inv}")

    cost = session.query(CostGoal).count()
    if cost != 3:
        errors.append(f"Expected 3 cost goals, got {cost}")

    op = session.query(OperationalGoal).count()
    if op != 3:
        errors.append(f"Expected 3 operational goals, got {op}")

    session.close()

    if errors:
        print("✗ Phase 7 validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase 7 validated")
        print(f"  - {sl+inv+cost+op} total goals")

if __name__ == "__main__":
    try:
        validate_phase7()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
