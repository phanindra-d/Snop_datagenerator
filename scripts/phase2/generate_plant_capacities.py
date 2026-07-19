"""
Phase 2, Step 2.3: Generate Plant Capacities
Creates 18 capacity records (6 plants/subcontractors × 3 SKUs)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, PlantCapacity, LocationNode, Item, LocationType, ItemType

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_plant_capacities():
    """Generate 18 plant capacities"""
    session = Session()

    # Get manufacturing locations (plants + subcontractors)
    plants = session.query(LocationNode).filter(LocationNode.type == LocationType.PLANT).all()
    subcontractors = session.query(LocationNode).filter(LocationNode.type == LocationType.SUBCONTRACTOR).all()

    # Get finished goods
    finished_goods = session.query(Item).filter(Item.type == ItemType.FINISHED_GOOD).all()

    capacities = []

    # Plant capacities (4 plants × 3 SKUs = 12)
    PLANT_CAPACITY_DATA = {
        "PARA500": 50000,  # units/day
        "IBUP400": 40000,
        "AZITH500": 10000
    }

    for plant in plants:
        for fg in finished_goods:
            capacities.append(PlantCapacity(
                id=uuid.uuid4(),
                location_id=plant.id,
                item_id=fg.id,
                capacity_per_day=PLANT_CAPACITY_DATA[fg.code],
                is_owned=True,  # Company plant
                outsourcing_premium=None,
                created_by="generate_plant_capacities.py",
                is_active=True
            ))

    # Subcontractor capacities (2 SC × 3 SKUs = 6)
    SC_CAPACITY_DATA = {
        "PARA500": 30000,  # Lower capacity than company plants
        "IBUP400": 25000,
        "AZITH500": 5000
    }

    for sc in subcontractors:
        for fg in finished_goods:
            capacities.append(PlantCapacity(
                id=uuid.uuid4(),
                location_id=sc.id,
                item_id=fg.id,
                capacity_per_day=SC_CAPACITY_DATA[fg.code],
                is_owned=False,  # Subcontractor
                outsourcing_premium=1.15,  # 15% cost premium
                created_by="generate_plant_capacities.py",
                is_active=True
            ))

    # Create table if not exists
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(capacities)
    session.commit()

    print(f"✓ Inserted {len(capacities)} plant capacities")
    print(f"  - Company plants: {len(plants) * len(finished_goods)}")
    print(f"  - Subcontractors: {len(subcontractors) * len(finished_goods)}")

    session.close()

if __name__ == "__main__":
    try:
        generate_plant_capacities()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
