"""
Phase 3, Step 3.1: Generate Inventory Rules
Creates 9 inventory rules (safety stock, max stock)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, InventoryRule, RuleType, LocationType

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_inventory_rules():
    """Generate 9 inventory rules"""
    session = Session()

    rules = []

    RULES_DATA = [
        # Safety stock rules
        ("INV-RULE-001", RuleType.SAFETY_STOCK, LocationType.WAREHOUSE_PLANT, 5, None),    # RM at plant WH
        ("INV-RULE-002", RuleType.SAFETY_STOCK, LocationType.WAREHOUSE_PLANT, 15, None),   # FAST FG at plant WH
        ("INV-RULE-003", RuleType.SAFETY_STOCK, LocationType.WAREHOUSE_REGIONAL, 15, None), # FAST FG at regional WH
        ("INV-RULE-004", RuleType.SAFETY_STOCK, LocationType.WAREHOUSE_PLANT, 5, None),    # SLOW FG at plant WH
        ("INV-RULE-005", RuleType.SAFETY_STOCK, LocationType.WAREHOUSE_REGIONAL, 5, None), # SLOW FG at regional WH

        # Max stock rules
        ("INV-RULE-006", RuleType.MAX_STOCK, LocationType.WAREHOUSE_REGIONAL, 30, None),   # FAST FG max
        ("INV-RULE-007", RuleType.MAX_STOCK, LocationType.WAREHOUSE_REGIONAL, 15, None),   # SLOW FG max
        ("INV-RULE-008", RuleType.MAX_STOCK, LocationType.WAREHOUSE_PLANT, 15, None),      # RM max

        # Reorder point
        ("INV-RULE-009", RuleType.REORDER_POINT, LocationType.WAREHOUSE_REGIONAL, 7, None) # Generic reorder
    ]

    for rule_code, rule_type, loc_type, min_days, max_days in RULES_DATA:
        rules.append(InventoryRule(
            id=uuid.uuid4(),
            rule_code=rule_code,
            rule_type=rule_type,
            location_type=loc_type,
            min_days_supply=min_days if rule_type == RuleType.SAFETY_STOCK else None,
            max_days_supply=max_days if rule_type == RuleType.MAX_STOCK else min_days,
            created_by="generate_inventory_rules.py",
            is_active=True
        ))

    # Create table
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(rules)
    session.commit()

    print(f"✓ Inserted {len(rules)} inventory rules")
    print(f"  - Safety stock rules: {sum(1 for r in rules if r.rule_type == RuleType.SAFETY_STOCK)}")
    print(f"  - Max stock rules: {sum(1 for r in rules if r.rule_type == RuleType.MAX_STOCK)}")

    session.close()

if __name__ == "__main__":
    try:
        generate_inventory_rules()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
