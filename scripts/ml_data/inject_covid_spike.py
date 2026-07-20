"""
Apply historical event demand spikes from database to demand_plans
Reads multipliers from historical_events table (single source of truth)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def apply_event_spikes_from_database(session):
    """
    Read historical_events table and apply demand_impact_multiplier to demand_plans

    Database is single source of truth for event definitions and multipliers
    """

    print("Reading historical events from database...")

    # Fetch all events with demand impact
    events_query = text("""
        SELECT
            event_code,
            event_name,
            event_type,
            start_date,
            end_date,
            affected_items,
            affected_regions,
            demand_impact_multiplier,
            impact_description
        FROM historical_events
        WHERE demand_impact_multiplier IS NOT NULL
          AND demand_impact_multiplier != 1
        ORDER BY start_date
    """)

    result = session.execute(events_query)
    events = result.fetchall()

    if len(events) == 0:
        print("⚠️  No events found with demand impact multiplier")
        return 0

    print(f"Found {len(events)} events with demand impact:\n")

    total_updated = 0

    for event in events:
        print(f"📊 {event.event_name} ({event.event_code})")
        print(f"   Period: {event.start_date} to {event.end_date or 'ongoing'}")
        print(f"   Multiplier: {event.demand_impact_multiplier}x")
        print(f"   Description: {event.impact_description}")

        # Parse affected items (JSON array)
        try:
            affected_items = json.loads(event.affected_items) if isinstance(event.affected_items, str) else event.affected_items
        except:
            affected_items = []

        if not affected_items:
            print(f"   ⚠️  No affected items, skipping")
            continue

        print(f"   Affected items: {', '.join(affected_items)}")

        # Parse affected regions (JSON array)
        try:
            affected_regions = json.loads(event.affected_regions) if isinstance(event.affected_regions, str) else event.affected_regions
        except:
            affected_regions = ['NORTH', 'EAST', 'WEST', 'SOUTH']  # Default all

        # Build WHERE clause for regions
        if affected_regions and affected_regions != ['NORTH', 'EAST', 'WEST', 'SOUTH']:
            region_filter = "AND r.code = ANY(:regions)"
        else:
            region_filter = ""  # All regions

        # Apply multiplier to each affected item
        for item_code in affected_items:
            update_query = text(f"""
                UPDATE demand_plans dp
                SET
                    quantity = CAST(dp.quantity * :multiplier AS INTEGER),
                    updated_at = NOW(),
                    created_by = CONCAT('inject_event_spikes.py (', :event_code, ')')
                FROM items i, location_nodes ln, regions r
                WHERE dp.item_id = i.id
                  AND dp.location_id = ln.id
                  AND ln.region_id = r.id
                  AND i.code = :item_code
                  AND dp.period_start >= :start_date
                  AND (
                    :end_date IS NULL
                    OR dp.period_start <= :end_date
                  )
                  {region_filter}
            """)

            params = {
                'multiplier': event.demand_impact_multiplier,
                'event_code': event.event_code,
                'item_code': item_code,
                'start_date': event.start_date,
                'end_date': event.end_date
            }

            if region_filter:
                params['regions'] = affected_regions

            result = session.execute(update_query, params)
            rows_updated = result.rowcount
            total_updated += rows_updated

            print(f"   - {item_code}: {rows_updated} rows updated")

        print()

    session.commit()

    print(f"✓ Total rows updated across all events: {total_updated}\n")
    return total_updated

def verify_spike_pattern(session):
    """Verify COVID spike exists"""
    print("\n" + "="*60)
    print("Verifying spike patterns...")

    query = text("""
        SELECT
            TO_CHAR(dp.period_start, 'YYYY-MM') as month,
            i.code as item,
            AVG(dp.quantity) as avg_demand
        FROM demand_plans dp
        JOIN items i ON dp.item_id = i.id
        WHERE i.code = 'PARA500'
          AND dp.period_start BETWEEN '2019-12-01' AND '2021-06-01'
        GROUP BY TO_CHAR(dp.period_start, 'YYYY-MM'), i.code
        ORDER BY month
    """)

    result = session.execute(query)
    rows = result.fetchall()

    if len(rows) == 0:
        print("✗ No data found")
        return False

    print("\nPARA500 demand pattern (Dec 2019 - Jun 2021):")
    baseline = rows[0].avg_demand if len(rows) > 0 else 1

    covid_detected = False
    for row in rows:
        surge_pct = ((row.avg_demand - baseline) / baseline * 100)

        if row.month >= '2020-03' and row.month <= '2020-06' and surge_pct > 150:
            indicator = "📈 COVID PEAK"
            covid_detected = True
        elif row.month >= '2020-03' and row.month <= '2021-12' and surge_pct > 50:
            indicator = "📊 ELEVATED"
        else:
            indicator = ""

        print(f"  {row.month}: {row.avg_demand:>7,.0f} units ({surge_pct:>+6.0f}%) {indicator}")

    if covid_detected:
        print("\n✓ COVID-19 spike pattern successfully injected")
        return True
    else:
        print("\n⚠️  Spike pattern weak. Expected >150% increase Mar-Jun 2020.")
        return False

def main():
    print("="*60)
    print("Apply Historical Event Demand Spikes from Database")
    print("="*60)

    session = Session()

    try:
        # Step 1: Apply all event spikes from historical_events table
        total = apply_event_spikes_from_database(session)

        if total == 0:
            print("⚠️  No demand spikes applied. Check historical_events table.")
            sys.exit(1)

        # Step 2: Verify COVID spike pattern
        verify_spike_pattern(session)

        print("\n" + "="*60)
        print(f"✓ Applied {total} event-driven demand spikes!")
        print("="*60)

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
