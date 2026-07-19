"""
Phase 6, Step 6.1: Generate Inventory Provenance
Creates 56 provenance records (1 per inventory)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, InventoryProvenance, CurrentInventory, TrustLevel, VerificationMethod

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_inventory_provenance():
    session = Session()

    inventories = session.query(CurrentInventory).all()
    provenance = []

    for inv in inventories:
        provenance.append(InventoryProvenance(
            id=uuid.uuid4(), inventory_id=inv.id, data_source="WMS_system",
            trust_level=random.choice([TrustLevel.HIGH, TrustLevel.MEDIUM]),
            verification_method=random.choice([VerificationMethod.SYSTEM_COUNT, VerificationMethod.MANUAL_COUNT]),
            last_verified_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            verified_by="system", data_age_hours=random.randint(1, 24),
            created_by="generate_inventory_provenance.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(provenance)
    session.commit()
    print(f"✓ Inserted {len(provenance)} inventory provenance records")
    session.close()

if __name__ == "__main__":
    try:
        generate_inventory_provenance()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
