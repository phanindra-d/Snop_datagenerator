"""
Phase 1, Step 1.3: Generate Items
Creates 11 items (3 finished goods + 8 raw materials)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Item, ItemType, SKUCategory

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_items():
    """Generate 11 items (3 FG + 8 RM)"""
    session = Session()

    items = []

    # Finished Goods (3)
    FINISHED_GOODS = [
        {
            "code": "PARA500",
            "name": "Paracetamol 500mg Tablets",
            "type": ItemType.FINISHED_GOOD,
            "volume_category": SKUCategory.FAST,
            "uom": "EA"
        },
        {
            "code": "IBUP400",
            "name": "Ibuprofen 400mg Capsules",
            "type": ItemType.FINISHED_GOOD,
            "volume_category": SKUCategory.FAST,
            "uom": "EA"
        },
        {
            "code": "AZITH500",
            "name": "Azithromycin 500mg Tablets",
            "type": ItemType.FINISHED_GOOD,
            "volume_category": SKUCategory.SLOW,
            "uom": "EA"
        }
    ]

    for fg in FINISHED_GOODS:
        items.append(Item(
            id=uuid.uuid4(),
            code=fg["code"],
            name=fg["name"],
            type=fg["type"],
            volume_category=fg["volume_category"],
            unit_of_measure=fg["uom"],
            created_by="generate_items.py",
            is_active=True
        ))

    # Raw Materials (8)
    RAW_MATERIALS = [
        {"code": "API-PARA", "name": "Paracetamol API (Active Pharmaceutical Ingredient)", "uom": "KG"},
        {"code": "API-IBUP", "name": "Ibuprofen API", "uom": "KG"},
        {"code": "API-AZITH", "name": "Azithromycin API", "uom": "KG"},
        {"code": "EXC-STARCH", "name": "Corn Starch (Binder/Disintegrant)", "uom": "KG"},
        {"code": "EXC-MCC", "name": "Microcrystalline Cellulose (Filler)", "uom": "KG"},
        {"code": "EXC-GELATIN", "name": "Gelatin (Capsule)", "uom": "KG"},
        {"code": "EXC-GLYCERIN", "name": "Glycerin", "uom": "L"},
        {"code": "EXC-LACTOSE", "name": "Lactose Monohydrate", "uom": "KG"}
    ]

    for rm in RAW_MATERIALS:
        items.append(Item(
            id=uuid.uuid4(),
            code=rm["code"],
            name=rm["name"],
            type=ItemType.RAW_MATERIAL,
            unit_of_measure=rm["uom"],
            created_by="generate_items.py",
            is_active=True
        ))

    # Create table if not exists
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(items)
    session.commit()

    print(f"✓ Inserted {len(items)} items")
    print(f"  - Finished Goods: {sum(1 for i in items if i.type == ItemType.FINISHED_GOOD)}")
    print(f"    - FAST SKUs: {sum(1 for i in items if i.volume_category == SKUCategory.FAST)}")
    print(f"    - SLOW SKUs: {sum(1 for i in items if i.volume_category == SKUCategory.SLOW)}")
    print(f"  - Raw Materials: {sum(1 for i in items if i.type == ItemType.RAW_MATERIAL)}")

    session.close()

if __name__ == "__main__":
    try:
        generate_items()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
