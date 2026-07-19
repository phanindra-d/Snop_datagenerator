# Scripts TODO - Remaining 37 Scripts

**✓ Phase 1 Complete** (4 scripts created)

**Pattern for all scripts:**

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
from models import Base, [TableModel], [DependencyModel]

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_[table_name]():
    """Generate [N] [table_name]"""
    session = Session()

    # Get dependencies (if needed)
    # items = {i.code: i.id for i in session.query(Item).all()}

    records = []

    # Data definition
    DATA = [
        # ... data rows
    ]

    for data in DATA:
        records.append([TableModel](
            id=uuid.uuid4(),
            # ... fields
            created_by="generate_[table_name].py",
            is_active=True
        ))

    # Create table if not exists
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

## Phase 2: Relationships (4 scripts)

### scripts/phase2/generate_boms.py

**Data** (from SNOP_DATA_GENERATION_PLAN.md lines 545-643):
```python
# 9 BOMs (3 FG × 3 materials each)
# PARA500 needs: API-PARA (0.0005kg), EXC-STARCH (0.00015kg), EXC-MCC (0.0002kg)
# IBUP400 needs: API-IBUP (0.0004kg), EXC-GELATIN (0.0001kg), EXC-GLYCERIN (0.00005kg)
# AZITH500 needs: API-AZITH (0.0005kg), EXC-LACTOSE (0.0002kg), EXC-MCC (0.0001kg)
```

### scripts/phase2/generate_transportation_lanes.py

**Data** (lines 645-775):
```python
# 24 lanes
# Plant → Plant WH (0 days)
# Plant WH → Regional WH (2 days)
# Regional WH → Distributor (1 day)
# Subcontractor → Plant WH (3 days)
```

### scripts/phase2/generate_plant_capacities.py

**Data** (lines 777-921):
```python
# 18 capacities (6 plants/SC × 3 SKUs)
# PARA500: 50,000/day at plants, 30,000/day at SC
# IBUP400: 40,000/day at plants, 25,000/day at SC
# AZITH500: 10,000/day at plants, 5,000/day at SC
```

### scripts/phase2/validate_phase2.py

**Checks:**
- COUNT(boms) = 9
- COUNT(transportation_lanes) = 24
- COUNT(plant_capacities) = 18
- All foreign keys valid
- No self-loops in lanes
- BOM quantities > 0

---

## Phase 3: Rules & Constraints (4 scripts)

### scripts/phase3/generate_inventory_rules.py

**Data** (lines 1047-1322):
```python
# 9 rules
# FAST FG at regional WH: 15 days safety stock
# SLOW FG at regional WH: 5 days safety stock
# RM at plant WH: 5 days safety stock
```

### scripts/phase3/generate_validation_rules.py

**Data** (lines 1324-1430):
```python
# 15 rules
# BOM quantity: > 0 and < 0.01kg
# Inventory quantity: >= 0
# Transit time: >= 0
```

### scripts/phase3/generate_optimization_constraints.py

**Data** (lines 1432-1467):
```python
# 8 constraints
# Max production cost: $5.00/unit
# Max transport cost: $0.50/unit
# Min service level: 95%
```

### scripts/phase3/validate_phase3.py

---

## Phase 4: Historical Data (7 scripts)

### scripts/phase4/download_kaggle_data.py

```python
import os
import kaggle

# Set Kaggle credentials from .env
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

# Download dataset
kaggle.api.dataset_download_files(
    'annemark/global-pharmacy-sales-dataset-20202025',
    path='data/raw',
    unzip=True
)
```

### scripts/phase4/clean_kaggle_data.py

**Cleaning logic** (lines 2108-2413):
- Map product names → our codes
- Aggregate daily → monthly
- Split regions (North America → NORTH/EAST/WEST/SOUTH)
- Remove outliers
- Fill gaps

### scripts/phase4/generate_historical_events.py

**Data** (lines 2415-2518):
```python
# 6 events
# COVID-19: 2020-03-01 to 2021-12-31
# Flu Season 2021-Q4, 2022-Q4, 2023-Q4
# Supply Crisis: 2021-08-01 to 2021-11-30
# Russia-Ukraine War: 2022-02-24 to ongoing
```

### scripts/phase4/generate_demand_plans.py

**Uses cleaned Kaggle data** → 864 rows (3 items × 4 regions × 72 months)

### scripts/phase4/generate_supply_plans.py

**Data** (lines 2640-2750):
648 rows (3 items × 3 production locations × 72 months)

### scripts/phase4/generate_inventory_movements.py

**Data** (lines 2752-2860):
1,944 rows (transfers between warehouses)

### scripts/phase4/validate_phase4.py

---

## Phase 5: Current State (2 scripts)

### scripts/phase5/generate_current_inventory.py

**Logic** (lines 1968-2098):
- Query last month supply_plans
- Calculate current inventory based on historical data
- 56 rows (24 FG + 32 RM)

### scripts/phase5/validate_phase5.py

---

## Phase 6: Provenance (4 scripts)

### scripts/phase6/generate_inventory_provenance.py

**Data** (lines 3636-3840):
56 rows (1 per current_inventory)
- trust_level: high/medium/low
- verification_method: system_count/manual_count

### scripts/phase6/generate_demand_provenance.py

**Data** (lines 3842-3970):
72 rows (recent demand plans)

### scripts/phase6/generate_manual_adjustments.py

**Data** (lines 3972-4040):
20 rows (audit trail)

### scripts/phase6/validate_phase6.py

---

## Phase 7: Goals & Targets (5 scripts)

### scripts/phase7/generate_service_level_goals.py

**Data** (lines 4816-4880):
4 rows (95% on-time, 98% in-stock, etc.)

### scripts/phase7/generate_inventory_goals.py

**Data** (lines 4882-4912):
5 rows (max days supply by SKU category)

### scripts/phase7/generate_cost_goals.py

**Data** (lines 4914-4920):
3 rows (production cost, transport cost, carrying cost)

### scripts/phase7/generate_operational_goals.py

**Data** (lines 4922-4927):
3 rows (lead time, batch size, order cycle)

### scripts/phase7/validate_phase7.py

---

## Phase 8: User Context (4 scripts)

### scripts/phase8/generate_users.py

**Data** (lines 5624-5684):
20 users (3 executives, 4 plant managers, 4 SC managers, 3 demand planners, 4 WH managers, 2 analysts)

### scripts/phase8/generate_user_preferences.py

**Data** (lines 5686-5713):
25 rows (~1-2 per user)

### scripts/phase8/generate_interaction_history.py

**Data** (lines 5715-5735):
75 rows (last 30 days queries)

### scripts/phase8/validate_phase8.py

---

## Phase 9: Outcomes & Feedback (4 scripts)

### scripts/phase9/generate_agent_recommendations.py

**Data** (lines 6399-6456):
50 rows (past 60 days recommendations)

### scripts/phase9/generate_recommendation_outcomes.py

**Data** (lines 6458-6476):
35 rows (outcomes for 35 of 50 recommendations)

### scripts/phase9/generate_user_feedback.py

**Data** (lines 6478-6500):
55 rows (ratings, comments)

### scripts/phase9/validate_phase9.py

---

## Phase 10: Exceptions & Alerts (4 scripts)

### scripts/phase10/generate_exception_rules.py

**Data** (lines 7122-7180):
9 rules (stockout risk thresholds, quality deviation, compliance deadlines)

### scripts/phase10/generate_active_exceptions.py

**Data** (lines 7182-7212):
8 active alerts (critical stockouts, safety stock breaches)

### scripts/phase10/generate_exception_history.py

**Data** (lines 7214-7220):
5 resolved alerts

### scripts/phase10/validate_phase10.py

---

## Quick Reference: Extract Data from SNOP_DATA_GENERATION_PLAN.md

**Line ranges for each phase data:**

| Phase | File | Lines |
|-------|------|-------|
| 2 BOM | generate_boms.py | 545-643 |
| 2 Lanes | generate_transportation_lanes.py | 645-775 |
| 2 Capacity | generate_plant_capacities.py | 777-921 |
| 3 Inventory Rules | generate_inventory_rules.py | 1047-1322 |
| 3 Validation Rules | generate_validation_rules.py | 1324-1430 |
| 3 Opt Constraints | generate_optimization_constraints.py | 1432-1467 |
| 4 Events | generate_historical_events.py | 2415-2518 |
| 4 Demand | generate_demand_plans.py | 2520-2638 (uses cleaned Kaggle) |
| 4 Supply | generate_supply_plans.py | 2640-2750 |
| 4 Movements | generate_inventory_movements.py | 2752-2860 |
| 5 Inventory | generate_current_inventory.py | 1968-2098 |
| 6 Inv Prov | generate_inventory_provenance.py | 3636-3840 |
| 6 Demand Prov | generate_demand_provenance.py | 3842-3970 |
| 6 Adjustments | generate_manual_adjustments.py | 3972-4040 |
| 7 Service | generate_service_level_goals.py | 4816-4880 |
| 7 Inventory | generate_inventory_goals.py | 4882-4912 |
| 7 Cost | generate_cost_goals.py | 4914-4920 |
| 7 Operational | generate_operational_goals.py | 4922-4927 |
| 8 Users | generate_users.py | 5624-5684 |
| 8 Preferences | generate_user_preferences.py | 5686-5713 |
| 8 Interactions | generate_interaction_history.py | 5715-5735 |
| 9 Recommendations | generate_agent_recommendations.py | 6399-6456 |
| 9 Outcomes | generate_recommendation_outcomes.py | 6458-6476 |
| 9 Feedback | generate_user_feedback.py | 6478-6500 |
| 10 Rules | generate_exception_rules.py | 7122-7180 |
| 10 Active | generate_active_exceptions.py | 7182-7212 |
| 10 History | generate_exception_history.py | 7214-7220 |

---

## Implementation Strategy

**Option 1: Manual (Recommended for learning)**
1. Read SNOP_DATA_GENERATION_PLAN.md line ranges above
2. Copy code blocks into script files
3. Adapt to script template pattern
4. Test each script individually

**Option 2: Automated**
Use LLM/Claude Code to:
1. Read plan sections
2. Generate scripts following template
3. Validate against expected row counts

**Option 3: Hybrid**
1. Create critical phases manually (2, 4)
2. Generate boilerplate phases with LLM (3, 6, 7, 8, 9, 10)
3. Validate all

---

## Testing Individual Scripts

```bash
# Test Phase 2 script
python scripts/phase2/generate_boms.py

# Check result
psql -d snop_db -c "SELECT COUNT(*) FROM boms;"
# Should return 9

# Test Phase 4 (Kaggle download)
python scripts/phase4/download_kaggle_data.py
ls -lh data/raw/*.csv
# Should see pharmacy_sales CSV ~50MB
```

---

## Status

- ✅ Phase 1: 4/4 scripts created
- ⏸️ Phase 2: 0/4 scripts (data ready in plan, template available)
- ⏸️ Phase 3: 0/4 scripts
- ⏸️ Phase 4: 0/7 scripts (critical - Kaggle integration)
- ⏸️ Phase 5: 0/2 scripts
- ⏸️ Phase 6: 0/4 scripts
- ⏸️ Phase 7: 0/5 scripts
- ⏸️ Phase 8: 0/4 scripts
- ⏸️ Phase 9: 0/4 scripts
- ⏸️ Phase 10: 0/4 scripts

**Total:** 4/42 scripts created (10% complete)

**Next:** Create Phase 2-10 scripts using template + data from SNOP_DATA_GENERATION_PLAN.md
