"""
Phase 6 Validation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import InventoryProvenance, DemandProvenance, ManualAdjustment

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase6():
    session = Session()
    errors = []

    inv_prov = session.query(InventoryProvenance).count()
    if inv_prov != 56:
        errors.append(f"Expected 56 inventory provenance, got {inv_prov}")

    demand_prov = session.query(DemandProvenance).count()
    if demand_prov != 72:
        errors.append(f"Expected 72 demand provenance, got {demand_prov}")

    adjustments = session.query(ManualAdjustment).count()
    if adjustments != 20:
        errors.append(f"Expected 20 adjustments, got {adjustments}")

    session.close()

    if errors:
        print("✗ Phase 6 validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase 6 validated")
        print(f"  - {inv_prov} inv prov, {demand_prov} demand prov, {adjustments} adjustments")

if __name__ == "__main__":
    try:
        validate_phase6()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
