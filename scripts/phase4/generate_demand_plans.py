"""
Phase 4, Step 4.4: Generate Demand Plans
Creates 864 demand plans from cleaned Kaggle data (3 items × 4 regions × 72 months)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, DemandPlan, Item, LocationNode, Region, BucketType, PlanType, LocationType

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_demand_plans():
    """Generate 864 demand plans"""
    session = Session()

    # Get items and locations
    items = {i.code: i.id for i in session.query(Item).filter(Item.code.in_(['PARA500', 'IBUP400', 'AZITH500'])).all()}
    regions = {r.code: r.id for r in session.query(Region).all()}

    # Get one distributor per region (demand point)
    distributors = {}
    for region_code, region_id in regions.items():
        dist = session.query(LocationNode).filter(
            LocationNode.region_id == region_id,
            LocationNode.type == LocationType.DISTRIBUTOR
        ).first()
        if dist:
            distributors[region_code] = dist.id

    plans = []

    # Generate 72 months (2020-01 to 2025-12)
    start_date = date(2020, 1, 1)

    # Simple demand (user should replace with Kaggle data)
    BASE_DEMAND = {
        'PARA500': 100000,
        'IBUP400': 80000,
        'AZITH500': 20000
    }

    for month_offset in range(72):
        period_start = start_date + relativedelta(months=month_offset)
        period_end = period_start + relativedelta(months=1, days=-1)

        for item_code, item_id in items.items():
            for region_code, location_id in distributors.items():
                # Simple quantity (user should load from cleaned CSV)
                quantity = BASE_DEMAND[item_code]

                plans.append(DemandPlan(
                    id=uuid.uuid4(),
                    item_id=item_id,
                    location_id=location_id,
                    period_start=period_start,
                    period_end=period_end,
                    bucket_type=BucketType.MONTHLY,
                    plan_type=PlanType.HISTORICAL,
                    quantity=quantity,
                    created_by="generate_demand_plans.py",
                    is_active=True
                ))

    Base.metadata.create_all(engine)
    session.add_all(plans)
    session.commit()

    print(f"✓ Inserted {len(plans)} demand plans")
    session.close()

if __name__ == "__main__":
    try:
        generate_demand_plans()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
