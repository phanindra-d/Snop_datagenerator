"""
Replace synthetic demand_plans with real Kaggle data
Run AFTER Phase 4 generation to overwrite with realistic COVID/flu patterns
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def load_kaggle_data(csv_path):
    """Load and filter Kaggle dataset"""
    print("Loading Kaggle CSV...")
    df = pd.read_csv(csv_path)

    # Filter to 3 medicines only
    medicines = ['Paracetamol', 'Ibuprofen', 'Azithromycin']
    df = df[df['medicine'].isin(medicines)]

    # Filter to North America only (will split into 4 US regions)
    df = df[df['region'] == 'North America'].copy()

    print(f"Filtered to {len(df)} rows (3 medicines × North America)")
    return df

def transform_to_snop_regions(df_kaggle):
    """
    Transform Kaggle North America → 4 US regions (NORTH, EAST, WEST, SOUTH)
    Split demand equally with random variation
    """
    print("Transforming to SNOP regions...")

    snop_data = []
    us_regions = ['NORTH', 'EAST', 'WEST', 'SOUTH']

    for _, row in df_kaggle.iterrows():
        # Split North America demand into 4 regions with variation
        base_demand = row['units_sold'] / 4

        for region in us_regions:
            # Add realistic variation (±10%)
            variation = np.random.uniform(0.9, 1.1)
            demand = int(base_demand * variation)

            snop_data.append({
                'month': row['month'],
                'medicine': row['medicine'],
                'region': region,
                'demand': demand
            })

    df_snop = pd.DataFrame(snop_data)
    print(f"Generated {len(df_snop)} SNOP rows (3 items × 4 regions × N months)")

    return df_snop

def get_location_mapping(session):
    """
    Get mapping: (item_code, region_code) → location_id
    Use first distributor in each region
    """
    print("Fetching location mappings...")

    query = text("""
        SELECT
            i.code as item_code,
            r.code as region_code,
            ln.id as location_id,
            ln.name as location_name
        FROM items i
        CROSS JOIN regions r
        LEFT JOIN location_nodes ln ON ln.region_id = r.id
        WHERE i.type = 'FINISHED_GOOD'
          AND ln.type = 'DISTRIBUTOR'
        ORDER BY i.code, r.code, ln.name
    """)

    result = session.execute(query)
    rows = result.fetchall()

    # Create mapping: (item, region) -> first location_id
    mapping = {}
    for row in rows:
        key = (row.item_code, row.region_code)
        if key not in mapping:
            mapping[key] = row.location_id

    print(f"Created mappings for {len(mapping)} item-region combinations")
    return mapping

def get_item_mapping(session):
    """Map medicine names to item IDs"""
    query = text("SELECT code, id FROM items WHERE type = 'FINISHED_GOOD'")
    result = session.execute(query)

    name_to_id = {}
    code_to_id = {}
    for row in result:
        code_to_id[row.code] = row.id

    # Map Kaggle names to SNOP codes
    name_to_id['Paracetamol'] = code_to_id.get('PARA500')
    name_to_id['Ibuprofen'] = code_to_id.get('IBUP400')
    name_to_id['Azithromycin'] = code_to_id.get('AZITH500')

    print(f"Mapped 3 medicines to item IDs")
    return name_to_id

def delete_existing_demand_plans(session):
    """Delete existing synthetic demand_plans"""
    print("Deleting existing demand_plans...")

    count_query = text("SELECT COUNT(*) FROM demand_plans WHERE plan_type = 'HISTORICAL'")
    count_before = session.execute(count_query).scalar()

    delete_provenance_query = text("""
        DELETE FROM demand_provenance
        WHERE demand_plan_id IN (
            SELECT id FROM demand_plans WHERE plan_type = 'HISTORICAL'
        )
    """)
    session.execute(delete_provenance_query)

    delete_query = text("DELETE FROM demand_plans WHERE plan_type = 'HISTORICAL'")
    session.execute(delete_query)
    session.commit()

    print(f"✓ Deleted {count_before} synthetic demand_plan rows")

def insert_kaggle_demand_plans(session, df_snop, location_mapping, item_mapping):
    """Insert Kaggle-based demand plans"""
    print("Inserting Kaggle demand plans...")

    inserted = 0
    errors = 0

    for _, row in df_snop.iterrows():
        try:
            # Get item_id
            item_id = item_mapping.get(row['medicine'])
            if not item_id:
                print(f"⚠️  Skipping unknown medicine: {row['medicine']}")
                errors += 1
                continue

            # Get item code for location lookup
            item_code = None
            for name, iid in item_mapping.items():
                if iid == item_id:
                    if name == 'Paracetamol':
                        item_code = 'PARA500'
                    elif name == 'Ibuprofen':
                        item_code = 'IBUP400'
                    elif name == 'Azithromycin':
                        item_code = 'AZITH500'

            # Get location_id
            location_id = location_mapping.get((item_code, row['region']))
            if not location_id:
                print(f"⚠️  Skipping missing location: {item_code} {row['region']}")
                errors += 1
                continue

            # Parse period_start (Kaggle format: "2020-01")
            period_start = datetime.strptime(row['month'], '%Y-%m')

            # Calculate period_end (last day of month)
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1, day=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1, day=1)

            from datetime import timedelta
            period_end = period_end - timedelta(days=1)

            # Insert row
            insert_query = text("""
                INSERT INTO demand_plans (
                    id, item_id, location_id, period_start, period_end,
                    bucket_type, plan_type, quantity, scenario_id,
                    created_at, updated_at, created_by, is_active, version
                ) VALUES (
                    :id, :item_id, :location_id, :period_start, :period_end,
                    'MONTHLY', 'HISTORICAL', :quantity, NULL,
                    NOW(), NOW(), 'replace_demand_with_kaggle.py', TRUE, 1
                )
            """)

            session.execute(insert_query, {
                'id': uuid.uuid4(),
                'item_id': item_id,
                'location_id': location_id,
                'period_start': period_start,
                'period_end': period_end,
                'quantity': row['demand']
            })

            inserted += 1

            if inserted % 100 == 0:
                print(f"  ... inserted {inserted} rows")
                session.commit()

        except Exception as e:
            print(f"✗ Error inserting row: {e}")
            errors += 1
            continue

    session.commit()
    print(f"✓ Inserted {inserted} Kaggle demand_plan rows")
    if errors > 0:
        print(f"⚠️  {errors} rows skipped due to errors")

def verify_covid_spike(session):
    """Verify COVID spike exists in data"""
    print("\nVerifying COVID spike pattern...")

    query = text("""
        SELECT
            TO_CHAR(dp.period_start, 'YYYY-MM') as month,
            i.code as item,
            r.code as region,
            dp.quantity
        FROM demand_plans dp
        JOIN items i ON dp.item_id = i.id
        JOIN location_nodes ln ON dp.location_id = ln.id
        JOIN regions r ON ln.region_id = r.id
        WHERE i.code = 'PARA500'
          AND r.code = 'NORTH'
          AND dp.period_start BETWEEN '2020-01-01' AND '2020-06-01'
        ORDER BY dp.period_start
    """)

    result = session.execute(query)
    rows = result.fetchall()

    if len(rows) == 0:
        print("✗ No data found for verification")
        return False

    print("\nPARA500 NORTH demand (Jan-Jun 2020):")
    baseline = rows[0].quantity if len(rows) > 0 else 0

    covid_spike_detected = False
    for row in rows:
        spike_pct = ((row.quantity - baseline) / baseline * 100) if baseline > 0 else 0
        spike_indicator = "📈 COVID SPIKE" if spike_pct > 100 else ""
        print(f"  {row.month}: {row.quantity:,} units ({spike_pct:+.0f}%) {spike_indicator}")

        if spike_pct > 100:
            covid_spike_detected = True

    if covid_spike_detected:
        print("\n✓ COVID spike pattern detected (Mar 2020 shows >100% increase)")
        return True
    else:
        print("\n⚠️  No significant spike detected. Check Kaggle data has COVID pattern.")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("Replace Demand Plans with Kaggle Data")
    print("=" * 60)

    # Check if Kaggle CSV exists
    kaggle_csv = 'data/processed/pharmacy_sales_monthly.csv'

    if not os.path.exists(kaggle_csv):
        print(f"\n✗ Kaggle CSV not found at: {kaggle_csv}")
        print("\nPlease download Kaggle dataset:")
        print("  1. Download from: https://www.kaggle.com/datasets/annemark/global-pharmacy-sales-dataset-20202025")
        print("  2. Extract CSV to: data/raw/global_pharmacy_sales_2020_2025.csv")
        print("  3. Re-run this script")
        sys.exit(1)

    session = Session()

    try:
        # Step 1: Load Kaggle data
        df_kaggle = load_kaggle_data(kaggle_csv)

        # Step 2: Transform to SNOP regions
        df_snop = transform_to_snop_regions(df_kaggle)

        # Step 3: Get mappings
        location_mapping = get_location_mapping(session)
        item_mapping = get_item_mapping(session)

        # Step 4: Delete existing
        delete_existing_demand_plans(session)

        # Step 5: Insert Kaggle data
        insert_kaggle_demand_plans(session, df_snop, location_mapping, item_mapping)

        # Step 6: Verify COVID spike
        verify_covid_spike(session)

        print("\n" + "=" * 60)
        print("✓ Demand plans replacement complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        session.rollback()
        sys.exit(1)

    finally:
        session.close()

if __name__ == "__main__":
    main()
