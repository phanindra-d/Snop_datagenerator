"""
Phase 5, Step 5.1: Generate Current Inventory
Creates 56 current inventory records (24 FG + 32 RM)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, CurrentInventory, Item, LocationNode, ItemType, LocationType

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_current_inventory():
    session = Session()

    fg_items = session.query(Item).filter(Item.type == ItemType.FINISHED_GOOD).all()
    rm_items = session.query(Item).filter(Item.type == ItemType.RAW_MATERIAL).all()

    fg_warehouses = session.query(LocationNode).filter(LocationNode.type.in_([LocationType.WAREHOUSE_PLANT, LocationType.WAREHOUSE_REGIONAL])).all()
    rm_warehouses = session.query(LocationNode).filter(LocationNode.type == LocationType.WAREHOUSE_PLANT).all()

    inventory = []

    # FG inventory (3 items × 8 warehouses = 24)
    for item in fg_items:
        for warehouse in fg_warehouses:
            quantity = random.randint(5000, 50000) if item.volume_category and 'FAST' in str(item.volume_category) else random.randint(1000, 10000)
            inventory.append(CurrentInventory(
                id=uuid.uuid4(), item_id=item.id, location_id=warehouse.id,
                quantity_on_hand=quantity, last_updated=datetime.utcnow(),
                created_by="generate_current_inventory.py", is_active=True
            ))

    # RM inventory (8 items × 4 plant warehouses = 32)
    for item in rm_items:
        for warehouse in rm_warehouses:
            quantity = random.randint(500, 5000)
            inventory.append(CurrentInventory(
                id=uuid.uuid4(), item_id=item.id, location_id=warehouse.id,
                quantity_on_hand=quantity, last_updated=datetime.utcnow(),
                created_by="generate_current_inventory.py", is_active=True
            ))

    Base.metadata.create_all(engine)
    session.add_all(inventory)
    session.commit()
    print(f"✓ Inserted {len(inventory)} current inventory records")
    session.close()

if __name__ == "__main__":
    try:
        generate_current_inventory()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
