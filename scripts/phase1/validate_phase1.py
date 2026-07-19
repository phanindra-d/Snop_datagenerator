"""
Phase 1 Validation
Verifies all Phase 1 data was inserted correctly
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Region, LocationNode, Item, ItemType, LocationType

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase1():
    """Validate Phase 1: Master Data"""
    session = Session()
    errors = []

    # Regions
    region_count = session.query(Region).count()
    if region_count != 4:
        errors.append(f"Expected 4 regions, got {region_count}")

    # Check all region codes exist
    region_codes = [r.code for r in session.query(Region.code).all()]
    expected_codes = ["NORTH", "EAST", "WEST", "SOUTH"]
    for code in expected_codes:
        if code not in region_codes:
            errors.append(f"Missing region: {code}")

    # Location Nodes
    location_count = session.query(LocationNode).count()
    if location_count != 18:
        errors.append(f"Expected 18 location nodes, got {location_count}")

    # Check location type counts
    type_counts = {
        LocationType.PLANT: 4,
        LocationType.SUBCONTRACTOR: 2,
        LocationType.WAREHOUSE_PLANT: 4,
        LocationType.WAREHOUSE_REGIONAL: 4,
        LocationType.DISTRIBUTOR: 4
    }

    for loc_type, expected_count in type_counts.items():
        actual_count = session.query(LocationNode).filter(LocationNode.type == loc_type).count()
        if actual_count != expected_count:
            errors.append(f"Expected {expected_count} {loc_type.value}, got {actual_count}")

    # Check all locations have region_id
    orphan_locations = session.query(LocationNode).filter(LocationNode.region_id == None).count()
    if orphan_locations > 0:
        errors.append(f"Found {orphan_locations} locations without region_id")

    # Items
    item_count = session.query(Item).count()
    if item_count != 11:
        errors.append(f"Expected 11 items, got {item_count}")

    # Check item type counts
    fg_count = session.query(Item).filter(Item.type == ItemType.FINISHED_GOOD).count()
    if fg_count != 3:
        errors.append(f"Expected 3 finished goods, got {fg_count}")

    rm_count = session.query(Item).filter(Item.type == ItemType.RAW_MATERIAL).count()
    if rm_count != 8:
        errors.append(f"Expected 8 raw materials, got {rm_count}")

    # Check all item codes unique
    item_codes = [i.code for i in session.query(Item.code).all()]
    if len(item_codes) != len(set(item_codes)):
        errors.append("Duplicate item codes found")

    session.close()

    # Report
    if errors:
        print("✗ Phase 1 validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase 1 validated successfully")
        print(f"  - {region_count} regions")
        print(f"  - {location_count} location nodes")
        print(f"  - {item_count} items")

if __name__ == "__main__":
    try:
        validate_phase1()
    except Exception as e:
        print(f"✗ VALIDATION ERROR: {e}")
        sys.exit(1)
