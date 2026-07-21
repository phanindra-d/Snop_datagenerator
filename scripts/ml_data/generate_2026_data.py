"""
Generate 2026 data for future prediction demo

Context:
- Jan-Mar 2026: Normal months (already happened)
- April 2026 Week 1: SURGE spike (just ended - demo point)
- April 2026 Week 2-4: Future (to be predicted by ML)

Demo Date: April 7, 2026 (Monday, Week 1 just ended)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
import numpy as np

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_item_and_location_ids(session):
    """Get IDs for products and locations"""

    query = text("""
        SELECT
            i.id as item_id,
            i.code as item_code,
            ln.id as location_id,
            r.code as region_code
        FROM items i
        CROSS JOIN location_nodes ln
        JOIN regions r ON ln.region_id = r.id
        WHERE i.type = 'FINISHED_GOOD'
          AND ln.type = 'WAREHOUSE_REGIONAL'
        ORDER BY i.code, r.code
    """)

    result = session.execute(query)
    return result.fetchall()

def generate_monthly_demand_plans(session, year=2026, months=[1,2,3,4]):
    """Generate monthly demand plans for 2026"""

    print(f"\nGenerating monthly demand plans for {year} ({len(months)} months)...")

    combos = get_item_and_location_ids(session)
    records = []

    for month in months:
        period_start = datetime(year, month, 1).date()

        # Calculate period end (last day of month)
        if month == 12:
            period_end = datetime(year, 12, 31).date()
        else:
            period_end = (datetime(year, month + 1, 1) - timedelta(days=1)).date()

        for combo in combos:
            # Normal baseline demand (similar to 2025)
            if combo.item_code == 'PARA500':
                base_qty = 12000
            elif combo.item_code == 'IBUP400':
                base_qty = 9000
            else:  # AZITH500
                base_qty = 3000

            # Add random variation ±5%
            quantity = int(base_qty * np.random.uniform(0.95, 1.05))

            records.append({
                'id': uuid.uuid4(),
                'item_id': combo.item_id,
                'location_id': combo.location_id,
                'period_start': period_start,
                'period_end': period_end,
                'quantity': quantity,
                'plan_type': 'HISTORICAL',
                'created_by': 'generate_2026_data.py',
                'is_active': True
            })

    # Insert
    insert_query = text("""
        INSERT INTO demand_plans (
            id, item_id, location_id, period_start, period_end,
            quantity, plan_type, created_by, is_active, created_at, updated_at
        ) VALUES (
            :id, :item_id, :location_id, :period_start, :period_end,
            :quantity, :plan_type, :created_by, :is_active, NOW(), NOW()
        )
    """)

    for record in records:
        session.execute(insert_query, record)

    session.commit()
    print(f"✓ Inserted {len(records)} monthly demand plans")

def generate_weekly_actuals(session, year=2026):
    """Generate weekly actuals for Jan-Mar (normal) + April Week 1 (surge)"""

    print(f"\nGenerating weekly actuals for {year}...")

    combos = get_item_and_location_ids(session)
    records = []

    # Jan-Mar: Normal months (12 weeks)
    for month in [1, 2, 3]:
        month_start = datetime(year, month, 1).date()

        for combo in combos:
            # Get monthly plan
            if combo.item_code == 'PARA500':
                monthly_qty = 12000
            elif combo.item_code == 'IBUP400':
                monthly_qty = 9000
            else:
                monthly_qty = 3000

            weekly_base = monthly_qty / 4

            # Generate 4 normal weeks (±10% variation)
            for week_num in range(1, 5):
                week_start = month_start + timedelta(days=(week_num - 1) * 7)
                week_end = week_start + timedelta(days=6)

                forecast_qty = int(weekly_base)
                actual_qty = int(weekly_base * np.random.uniform(0.90, 1.10))
                deviation = ((actual_qty - forecast_qty) / forecast_qty * 100)
                is_surge = abs(deviation) > 25

                records.append({
                    'id': uuid.uuid4(),
                    'item_id': combo.item_id,
                    'location_id': combo.location_id,
                    'week_start_date': week_start,
                    'week_end_date': week_end,
                    'week_number': week_num,
                    'forecast_quantity': forecast_qty,
                    'actual_quantity': actual_qty,
                    'deviation_pct': deviation,
                    'is_surge': is_surge,
                    'created_by': 'generate_2026_data.py',
                    'is_active': True
                })

    # April Week 1: SURGE (demo point)
    april_start = datetime(year, 4, 1).date()

    for combo in combos:
        if combo.item_code == 'PARA500':
            monthly_qty = 12000
        elif combo.item_code == 'IBUP400':
            monthly_qty = 9000
        else:
            monthly_qty = 3000

        weekly_base = monthly_qty / 4

        # Week 1: SURGE +45% (NEW pattern for demo)
        week_start = april_start
        week_end = week_start + timedelta(days=6)

        forecast_qty = int(weekly_base)

        # SURGE: +45% spike (PARA500 NORTH gets biggest spike)
        if combo.item_code == 'PARA500' and combo.region_code == 'NORTH':
            actual_qty = int(weekly_base * 1.45)  # 5,200 units
        else:
            actual_qty = int(weekly_base * np.random.uniform(1.30, 1.40))

        deviation = ((actual_qty - forecast_qty) / forecast_qty * 100)
        is_surge = True

        records.append({
            'id': uuid.uuid4(),
            'item_id': combo.item_id,
            'location_id': combo.location_id,
            'week_start_date': week_start,
            'week_end_date': week_end,
            'week_number': 1,
            'forecast_quantity': forecast_qty,
            'actual_quantity': actual_qty,
            'deviation_pct': deviation,
            'is_surge': is_surge,
            'created_by': 'generate_2026_data.py',
            'is_active': True
        })

    # Insert
    insert_query = text("""
        INSERT INTO weekly_demand_actuals (
            id, item_id, location_id, week_start_date, week_end_date,
            week_number, forecast_quantity, actual_quantity, deviation_pct,
            is_surge, created_by, is_active, created_at, updated_at
        ) VALUES (
            :id, :item_id, :location_id, :week_start_date, :week_end_date,
            :week_number, :forecast_quantity, :actual_quantity, :deviation_pct,
            :is_surge, :created_by, :is_active, NOW(), NOW()
        )
    """)

    for record in records:
        session.execute(insert_query, record)

    session.commit()
    print(f"✓ Inserted {len(records)} weekly actuals")
    print(f"  - Jan-Mar: {len(records) - len(combos)} normal weeks")
    print(f"  - Apr Week 1: {len(combos)} surge weeks")

def verify_data(session):
    """Verify 2026 data"""

    print("\n" + "="*60)
    print("Verification: 2026 Data")
    print("="*60)

    # Check April Week 1 PARA500 NORTH
    query = text("""
        SELECT
            i.code,
            r.code as region,
            wda.week_start_date,
            wda.forecast_quantity,
            wda.actual_quantity,
            wda.deviation_pct,
            wda.is_surge
        FROM weekly_demand_actuals wda
        JOIN items i ON wda.item_id = i.id
        JOIN location_nodes ln ON wda.location_id = ln.id
        JOIN regions r ON ln.region_id = r.id
        WHERE i.code = 'PARA500'
          AND r.code = 'NORTH'
          AND wda.week_start_date = '2026-04-01'
    """)

    result = session.execute(query).fetchone()

    if result:
        print(f"\n✓ April 2026 Week 1 (DEMO POINT):")
        print(f"  Product: {result.code}")
        print(f"  Region: {result.region}")
        print(f"  Date: {result.week_start_date}")
        print(f"  Forecast: {result.forecast_quantity:,}")
        print(f"  Actual: {result.actual_quantity:,}")
        print(f"  Deviation: {result.deviation_pct:+.1f}%")
        print(f"  Surge: {'YES' if result.is_surge else 'No'}")
    else:
        print("\n✗ ERROR: April Week 1 data not found!")

    # Count total 2026 records
    count_query = text("""
        SELECT COUNT(*) FROM weekly_demand_actuals
        WHERE week_start_date >= '2026-01-01'
          AND week_start_date < '2026-05-01'
    """)

    count = session.execute(count_query).scalar()
    print(f"\n✓ Total 2026 weekly records: {count}")
    print(f"  Expected: {12 * 13} (3 products × 4 regions × 13 weeks)")

def main():
    print("="*60)
    print("Generate 2026 Future Data")
    print("="*60)
    print("\nStrategy:")
    print("  - Jan-Mar 2026: Normal (context)")
    print("  - Apr 2026 Week 1: SURGE (demo point)")
    print("  - Apr Week 2-4: Future (ML predicts)")

    session = Session()

    try:
        # Generate monthly plans
        generate_monthly_demand_plans(session, year=2026, months=[1,2,3,4])

        # Generate weekly actuals
        generate_weekly_actuals(session, year=2026)

        # Verify
        verify_data(session)

        print("\n" + "="*60)
        print("✓ 2026 data generation complete!")
        print("="*60)
        print("\nNext: Verify ML models only train on 2020-2025")
        print("Demo date: 2026-04-07 (April Week 1 ended)")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        sys.exit(1)

    finally:
        session.close()

if __name__ == "__main__":
    main()
