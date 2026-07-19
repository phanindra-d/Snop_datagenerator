"""
Phase 5 Validation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CurrentInventory

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase5():
    session = Session()
    errors = []

    count = session.query(CurrentInventory).count()
    if count != 56:
        errors.append(f"Expected 56 inventory records, got {count}")

    session.close()

    if errors:
        print("✗ Phase 5 validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase 5 validated")
        print(f"  - {count} current inventory records")

if __name__ == "__main__":
    try:
        validate_phase5()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
