"""Phase 10 Validation"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ExceptionRule, ActiveException, ExceptionHistory

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phase10():
    session = Session()
    errors = []
    rules = session.query(ExceptionRule).count()
    if rules != 9: errors.append(f"Expected 9 rules, got {rules}")
    active = session.query(ActiveException).count()
    if active != 8: errors.append(f"Expected 8 active, got {active}")
    history = session.query(ExceptionHistory).count()
    if history != 5: errors.append(f"Expected 5 history, got {history}")
    session.close()
    if errors:
        print("✗ Phase 10 validation FAILED")
        for error in errors: print(f"  - {error}")
        sys.exit(1)
    else: print(f"✓ Phase 10 validated\n  - {rules+active+history} total records")

if __name__ == "__main__":
    try: validate_phase10()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
