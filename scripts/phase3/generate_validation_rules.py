"""
Phase 3, Step 3.2: Generate Validation Rules
Creates 15 validation rules (data quality checks)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ValidationRule, ValidationType

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_validation_rules():
    """Generate 15 validation rules"""
    session = Session()

    rules = []

    RULES_DATA = [
        ("VAL-001", "BOM Quantity Positive", ValidationType.RANGE_CHECK, "boms", "quantity_per_unit > 0", "BOM quantity must be positive", "ERROR"),
        ("VAL-002", "BOM Quantity Realistic", ValidationType.RANGE_CHECK, "boms", "quantity_per_unit < 0.01", "BOM quantity too large (>10g per tablet)", "ERROR"),
        ("VAL-003", "Inventory Non-Negative", ValidationType.RANGE_CHECK, "current_inventory", "quantity_on_hand >= 0", "Inventory cannot be negative", "ERROR"),
        ("VAL-004", "Transit Time Non-Negative", ValidationType.RANGE_CHECK, "transportation_lanes", "transit_time_days >= 0", "Transit time cannot be negative", "ERROR"),
        ("VAL-005", "Capacity Positive", ValidationType.RANGE_CHECK, "plant_capacities", "capacity_per_day > 0", "Plant capacity must be positive", "ERROR"),
        ("VAL-006", "Region Code Valid", ValidationType.MANDATORY_FIELD, "regions", "code IN ('NORTH','EAST','WEST','SOUTH')", "Invalid region code", "ERROR"),
        ("VAL-007", "Item Code Unique", ValidationType.RELATIONSHIP_CHECK, "items", "COUNT(*) = COUNT(DISTINCT code)", "Duplicate item codes", "ERROR"),
        ("VAL-008", "Location Has Region", ValidationType.MANDATORY_FIELD, "location_nodes", "region_id IS NOT NULL", "Location must have region", "ERROR"),
        ("VAL-009", "Safety Stock Reasonable", ValidationType.RANGE_CHECK, "inventory_rules", "min_days_supply BETWEEN 1 AND 60", "Safety stock days out of range", "WARNING"),
        ("VAL-010", "BOM No Circular Dependency", ValidationType.BUSINESS_LOGIC, "boms", "parent_item_id != child_item_id", "BOM circular dependency", "ERROR"),
        ("VAL-011", "Lane No Self-Loop", ValidationType.BUSINESS_LOGIC, "transportation_lanes", "from_location_id != to_location_id", "Lane self-loop detected", "ERROR"),
        ("VAL-012", "Demand Quantity Positive", ValidationType.RANGE_CHECK, "demand_plans", "quantity > 0", "Demand must be positive", "ERROR"),
        ("VAL-013", "Supply Quantity Positive", ValidationType.RANGE_CHECK, "supply_plans", "quantity > 0", "Supply must be positive", "ERROR"),
        ("VAL-014", "Period Start Before End", ValidationType.BUSINESS_LOGIC, "demand_plans", "period_start < period_end", "Period start must be before end", "ERROR"),
        ("VAL-015", "Trust Level Valid", ValidationType.MANDATORY_FIELD, "inventory_provenance", "trust_level IN ('high','medium','low')", "Invalid trust level", "ERROR"),
    ]

    for code, name, val_type, table, condition, message, severity in RULES_DATA:
        rules.append(ValidationRule(
            id=uuid.uuid4(),
            rule_code=code,
            rule_name=name,
            validation_type=val_type,
            target_table=table,
            condition_sql=condition,
            error_message=message,
            severity=severity,
            created_by="generate_validation_rules.py",
            is_active=True
        ))

    # Create table
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(rules)
    session.commit()

    print(f"✓ Inserted {len(rules)} validation rules")

    session.close()

if __name__ == "__main__":
    try:
        generate_validation_rules()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
