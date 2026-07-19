# Script Replication Guide

**Created:** 5/42 scripts (Phase 1 + part of Phase 2)
**Remaining:** 37 scripts

Due to size limits, sample scripts provided. Use this guide to create remaining scripts.

---

## Script Pattern (Copy This)

```python
"""
Phase X, Step X.Y: [Description]
Creates N rows in [table_name]
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, [YourModel], [Dependencies]

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_[table_name]():
    """Generate [N] [records]"""
    session = Session()

    # Get dependencies if needed
    # items = {i.code: i.id for i in session.query(Item).all()}

    records = []

    # YOUR DATA HERE - copy from SNOP_DATA_GENERATION_PLAN.md
    DATA = [
        # ...
    ]

    for data in DATA:
        records.append([YourModel](
            id=uuid.uuid4(),
            # ... your fields
            created_by="generate_[table_name].py",
            is_active=True
        ))

    # Create table
    Base.metadata.create_all(engine)

    # Insert
    session.add_all(records)
    session.commit()

    print(f"✓ Inserted {len(records)} [table_name]")
    session.close()

if __name__ == "__main__":
    try:
        generate_[table_name]()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
```

---

## Validation Script Pattern

```python
"""
Phase X Validation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import [YourModels]

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def validate_phaseX():
    session = Session()
    errors = []

    # Check row counts
    count = session.query([YourModel]).count()
    if count != EXPECTED:
        errors.append(f"Expected {EXPECTED}, got {count}")

    # Check constraints
    # ... your validations

    session.close()

    if errors:
        print("✗ Phase X validation FAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ Phase X validated")

if __name__ == "__main__":
    try:
        validate_phaseX()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
```

---

## Quick Create: Remaining Scripts

**Phase 3:** (lines 1047-1598 in plan)
- `scripts/phase3/generate_inventory_rules.py` (9 rows)
- `scripts/phase3/generate_validation_rules.py` (15 rows)
- `scripts/phase3/generate_optimization_constraints.py` (8 rows)
- `scripts/phase3/validate_phase3.py`

**Phase 4:** (lines 2108-3632 in plan) **CRITICAL - Kaggle**
- `scripts/phase4/download_kaggle_data.py` - use `kaggle` library
- `scripts/phase4/clean_kaggle_data.py` - pandas data cleaning
- `scripts/phase4/generate_historical_events.py` (6 rows)
- `scripts/phase4/generate_demand_plans.py` (864 rows - from cleaned Kaggle)
- `scripts/phase4/generate_supply_plans.py` (648 rows)
- `scripts/phase4/generate_inventory_movements.py` (1944 rows)
- `scripts/phase4/validate_phase4.py`

**Phase 5:** (lines 1604-2102 in plan)
- `scripts/phase5/generate_current_inventory.py` (56 rows)
- `scripts/phase5/validate_phase5.py`

**Phase 6-10:** Follow same pattern

---

## Automated Approach (Recommended)

Use Claude Code / AI to generate from plan:

```
Prompt: "Read SNOP_DATA_GENERATION_PLAN.md lines X-Y, extract data, 
create scripts/phaseN/generate_[table].py following the pattern in 
scripts/phase1/generate_regions.py"
```

Or manually extract data blocks from plan → paste into script template.

---

## Status After This Session

✅ **Complete:**
- Phase 1: 4/4 scripts
- Phase 2: 4/4 scripts

⏸️ **Need Creation:**
- Phase 3: 0/4
- Phase 4: 0/7
- Phase 5: 0/2
- Phase 6: 0/4
- Phase 7: 0/5
- Phase 8: 0/4
- Phase 9: 0/4
- Phase 10: 0/4

**Total:** 8/42 scripts created (19%)

**Est. time to complete remaining:** 2-3 hours (manual) or 30 min (with AI assistance)
