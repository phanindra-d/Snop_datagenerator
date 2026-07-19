"""
Phase 4, Step 4.6: Generate Inventory Movements
Creates 1944 inventory movements (warehouse transfers)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, InventoryMovement, Item, LocationNode, LocationType, MovementType

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_inventory_movements():
    session = Session()

    items = session.query(Item).filter(Item.code.in_(['PARA500', 'IBUP400', 'AZITH500'])).all()
    warehouses = session.query(LocationNode).filter(LocationNode.type.in_([LocationType.WAREHOUSE_PLANT, LocationType.WAREHOUSE_REGIONAL])).all()

    movements = []
    start_date = date(2023, 1, 1)

    # Generate ~1944 movements over 36 months
    for day_offset in range(0, 1095, 2):  # Every 2 days
        movement_date = start_date + timedelta(days=day_offset)
        for item in items:
            warehouse = random.choice(warehouses)
            quantity = random.randint(1000, 10000)
            movements.append(InventoryMovement(
                id=uuid.uuid4(), item_id=item.id, location_id=warehouse.id,
                movement_type=random.choice([MovementType.TRANSFER_IN, MovementType.TRANSFER_OUT]),
                quantity=quantity, movement_date=movement_date,
                created_by="generate_inventory_movements.py", is_active=True
            ))

    Base.metadata.create_all(engine)
    session.add_all(movements)
    session.commit()
    print(f"✓ Inserted {len(movements)} inventory movements")
    session.close()

if __name__ == "__main__":
    try:
        generate_inventory_movements()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
