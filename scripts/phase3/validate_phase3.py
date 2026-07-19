"""
Phase 3 Validation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import InventoryRule, ValidationRule, OptimizationConstraint

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase3():
    session = Session()
    errors = []

    inv_rules = session.query(InventoryRule).count()
    if inv_rules != 9:
        errors.append(f"Expected 9 inventory rules, got {inv_rules}")

    val_rules = session.query(ValidationRule).count()
    if val_rules != 15:
        errors.append(f"Expected 15 validation rules, got {val_rules}")

    opt_constraints = session.query(OptimizationConstraint).count()
    if opt_constraints != 8:
        errors.append(f"Expected 8 optimization constraints, got {opt_constraints}")

    session.close()

    if errors:
        print("✗ Phase 3 validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase 3 validated")
        print(f"  - {inv_rules} inventory rules")
        print(f"  - {val_rules} validation rules")
        print(f"  - {opt_constraints} optimization constraints")

if __name__ == "__main__":
    try:
        validate_phase3()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
