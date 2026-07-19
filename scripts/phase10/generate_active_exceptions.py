"""Phase 10, Step 10.2: Generate Active Exceptions"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid, random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ActiveException, ExceptionRule, Item, LocationNode, ExceptionType, SeverityLevel, ExceptionStatus

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_active_exceptions():
    session = Session()
    rules = session.query(ExceptionRule).all()
    items = session.query(Item).limit(3).all()
    locations = session.query(LocationNode).limit(4).all()
    exceptions = []
    for i in range(8):
        rule = random.choice(rules)
        exceptions.append(ActiveException(id=uuid.uuid4(), exception_rule_id=rule.id, exception_type=rule.exception_type, severity=rule.severity, status=random.choice([ExceptionStatus.ACTIVE, ExceptionStatus.ACKNOWLEDGED]), affected_item_id=random.choice(items).id if items else None, affected_location_id=random.choice(locations).id if locations else None, detected_at=datetime.utcnow()-timedelta(hours=random.randint(1,72)), current_value=80.0, threshold_value=100.0, deviation_pct=20.0, alert_title=f"Alert {i+1}", alert_message="Stockout risk detected", recommended_actions='["Order more"]', created_by="generate_active_exceptions.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(exceptions)
    session.commit()
    print(f"✓ Inserted {len(exceptions)} active exceptions")
    session.close()

if __name__ == "__main__":
    try: generate_active_exceptions()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
