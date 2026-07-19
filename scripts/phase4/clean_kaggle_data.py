"""
Phase 4, Step 4.2: Clean Kaggle Data
Cleans and aggregates pharmacy sales data
"""

import os
import sys
import pandas as pd
from datetime import datetime

def clean_kaggle_data():
    """Clean and aggregate Kaggle data"""

    csv_path = "data/raw/pharmacy_sales_2020_2025.csv"

    if not os.path.exists(csv_path):
        # Try alternate names
        raw_files = [f for f in os.listdir("data/raw") if f.endswith('.csv')]
        if raw_files:
            csv_path = f"data/raw/{raw_files[0]}"
        else:
            print(f"✗ ERROR: No CSV file found in data/raw/")
            print("  Run download_kaggle_data.py first")
            sys.exit(1)

    print(f"Reading {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"✗ ERROR reading CSV: {e}")
        sys.exit(1)

    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")

    # Clean data (adjust columns to actual dataset)
    # This is a template - user should adapt to actual CSV columns

    # Convert date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    # Aggregate daily → monthly
    if 'date' in df.columns and 'units_sold' in df.columns:
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby(['month', 'product', 'region'])['units_sold'].sum().reset_index()
    else:
        monthly = df  # Use as-is if columns don't match

    # Save cleaned data
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/pharmacy_sales_monthly.csv"
    monthly.to_csv(output_path, index=False)

    print(f"✓ Cleaned data saved to {output_path}")
    print(f"  Monthly aggregated rows: {len(monthly)}")

if __name__ == "__main__":
    try:
        clean_kaggle_data()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
