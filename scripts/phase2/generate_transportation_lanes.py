"""
Phase 2, Step 2.2: Generate Transportation Lanes
Creates 24 transportation lanes (shipping routes between locations)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TransportationLane, LocationNode, Region, LocationType

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_transportation_lanes():
    """Generate 24 transportation lanes"""
    session = Session()

    # Get all locations grouped by region and type
    locations = session.query(LocationNode).all()
    regions = session.query(Region).all()

    lanes = []

    for region in regions:
        # Get locations in this region
        plant = next((l for l in locations if l.region_id == region.id and l.type == LocationType.PLANT), None)
        plant_wh = next((l for l in locations if l.region_id == region.id and l.type == LocationType.WAREHOUSE_PLANT), None)
        regional_wh = next((l for l in locations if l.region_id == region.id and l.type == LocationType.WAREHOUSE_REGIONAL), None)
        distributor = next((l for l in locations if l.region_id == region.id and l.type == LocationType.DISTRIBUTOR), None)

        if not all([plant, plant_wh, regional_wh, distributor]):
            continue

        # Primary path: Plant → Plant WH → Regional WH → Distributor
        lanes.append(TransportationLane(
            id=uuid.uuid4(),
            from_location_id=plant.id,
            to_location_id=plant_wh.id,
            transit_time_days=0,  # Same location
            cost_per_unit=0.10,
            mode="INTERNAL",
            created_by="generate_transportation_lanes.py",
            is_active=True
        ))

        lanes.append(TransportationLane(
            id=uuid.uuid4(),
            from_location_id=plant_wh.id,
            to_location_id=regional_wh.id,
            transit_time_days=2,
            cost_per_unit=2.50,
            mode="TRUCK",
            created_by="generate_transportation_lanes.py",
            is_active=True
        ))

        lanes.append(TransportationLane(
            id=uuid.uuid4(),
            from_location_id=regional_wh.id,
            to_location_id=distributor.id,
            transit_time_days=1,
            cost_per_unit=1.00,
            mode="TRUCK",
            created_by="generate_transportation_lanes.py",
            is_active=True
        ))

        # Direct routes (bypass)
        lanes.append(TransportationLane(
            id=uuid.uuid4(),
            from_location_id=plant.id,
            to_location_id=regional_wh.id,
            transit_time_days=2,
            cost_per_unit=2.30,
            mode="TRUCK",
            created_by="generate_transportation_lanes.py",
            is_active=True
        ))

        lanes.append(TransportationLane(
            id=uuid.uuid4(),
            from_location_id=plant.id,
            to_location_id=distributor.id,
            transit_time_days=3,
            cost_per_unit=5.00,
            mode="EXPRESS",
            created_by="generate_transportation_lanes.py",
            is_active=True
        ))

    # Subcontractor lanes (SC → Regional WHs they serve)
    subcontractors = [l for l in locations if l.type == LocationType.SUBCONTRACTOR]

    # SC NorthEast serves NORTH + EAST
    sc_ne = next((sc for sc in subcontractors if "NorthEast" in sc.name), None)
    if sc_ne:
        for region_code in ["NORTH", "EAST"]:
            region = next((r for r in regions if r.code == region_code), None)
            if region:
                regional_wh = next((l for l in locations if l.region_id == region.id and l.type == LocationType.WAREHOUSE_REGIONAL), None)
                if regional_wh:
                    lanes.append(TransportationLane(
                        id=uuid.uuid4(),
                        from_location_id=sc_ne.id,
                        to_location_id=regional_wh.id,
                        transit_time_days=3,
                        cost_per_unit=3.50,
                        mode="TRUCK",
                        created_by="generate_transportation_lanes.py",
                        is_active=True
                    ))

    # SC SouthWest serves SOUTH + WEST
    sc_sw = next((sc for sc in subcontractors if "SouthWest" in sc.name), None)
    if sc_sw:
        for region_code in ["SOUTH", "WEST"]:
            region = next((r for r in regions if r.code == region_code), None)
            if region:
                regional_wh = next((l for l in locations if l.region_id == region.id and l.type == LocationType.WAREHOUSE_REGIONAL), None)
                if regional_wh:
                    lanes.append(TransportationLane(
                        id=uuid.uuid4(),
                        from_location_id=sc_sw.id,
                        to_location_id=regional_wh.id,
                        transit_time_days=3,
                        cost_per_unit=3.50,
                        mode="TRUCK",
                        created_by="generate_transportation_lanes.py",
                        is_active=True
                    ))

    # Create table if not exists
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(lanes)
    session.commit()

    print(f"✓ Inserted {len(lanes)} transportation lanes")
    print(f"  - Primary paths (4 regions × 3 lanes): {4 * 3}")
    print(f"  - Direct routes (4 regions × 2 lanes): {4 * 2}")
    print(f"  - Subcontractor lanes: {len(lanes) - 20}")

    session.close()

if __name__ == "__main__":
    try:
        generate_transportation_lanes()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
