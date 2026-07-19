"""
Phase 1, Step 1.2: Generate Location Nodes
Creates 18 location nodes (plants, subcontractors, warehouses, distributors)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LocationNode, Region, LocationType

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_location_nodes():
    """Generate 18 location nodes"""
    session = Session()

    # Get region IDs
    regions = {r.code: r.id for r in session.query(Region).all()}

    locations = []

    # Plants (4)
    PLANTS = [
        {"name": "Plant North Alpha", "region": "NORTH", "lat": 44.9778, "lon": -93.2650},
        {"name": "Plant East Beta", "region": "EAST", "lat": 42.3601, "lon": -71.0589},
        {"name": "Plant West Gamma", "region": "WEST", "lat": 34.0522, "lon": -118.2437},
        {"name": "Plant South Delta", "region": "SOUTH", "lat": 33.7490, "lon": -84.3880}
    ]

    for p in PLANTS:
        locations.append(LocationNode(
            id=uuid.uuid4(),
            name=p["name"],
            type=LocationType.PLANT,
            region_id=regions[p["region"]],
            latitude=p["lat"],
            longitude=p["lon"],
            created_by="generate_location_nodes.py",
            is_active=True
        ))

    # Subcontractors (2)
    SUBCONTRACTORS = [
        {"name": "SubContractor NorthEast Co.", "region": "NORTH"},
        {"name": "SubContractor SouthWest Ltd.", "region": "SOUTH"}
    ]

    for sc in SUBCONTRACTORS:
        locations.append(LocationNode(
            id=uuid.uuid4(),
            name=sc["name"],
            type=LocationType.SUBCONTRACTOR,
            region_id=regions[sc["region"]],
            created_by="generate_location_nodes.py",
            is_active=True
        ))

    # Plant Warehouses (4) - co-located with plants
    plants = [loc for loc in locations if loc.type == LocationType.PLANT]
    for plant in plants:
        locations.append(LocationNode(
            id=uuid.uuid4(),
            name=f"{plant.name} - Warehouse",
            type=LocationType.WAREHOUSE_PLANT,
            region_id=plant.region_id,
            latitude=plant.latitude,
            longitude=plant.longitude,
            created_by="generate_location_nodes.py",
            is_active=True
        ))

    # Regional Warehouses (4)
    REGIONAL_WH = [
        {"name": "Regional WH North", "region": "NORTH", "lat": 45.5152, "lon": -122.6784},
        {"name": "Regional WH East", "region": "EAST", "lat": 40.7128, "lon": -74.0060},
        {"name": "Regional WH West", "region": "WEST", "lat": 37.7749, "lon": -122.4194},
        {"name": "Regional WH South", "region": "SOUTH", "lat": 25.7617, "lon": -80.1918}
    ]

    for wh in REGIONAL_WH:
        locations.append(LocationNode(
            id=uuid.uuid4(),
            name=wh["name"],
            type=LocationType.WAREHOUSE_REGIONAL,
            region_id=regions[wh["region"]],
            latitude=wh["lat"],
            longitude=wh["lon"],
            created_by="generate_location_nodes.py",
            is_active=True
        ))

    # Distributors (4)
    DISTRIBUTORS = [
        {"name": "North Pharma Distributors", "region": "NORTH"},
        {"name": "East Medical Supply Corp", "region": "EAST"},
        {"name": "West HealthCare Logistics", "region": "WEST"},
        {"name": "South MedChain Distribution", "region": "SOUTH"}
    ]

    for dist in DISTRIBUTORS:
        locations.append(LocationNode(
            id=uuid.uuid4(),
            name=dist["name"],
            type=LocationType.DISTRIBUTOR,
            region_id=regions[dist["region"]],
            created_by="generate_location_nodes.py",
            is_active=True
        ))

    # Create table if not exists
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(locations)
    session.commit()

    print(f"✓ Inserted {len(locations)} location nodes")
    print(f"  - Plants: {sum(1 for loc in locations if loc.type == LocationType.PLANT)}")
    print(f"  - Subcontractors: {sum(1 for loc in locations if loc.type == LocationType.SUBCONTRACTOR)}")
    print(f"  - Plant Warehouses: {sum(1 for loc in locations if loc.type == LocationType.WAREHOUSE_PLANT)}")
    print(f"  - Regional Warehouses: {sum(1 for loc in locations if loc.type == LocationType.WAREHOUSE_REGIONAL)}")
    print(f"  - Distributors: {sum(1 for loc in locations if loc.type == LocationType.DISTRIBUTOR)}")

    session.close()

if __name__ == "__main__":
    try:
        generate_location_nodes()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
