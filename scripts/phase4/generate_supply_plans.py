"""
Phase 4, Step 4.5: Generate Supply Plans
Creates 648 supply plans (3 items × 3 plants × 72 months)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, SupplyPlan, Item, LocationNode, LocationType, BucketType, PlanType

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_supply_plans():
    session = Session()

    items = {i.code: i.id for i in session.query(Item).filter(Item.code.in_(['PARA500', 'IBUP400', 'AZITH500'])).all()}
    plants = session.query(LocationNode).filter(LocationNode.type == LocationType.PLANT).limit(3).all()

    plans = []
    start_date = date(2020, 1, 1)
    BASE_SUPPLY = {'PARA500': 90000, 'IBUP400': 70000, 'AZITH500': 18000}

    for month_offset in range(72):
        period_start = start_date + relativedelta(months=month_offset)
        period_end = period_start + relativedelta(months=1, days=-1)
        for item_code, item_id in items.items():
            for plant in plants:
                plans.append(SupplyPlan(
                    id=uuid.uuid4(), item_id=item_id, location_id=plant.id,
                    period_start=period_start, period_end=period_end,
                    bucket_type=BucketType.MONTHLY, plan_type=PlanType.HISTORICAL,
                    quantity=BASE_SUPPLY[item_code], created_by="generate_supply_plans.py", is_active=True
                ))

    Base.metadata.create_all(engine)
    session.add_all(plans)
    session.commit()
    print(f"✓ Inserted {len(plans)} supply plans")
    session.close()

if __name__ == "__main__":
    try:
        generate_supply_plans()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
