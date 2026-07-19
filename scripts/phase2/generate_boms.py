"""
Phase 2, Step 2.1: Generate BOMs
Creates 9 bill of materials (3 FG × 3 materials each)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, BOM, Item

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_boms():
    """Generate 9 BOMs"""
    session = Session()

    # Get item IDs
    items = {i.code: i.id for i in session.query(Item).all()}

    boms = []

    # BOM data: (parent, child, quantity_kg_per_unit)
    BOM_DATA = [
        # Paracetamol 500mg (3 materials)
        ("PARA500", "API-PARA", 0.0005),     # 500mg API
        ("PARA500", "EXC-STARCH", 0.00015),  # 150mg starch
        ("PARA500", "EXC-MCC", 0.0002),      # 200mg cellulose

        # Ibuprofen 400mg (3 materials)
        ("IBUP400", "API-IBUP", 0.0004),     # 400mg API
        ("IBUP400", "EXC-GELATIN", 0.0001),  # 100mg gelatin capsule
        ("IBUP400", "EXC-GLYCERIN", 0.00005), # 50mg glycerin

        # Azithromycin 500mg (3 materials)
        ("AZITH500", "API-AZITH", 0.0005),   # 500mg API
        ("AZITH500", "EXC-LACTOSE", 0.0002), # 200mg lactose
        ("AZITH500", "EXC-MCC", 0.0001)      # 100mg cellulose
    ]

    for parent_code, child_code, qty in BOM_DATA:
        boms.append(BOM(
            id=uuid.uuid4(),
            parent_item_id=items[parent_code],
            child_item_id=items[child_code],
            quantity_per_unit=qty,
            created_by="generate_boms.py",
            is_active=True
        ))

    # Create table if not exists
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(boms)
    session.commit()

    print(f"✓ Inserted {len(boms)} BOMs")
    for bom in boms:
        parent = session.query(Item).filter(Item.id == bom.parent_item_id).first()
        child = session.query(Item).filter(Item.id == bom.child_item_id).first()
        print(f"  - {parent.code} → {child.code}: {bom.quantity_per_unit}kg/unit")

    session.close()

if __name__ == "__main__":
    try:
        generate_boms()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
