"""
Phase 2 Validation
Verifies all Phase 2 data was inserted correctly
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import BOM, TransportationLane, PlantCapacity

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase2():
    """Validate Phase 2: Relationships"""
    session = Session()
    errors = []

    # BOMs
    bom_count = session.query(BOM).count()
    if bom_count != 9:
        errors.append(f"Expected 9 BOMs, got {bom_count}")

    # All BOM quantities > 0
    invalid_qty = session.query(BOM).filter(BOM.quantity_per_unit <= 0).count()
    if invalid_qty > 0:
        errors.append(f"Found {invalid_qty} BOMs with invalid quantity (<=0)")

    # Transportation Lanes
    lane_count = session.query(TransportationLane).count()
    if lane_count < 20:  # At least 20 lanes
        errors.append(f"Expected >=20 transportation lanes, got {lane_count}")

    # No self-loops
    self_loops = session.query(TransportationLane).filter(
        TransportationLane.from_location_id == TransportationLane.to_location_id
    ).count()
    if self_loops > 0:
        errors.append(f"Found {self_loops} self-loop lanes (from == to)")

    # All transit times >= 0
    negative_transit = session.query(TransportationLane).filter(
        TransportationLane.transit_time_days < 0
    ).count()
    if negative_transit > 0:
        errors.append(f"Found {negative_transit} lanes with negative transit time")

    # Plant Capacities
    capacity_count = session.query(PlantCapacity).count()
    if capacity_count != 18:
        errors.append(f"Expected 18 plant capacities, got {capacity_count}")

    # All capacities > 0
    zero_capacity = session.query(PlantCapacity).filter(
        PlantCapacity.capacity_per_day <= 0
    ).count()
    if zero_capacity > 0:
        errors.append(f"Found {zero_capacity} capacities with invalid value (<=0)")

    session.close()

    # Report
    if errors:
        print("✗ Phase 2 validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase 2 validated successfully")
        print(f"  - {bom_count} BOMs")
        print(f"  - {lane_count} transportation lanes")
        print(f"  - {capacity_count} plant capacities")

if __name__ == "__main__":
    try:
        validate_phase2()
    except Exception as e:
        print(f"✗ VALIDATION ERROR: {e}")
        sys.exit(1)
