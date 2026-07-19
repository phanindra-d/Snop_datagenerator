"""
Phase 4 Validation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import HistoricalEvent, DemandPlan, SupplyPlan, InventoryMovement

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase4():
    session = Session()
    errors = []

    events = session.query(HistoricalEvent).count()
    if events != 6:
        errors.append(f"Expected 6 events, got {events}")

    demand = session.query(DemandPlan).count()
    if demand < 800:
        errors.append(f"Expected ~864 demand plans, got {demand}")

    supply = session.query(SupplyPlan).count()
    if supply < 600:
        errors.append(f"Expected ~648 supply plans, got {supply}")

    movements = session.query(InventoryMovement).count()
    if movements < 1500:
        errors.append(f"Expected ~1944 movements, got {movements}")

    session.close()

    if errors:
        print("✗ Phase 4 validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase 4 validated")
        print(f"  - {events} events, {demand} demand, {supply} supply, {movements} movements")

if __name__ == "__main__":
    try:
        validate_phase4()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
