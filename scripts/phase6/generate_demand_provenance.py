"""
Phase 6, Step 6.2: Generate Demand Provenance
Creates 72 demand provenance records
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, DemandProvenance, DemandPlan, TrustLevel, ForecastMethod

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_demand_provenance():
    session = Session()

    demand_plans = session.query(DemandPlan).limit(72).all()
    provenance = []

    for dp in demand_plans:
        provenance.append(DemandProvenance(
            id=uuid.uuid4(), demand_plan_id=dp.id,
            forecast_method=random.choice([ForecastMethod.ML_MODEL, ForecastMethod.STATISTICAL]),
            trust_level=random.choice([TrustLevel.HIGH, TrustLevel.MEDIUM]),
            model_accuracy_pct=random.uniform(85.0, 98.0),
            overridden_by_planner=random.choice([True, False]),
            created_by="generate_demand_provenance.py", is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(provenance)
    session.commit()
    print(f"✓ Inserted {len(provenance)} demand provenance records")
    session.close()

if __name__ == "__main__":
    try:
        generate_demand_provenance()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
