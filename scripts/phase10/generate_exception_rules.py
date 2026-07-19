"""Phase 10, Step 10.1: Generate Exception Rules"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ExceptionRule, ExceptionType, SeverityLevel

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_exception_rules():
    session = Session()
    rules = []
    RULES_DATA = [
        ("EXC-001", "Stockout Risk Critical", ExceptionType.STOCKOUT_RISK, SeverityLevel.CRITICAL, 2.0, "days"),
        ("EXC-002", "Stockout Risk High", ExceptionType.STOCKOUT_RISK, SeverityLevel.HIGH, 5.0, "days"),
        ("EXC-003", "Safety Stock Breach", ExceptionType.SAFETY_STOCK_BREACH, SeverityLevel.HIGH, 1.0, "ratio"),
        ("EXC-004", "Excess Inventory", ExceptionType.EXCESS_INVENTORY, SeverityLevel.MEDIUM, 60.0, "days"),
        ("EXC-005", "Quality Deviation", ExceptionType.QUALITY_DEVIATION, SeverityLevel.HIGH, 10.0, "percent"),
        ("EXC-006", "Demand Spike", ExceptionType.DEMAND_SPIKE, SeverityLevel.HIGH, 150.0, "percent"),
        ("EXC-007", "Demand Drop", ExceptionType.DEMAND_DROP, SeverityLevel.MEDIUM, 50.0, "percent"),
        ("EXC-008", "Late Delivery", ExceptionType.LATE_DELIVERY, SeverityLevel.HIGH, 2.0, "days"),
        ("EXC-009", "Compliance Deadline", ExceptionType.COMPLIANCE_DEADLINE, SeverityLevel.HIGH, 10.0, "days"),
    ]
    for code, name, exc_type, severity, threshold, unit in RULES_DATA:
        rules.append(ExceptionRule(id=uuid.uuid4(), rule_code=code, rule_name=name, exception_type=exc_type, severity=severity, threshold_value=threshold, threshold_unit=unit, is_enabled=True, created_by="generate_exception_rules.py", is_active=True))
    Base.metadata.create_all(engine)
    session.add_all(rules)
    session.commit()
    print(f"✓ Inserted {len(rules)} exception rules")
    session.close()

if __name__ == "__main__":
    try: generate_exception_rules()
    except Exception as e: print(f"✗ ERROR: {e}"); sys.exit(1)
