"""Phase 10, Step 10.3: Generate Exception History"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid, random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ExceptionHistory, ExceptionType, SeverityLevel, ExceptionStatus

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_exception_history():
    session = Session()
    history = []
    for i in range(5):
        detected = datetime.utcnow()-timedelta(days=random.randint(10,30))
        resolved = detected + timedelta(hours=random.randint(12,72))
        history.append(ExceptionHistory(id=uuid.uuid4(), active_exception_id=uuid.uuid4(), exception_type=ExceptionType.STOCKOUT_RISK, severity=SeverityLevel.CRITICAL, status=ExceptionStatus.RESOLVED, affected_item_code="PARA500", affected_location_name="Plant North", detected_at=detected, resolved_at=resolved, duration_hours=int((resolved-detected).total_seconds()/3600), alert_message="Stockout resolved", resolution_action="Emergency order placed", created_by="generate_exception_history.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(history)
    session.commit()
    print(f"✓ Inserted {len(history)} exception history records")
    session.close()

if __name__ == "__main__":
    try: generate_exception_history()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
