"""
Phase 8, Step 8.1: Generate Users
Creates 20 users
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, UserRole, Region

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_users():
    session = Session()

    regions = {r.code: r.id for r in session.query(Region).all()}
    users = []

    USERS_DATA = [
        ("exec1@company.com", "John Executive", UserRole.EXECUTIVE, None),
        ("exec2@company.com", "Jane Director", UserRole.EXECUTIVE, None),
        ("exec3@company.com", "Bob VP", UserRole.EXECUTIVE, None),
        ("pm_north@company.com", "Alice Manager", UserRole.PLANT_MANAGER, "NORTH"),
        ("pm_east@company.com", "Carol Plant Manager", UserRole.PLANT_MANAGER, "EAST"),
        ("pm_west@company.com", "Dave PM", UserRole.PLANT_MANAGER, "WEST"),
        ("pm_south@company.com", "Eve Manager", UserRole.PLANT_MANAGER, "SOUTH"),
        ("sc_north@company.com", "Frank SC", UserRole.SC_MANAGER, "NORTH"),
        ("sc_east@company.com", "Grace SC", UserRole.SC_MANAGER, "EAST"),
        ("sc_west@company.com", "Henry SC", UserRole.SC_MANAGER, "WEST"),
        ("sc_south@company.com", "Irene SC", UserRole.SC_MANAGER, "SOUTH"),
        ("planner1@company.com", "Jack Planner", UserRole.DEMAND_PLANNER, None),
        ("planner2@company.com", "Kelly Planner", UserRole.DEMAND_PLANNER, None),
        ("planner3@company.com", "Leo Planner", UserRole.DEMAND_PLANNER, None),
        ("wh_north@company.com", "Mary WH", UserRole.WH_MANAGER, "NORTH"),
        ("wh_east@company.com", "Nancy WH", UserRole.WH_MANAGER, "EAST"),
        ("wh_west@company.com", "Oscar WH", UserRole.WH_MANAGER, "WEST"),
        ("wh_south@company.com", "Paul WH", UserRole.WH_MANAGER, "SOUTH"),
        ("analyst1@company.com", "Quinn Analyst", UserRole.ANALYST, None),
        ("analyst2@company.com", "Rachel Analyst", UserRole.ANALYST, None),
    ]

    for email, name, role, region_code in USERS_DATA:
        users.append(User(
            id=uuid.uuid4(), email=email, full_name=name, role=role,
            region_id=regions[region_code] if region_code else None,
            created_by="generate_users.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(users)
    session.commit()
    print(f"✓ Inserted {len(users)} users")
    session.close()

if __name__ == "__main__":
    try:
        generate_users()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
