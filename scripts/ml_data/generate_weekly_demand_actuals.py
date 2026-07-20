"""
Generate weekly demand actuals for real-time surge detection

Decomposes monthly demand_plans into weekly granularity with:
- Normal months: ±10% random variation per week
- Surge months (COVID, flu): Week 1 shows early spike signal (25-40%)
- Creates realistic patterns for ML training and demo
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
import json

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_weekly_actuals_table(session):
    """Create table for weekly demand tracking"""

    create_table = text("""
        CREATE TABLE IF NOT EXISTS weekly_demand_actuals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            item_id UUID NOT NULL REFERENCES items(id),
            location_id UUID NOT NULL REFERENCES location_nodes(id),
            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,
            week_number INTEGER,  -- 1-4 within month
            forecast_quantity INTEGER,  -- Expected for this week
            actual_quantity INTEGER,    -- What actually happened
            deviation_pct FLOAT,        -- (actual - forecast) / forecast * 100
            is_surge BOOLEAN,           -- deviation_pct > 25%
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            created_by VARCHAR(200),
            is_active BOOLEAN DEFAULT TRUE,

            UNIQUE(item_id, location_id, week_start_date)
        );

        CREATE INDEX IF NOT EXISTS idx_weekly_actuals_date
            ON weekly_demand_actuals(week_start_date);
        CREATE INDEX IF NOT EXISTS idx_weekly_actuals_item
            ON weekly_demand_actuals(item_id);
        CREATE INDEX IF NOT EXISTS idx_weekly_actuals_surge
            ON weekly_demand_actuals(is_surge) WHERE is_surge = TRUE;
    """)

    session.execute(create_table)
    session.commit()
    print("✓ Created weekly_demand_actuals table")

def get_monthly_demands(session):
    """Fetch all monthly demand plans to decompose"""

    query = text("""
        SELECT
            dp.id,
            dp.item_id,
            dp.location_id,
            dp.period_start,
            dp.period_end,
            dp.quantity as monthly_quantity,
            i.code as item_code,
            ln.name as location_name,
            r.code as region_code
        FROM demand_plans dp
        JOIN items i ON dp.item_id = i.id
        JOIN location_nodes ln ON dp.location_id = ln.id
        JOIN regions r ON ln.region_id = r.id
        WHERE dp.plan_type = 'HISTORICAL'
          AND i.type = 'FINISHED_GOOD'
        ORDER BY dp.period_start, i.code, r.code
    """)

    result = session.execute(query)
    return result.fetchall()

def get_event_for_month(session, item_code, month_date):
    """Check if this month falls within any historical event"""

    query = text("""
        SELECT
            event_code,
            event_name,
            event_type,
            demand_impact_multiplier
        FROM historical_events
        WHERE :month_date BETWEEN start_date AND COALESCE(end_date, '2025-12-31')
          AND (
            affected_items::text LIKE :item_pattern
            OR affected_items IS NULL
          )
          AND demand_impact_multiplier > 1
        ORDER BY demand_impact_multiplier DESC
        LIMIT 1
    """)

    result = session.execute(query, {
        'month_date': month_date,
        'item_pattern': f'%{item_code}%'
    })

    return result.fetchone()

def generate_weekly_pattern(monthly_qty, event_info):
    """
    Generate 4 weekly actuals from monthly total

    Patterns:
    - Normal month (no event): ±10% random variation
    - COVID surge (2x multiplier): Week1 +40%, Week2 +80%, Week3 +120%, Week4 +100%
    - Flu surge (1.25x multiplier): Week1 +10%, Week2 +20%, Week3 +30%, Week4 +15%
    """

    base_weekly = monthly_qty / 4

    if not event_info:
        # Normal month: random variation ±10%
        weekly_actuals = [
            int(base_weekly * np.random.uniform(0.9, 1.1)) for _ in range(4)
        ]
        is_surge_month = False

    elif event_info.demand_impact_multiplier >= 2.0:
        # COVID-like surge: Sharp early spike
        # Week 1: +40% (early signal)
        # Week 2-4: Escalating to +100%+
        multipliers = [1.4, 1.8, 2.2, 2.0]
        weekly_actuals = [
            int(base_weekly * m * np.random.uniform(0.95, 1.05))
            for m in multipliers
        ]
        is_surge_month = True

    elif event_info.demand_impact_multiplier >= 1.2:
        # Flu-like surge: Gradual build
        # Week 1: +10% (mild early signal)
        # Week 2-3: Building
        # Week 4: Tapering
        multipliers = [1.1, 1.2, 1.3, 1.15]
        weekly_actuals = [
            int(base_weekly * m * np.random.uniform(0.95, 1.05))
            for m in multipliers
        ]
        is_surge_month = True

    else:
        # Shouldn't reach here, but fallback to normal
        weekly_actuals = [
            int(base_weekly * np.random.uniform(0.9, 1.1)) for _ in range(4)
        ]
        is_surge_month = False

    return weekly_actuals, is_surge_month

def generate_weekly_actuals(session, monthly_demands):
    """
    Decompose monthly demands into weekly actuals
    """

    print(f"Generating weekly actuals for {len(monthly_demands)} monthly records...")

    weekly_records = []
    surge_count = 0

    for demand in monthly_demands:
        # Get event info for this month
        event_info = get_event_for_month(
            session,
            demand.item_code,
            demand.period_start
        )

        # Generate 4 weekly actuals
        weekly_actuals, is_surge_month = generate_weekly_pattern(
            demand.monthly_quantity,
            event_info
        )

        # Create week records
        month_start = demand.period_start

        for week_num in range(1, 5):
            # Calculate week dates (7 days per week)
            week_start = month_start + timedelta(days=(week_num - 1) * 7)
            week_end = week_start + timedelta(days=6)

            # Ensure week_end doesn't exceed month
            if week_end > demand.period_end:
                week_end = demand.period_end

            forecast_qty = demand.monthly_quantity / 4
            actual_qty = weekly_actuals[week_num - 1]
            deviation = ((actual_qty - forecast_qty) / forecast_qty * 100) if forecast_qty > 0 else 0
            is_surge = deviation > 25  # 25% threshold

            weekly_records.append({
                'id': uuid.uuid4(),
                'item_id': demand.item_id,
                'location_id': demand.location_id,
                'week_start_date': week_start,
                'week_end_date': week_end,
                'week_number': week_num,
                'forecast_quantity': int(forecast_qty),
                'actual_quantity': actual_qty,
                'deviation_pct': deviation,
                'is_surge': is_surge,
                'created_by': 'generate_weekly_demand_actuals.py',
                'is_active': True
            })

            if is_surge:
                surge_count += 1

    print(f"Generated {len(weekly_records)} weekly records")
    print(f"Surge weeks detected: {surge_count} ({surge_count/len(weekly_records)*100:.1f}%)")

    return weekly_records

def insert_weekly_actuals(session, weekly_records):
    """Bulk insert weekly actuals"""

    print("Inserting weekly actuals...")

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
        ON CONFLICT (item_id, location_id, week_start_date) DO UPDATE
        SET
            actual_quantity = EXCLUDED.actual_quantity,
            deviation_pct = EXCLUDED.deviation_pct,
            is_surge = EXCLUDED.is_surge,
            updated_at = NOW()
    """)

    inserted = 0
    for record in weekly_records:
        session.execute(insert_query, record)
        inserted += 1

        if inserted % 500 == 0:
            print(f"  ... {inserted} rows")
            session.commit()

    session.commit()
    print(f"✓ Inserted {inserted} weekly actual records")

def verify_surge_detection(session):
    """Verify early surge detection (Week 1 of surge months)"""

    print("\n" + "="*60)
    print("Verifying Early Surge Detection (Week 1 Signals)")
    print("="*60)

    query = text("""
        SELECT
            TO_CHAR(wda.week_start_date, 'YYYY-MM') as month,
            wda.week_number,
            i.code as item,
            r.code as region,
            wda.forecast_quantity,
            wda.actual_quantity,
            wda.deviation_pct,
            wda.is_surge,
            he.event_name
        FROM weekly_demand_actuals wda
        JOIN items i ON wda.item_id = i.id
        JOIN location_nodes ln ON wda.location_id = ln.id
        JOIN regions r ON ln.region_id = r.id
        LEFT JOIN historical_events he ON
            wda.week_start_date BETWEEN he.start_date AND COALESCE(he.end_date, '2025-12-31')
            AND he.demand_impact_multiplier > 1
        WHERE i.code = 'PARA500'
          AND r.code = 'NORTH'
          AND wda.week_start_date BETWEEN '2020-01-01' AND '2020-12-31'
          AND wda.week_number = 1  -- Week 1 only
        ORDER BY wda.week_start_date
    """)

    result = session.execute(query)
    rows = result.fetchall()

    print("\nPARA500 NORTH - Week 1 of Each Month (2020):\n")
    print(f"{'Month':<10} {'Forecast':<10} {'Actual':<10} {'Deviation':<12} {'Surge?':<8} {'Event'}")
    print("-" * 80)

    early_detections = 0
    for row in rows:
        surge_indicator = "🚨 SURGE" if row.is_surge else "✓ Normal"
        event_name = row.event_name[:20] if row.event_name else "None"

        print(f"{row.month:<10} {row.forecast_quantity:<10,} {row.actual_quantity:<10,} "
              f"{row.deviation_pct:>+6.1f}%     {surge_indicator:<8} {event_name}")

        if row.is_surge:
            early_detections += 1

    print(f"\n✓ Early surge detections (Week 1): {early_detections} months")
    print(f"  (Agent would alert in Week 1, not wait for month-end)")

def main():
    print("="*60)
    print("Generate Weekly Demand Actuals")
    print("="*60)

    session = Session()

    try:
        # Step 1: Create table
        create_weekly_actuals_table(session)

        # Step 2: Fetch monthly demands
        monthly_demands = get_monthly_demands(session)
        print(f"\nFetched {len(monthly_demands)} monthly demand records")

        # Step 3: Generate weekly decomposition
        weekly_records = generate_weekly_actuals(session, monthly_demands)

        # Step 4: Insert into database
        insert_weekly_actuals(session, weekly_records)

        # Step 5: Verify surge detection
        verify_surge_detection(session)

        print("\n" + "="*60)
        print("✓ Weekly actuals generation complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Train ML model on weekly data (not monthly)")
        print("2. Demo: Simulate Week 1 data streaming in real-time")
        print("3. Agent monitors deviation_pct > 25% threshold")

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
