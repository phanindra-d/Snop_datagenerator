"""
Phase 4, Step 4.3: Generate Historical Events
Creates 6 historical events (COVID, flu seasons, etc.)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, HistoricalEvent, EventType

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_historical_events():
    """Generate 6 historical events"""
    session = Session()

    events = []

    EVENTS_DATA = [
        ("EVENT-COVID19", "COVID-19 Pandemic", EventType.PANDEMIC, date(2020, 3, 1), date(2021, 12, 31), '["PARA500"]', '["NORTH","EAST","WEST","SOUTH"]', "COVID pandemic drove 200% spike in analgesic demand", 2.0, 1.0),
        ("EVENT-FLU2021Q4", "Flu Season 2021-Q4", EventType.SEASONAL, date(2021, 10, 1), date(2022, 2, 28), '["PARA500","IBUP400"]', '["NORTH","EAST","WEST","SOUTH"]', "Seasonal flu outbreak", 1.25, 1.0),
        ("EVENT-SUPPLY2021", "Supply Chain Crisis", EventType.SUPPLY_DISRUPTION, date(2021, 8, 1), date(2021, 11, 30), '["PARA500","IBUP400","AZITH500"]', '["NORTH","EAST","WEST","SOUTH"]', "Supply chain bottlenecks reduced production", 1.0, 0.7),
        ("EVENT-FLU2022Q4", "Flu Season 2022-Q4", EventType.SEASONAL, date(2022, 10, 1), date(2023, 2, 28), '["PARA500","IBUP400"]', '["NORTH","EAST","WEST","SOUTH"]', "Seasonal flu outbreak", 1.25, 1.0),
        ("EVENT-UKRAINE2022", "Russia-Ukraine War", EventType.GEOPOLITICAL, date(2022, 2, 24), None, '["PARA500","IBUP400"]', '["NORTH","EAST","WEST","SOUTH"]', "Geopolitical disruption affected raw material supply", 1.0, 0.85),
        ("EVENT-FLU2023Q4", "Flu Season 2023-Q4", EventType.SEASONAL, date(2023, 10, 1), date(2024, 2, 28), '["PARA500","IBUP400"]', '["NORTH","EAST","WEST","SOUTH"]', "Seasonal flu outbreak", 1.25, 1.0),
    ]

    for code, name, event_type, start, end, items, regions, desc, demand_mult, supply_mult in EVENTS_DATA:
        events.append(HistoricalEvent(
            id=uuid.uuid4(),
            event_code=code,
            event_name=name,
            event_type=event_type,
            start_date=start,
            end_date=end,
            affected_items=items,
            affected_regions=regions,
            impact_description=desc,
            demand_impact_multiplier=demand_mult,
            supply_impact_multiplier=supply_mult,
            created_by="generate_historical_events.py",
            is_active=True
        ))

    Base.metadata.create_all(engine)
    session.add_all(events)
    session.commit()

    print(f"✓ Inserted {len(events)} historical events")
    session.close()

if __name__ == "__main__":
    try:
        generate_historical_events()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
