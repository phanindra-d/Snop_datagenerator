"""
Phase 3, Step 3.3: Generate Optimization Constraints
Creates 8 optimization constraints
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, OptimizationConstraint, ConstraintType

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_optimization_constraints():
    """Generate 8 optimization constraints"""
    session = Session()

    constraints = []

    CONSTRAINTS_DATA = [
        ("OPT-001", "Max Production Cost Per Unit", ConstraintType.BUDGET, None, 5.00, "USD/unit"),
        ("OPT-002", "Max Transportation Cost Per Unit", ConstraintType.BUDGET, None, 0.50, "USD/unit"),
        ("OPT-003", "Min Service Level", ConstraintType.SERVICE_LEVEL, 95.0, None, "percent"),
        ("OPT-004", "Max Production Lead Time", ConstraintType.LEAD_TIME, None, 7.0, "days"),
        ("OPT-005", "Min Batch Size", ConstraintType.CAPACITY, 10000.0, None, "units"),
        ("OPT-006", "Max Order Cycle Time", ConstraintType.LEAD_TIME, None, 3.0, "days"),
        ("OPT-007", "Max Total Budget", ConstraintType.BUDGET, None, 1000000.0, "USD"),
        ("OPT-008", "Min Capacity Utilization", ConstraintType.CAPACITY, 70.0, None, "percent"),
    ]

    for code, name, c_type, min_val, max_val, unit in CONSTRAINTS_DATA:
        constraints.append(OptimizationConstraint(
            id=uuid.uuid4(),
            constraint_code=code,
            constraint_name=name,
            constraint_type=c_type,
            min_value=min_val,
            max_value=max_val,
            unit=unit,
            created_by="generate_optimization_constraints.py",
            is_active=True
        ))

    # Create table
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(constraints)
    session.commit()

    print(f"✓ Inserted {len(constraints)} optimization constraints")

    session.close()

if __name__ == "__main__":
    try:
        generate_optimization_constraints()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
