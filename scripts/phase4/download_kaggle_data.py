"""
Phase 4, Step 4.1: Download Kaggle Dataset
Downloads pharmacy sales data from Kaggle
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Set Kaggle credentials from .env
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME', '')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY', '')

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except ImportError:
    print("✗ ERROR: kaggle library not installed")
    print("  Run: pip install kaggle")
    sys.exit(1)

def download_kaggle_data():
    """Download Kaggle dataset"""

    # Check credentials
    if not os.environ['KAGGLE_USERNAME'] or not os.environ['KAGGLE_KEY']:
        print("✗ ERROR: Kaggle credentials not found in .env")
        print("  Add KAGGLE_USERNAME and KAGGLE_KEY to .env file")
        sys.exit(1)

    # Create data directory
    os.makedirs("data/raw", exist_ok=True)

    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()

    print("Downloading Global Pharmacy Sales Dataset...")
    print("(This may take 2-5 minutes, ~50MB)")

    try:
        api.dataset_download_files(
            'annemark/global-pharmacy-sales-dataset-20202025',
            path='data/raw',
            unzip=True
        )

        print("✓ Dataset downloaded successfully")

        # List downloaded files
        files = os.listdir("data/raw")
        print(f"  Downloaded files: {', '.join(files)}")

    except Exception as e:
        print(f"✗ ERROR downloading dataset: {e}")
        print("\nTroubleshooting:")
        print("  1. Check Kaggle credentials in .env")
        print("  2. Ensure ~/.kaggle/kaggle.json exists (fallback)")
        print("  3. Check internet connection")
        print("  4. Visit: https://www.kaggle.com/datasets/annemark/global-pharmacy-sales-dataset-20202025")
        sys.exit(1)

if __name__ == "__main__":
    try:
        download_kaggle_data()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
