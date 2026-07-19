"""
Phase 1, Step 1.1: Generate Regions
Creates 4 geographic regions (NORTH, EAST, WEST, SOUTH)
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, UUID
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Model
class Region(Base):
    __tablename__ = "regions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

def generate_regions():
    """Generate 4 regions"""
    session = Session()

    REGIONS = [
        {"code": "NORTH", "name": "North Region"},
        {"code": "EAST", "name": "East Region"},
        {"code": "WEST", "name": "West Region"},
        {"code": "SOUTH", "name": "South Region"}
    ]

    regions = []
    for r in REGIONS:
        regions.append(Region(
            id=uuid.uuid4(),
            code=r["code"],
            name=r["name"],
            created_by="generate_regions.py",
            is_active=True
        ))

    # Create table if not exists
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(regions)
    session.commit()

    print(f"✓ Inserted {len(regions)} regions")
    for r in regions:
        print(f"  - {r.code}: {r.name}")

    session.close()

if __name__ == "__main__":
    try:
        generate_regions()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
