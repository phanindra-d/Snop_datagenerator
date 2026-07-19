# SNOP Data Generator - Phase Details & Schemas

**Technical Reference for Database Schema & Script Outputs**

This document contains complete table schemas, row counts, and validation criteria for all 10 phases.

---

## Phase 1: Master Data (37 rows)

### Tables Created

#### 1.1 regions (4 rows)

**Purpose:** Geographic regions for supply chain network segmentation

**Schema:**
```sql
CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Data:**
- NORTH - North Region
- EAST - East Region
- WEST - West Region
- SOUTH - South Region

**Validation:**
- `COUNT(*) = 4`
- All codes unique
- No NULL in required fields

---

#### 1.2 location_nodes (18 rows)

**Purpose:** Unified table for all supply chain nodes (plants, warehouses, subcontractors, distributors)

**Schema:**
```sql
CREATE TYPE location_type AS ENUM (
    'PLANT', 
    'WAREHOUSE_PLANT', 
    'WAREHOUSE_REGIONAL', 
    'DISTRIBUTOR', 
    'SUBCONTRACTOR'
);

CREATE TABLE location_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    type location_type NOT NULL,
    region_id UUID NOT NULL REFERENCES regions(id),
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Breakdown:**
- 4 PLANT (company-owned manufacturing)
- 2 SUBCONTRACTOR (outsourced manufacturing)
- 4 WAREHOUSE_PLANT (co-located with plants)
- 4 WAREHOUSE_REGIONAL (regional distribution centers)
- 4 DISTRIBUTOR (customer-facing)

**Validation:**
- `COUNT(*) = 18`
- `COUNT WHERE type = 'PLANT' = 4`
- All `region_id` exist in regions table
- Lat/lon optional (can be NULL)

---

#### 1.3 items (11 rows)

**Purpose:** Product catalog (finished goods + raw materials)

**Schema:**
```sql
CREATE TYPE item_type AS ENUM (
    'FINISHED_GOOD', 
    'RAW_MATERIAL', 
    'SEMI_FINISHED', 
    'EXCIPIENT'
);

CREATE TYPE sku_category AS ENUM ('FAST', 'SLOW');

CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    type item_type NOT NULL,
    volume_category sku_category,  -- Only for FINISHED_GOOD
    unit_of_measure VARCHAR(20) NOT NULL,  -- KG, EA, L
    default_supplier_id UUID REFERENCES location_nodes(id),  -- For raw materials
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Finished Goods (3):**
- PARA500 (Paracetamol 500mg) - FAST
- IBUP400 (Ibuprofen 400mg) - FAST
- AZITH500 (Azithromycin 500mg) - SLOW

**Raw Materials (8):**
- API-PARA, API-IBUP, API-AZITH (Active Pharmaceutical Ingredients)
- EXC-STARCH, EXC-MCC, EXC-GELATIN, EXC-GLYCERIN, EXC-LACTOSE (Excipients)

**Validation:**
- `COUNT(*) = 11`
- `COUNT WHERE type = 'FINISHED_GOOD' = 3`
- `COUNT WHERE type = 'RAW_MATERIAL' = 8`
- All codes unique
- FAST/SLOW only for finished goods

---

## Phase 2: Relationships (51 rows)

### Tables Created

#### 2.1 boms (9 rows)

**Purpose:** Bill of Materials - recipe for making finished goods

**Schema:**
```sql
CREATE TABLE boms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_item_id UUID NOT NULL REFERENCES items(id),  -- Finished good
    child_item_id UUID NOT NULL REFERENCES items(id),   -- Raw material
    quantity_per_unit DECIMAL(12, 6) NOT NULL,          -- KG per unit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    UNIQUE(parent_item_id, child_item_id)
);
```

**Example:**
- PARA500 → API-PARA: 0.0005 kg (500mg tablet needs 500mg API)
- PARA500 → EXC-STARCH: 0.00015 kg
- PARA500 → EXC-MCC: 0.0002 kg

**Validation:**
- `COUNT(*) = 9` (3 FG × ~3 materials each)
- All quantities > 0
- No circular dependencies (FG can't depend on itself)
- parent = FINISHED_GOOD, child = RAW_MATERIAL

---

#### 2.2 transportation_lanes (24 rows)

**Purpose:** Valid shipping routes between locations

**Schema:**
```sql
CREATE TABLE transportation_lanes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_location_id UUID NOT NULL REFERENCES location_nodes(id),
    to_location_id UUID NOT NULL REFERENCES location_nodes(id),
    transit_time_days DECIMAL(4, 1) NOT NULL,
    cost_per_unit DECIMAL(10, 2),
    mode VARCHAR(50),  -- TRUCK, RAIL, AIR
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    UNIQUE(from_location_id, to_location_id),
    CHECK (from_location_id != to_location_id)
);
```

**Patterns:**
- Plant → Plant WH (same location, 0 days)
- Plant WH → Regional WH (2 days truck)
- Regional WH → Distributor (1 day truck)
- Subcontractor → Plant WH (3 days)

**Validation:**
- `COUNT(*) = 24`
- All transit_time ≥ 0
- No self-loops (from != to)
- All location IDs valid

---

#### 2.3 plant_capacities (18 rows)

**Purpose:** Production capacity per plant/subcontractor per SKU

**Schema:**
```sql
CREATE TABLE plant_capacities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES location_nodes(id),
    item_id UUID NOT NULL REFERENCES items(id),
    capacity_per_day INTEGER NOT NULL,  -- Units/day
    is_owned BOOLEAN DEFAULT TRUE,       -- TRUE = company plant, FALSE = subcontractor
    outsourcing_premium DECIMAL(5, 2),  -- 1.25 = 25% cost premium
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    UNIQUE(location_id, item_id)
);
```

**Example:**
- Plant North Alpha × PARA500: 50,000 units/day
- Plant North Alpha × IBUP400: 40,000 units/day
- SubContractor NorthEast × PARA500: 30,000 units/day (outsourcing_premium = 1.15)

**Validation:**
- `COUNT(*) = 18` (6 plants/SCs × 3 SKUs)
- capacity_per_day > 0
- Subcontractors have outsourcing_premium > 1.0

---

## Phase 3: Rules & Constraints (32 rows)

### Tables Created

#### 3.1 inventory_rules (9 rows)

**Purpose:** Safety stock and inventory policy rules

**Schema:**
```sql
CREATE TYPE rule_type AS ENUM ('SAFETY_STOCK', 'MAX_STOCK', 'REORDER_POINT');

CREATE TABLE inventory_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    rule_type rule_type NOT NULL,
    item_id UUID REFERENCES items(id),          -- NULL = applies to all
    location_type location_type,                 -- NULL = applies to all
    min_days_supply INTEGER,
    max_days_supply INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Examples:**
- FAST finished goods at regional WH: 15 days safety stock
- SLOW finished goods at regional WH: 5 days safety stock
- Raw materials at plant WH: 5 days safety stock

**Validation:**
- `COUNT(*) = 9`
- min_days ≤ max_days
- All rule_codes unique

---

#### 3.2 validation_rules (15 rows)

**Purpose:** Data quality and business validation rules

**Schema:**
```sql
CREATE TYPE validation_type AS ENUM (
    'RANGE_CHECK',
    'MANDATORY_FIELD',
    'RELATIONSHIP_CHECK',
    'BUSINESS_LOGIC'
);

CREATE TABLE validation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    validation_type validation_type NOT NULL,
    target_table VARCHAR(100),
    condition_sql TEXT,  -- WHERE clause for validation
    error_message TEXT,
    severity VARCHAR(20),  -- ERROR, WARNING
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Examples:**
- BOM quantity must be > 0 and < 0.01kg (realistic for tablets)
- Inventory quantity must be non-negative
- Transportation lane transit time must be ≥ 0

**Validation:**
- `COUNT(*) = 15`
- All severity in (ERROR, WARNING)

---

#### 3.3 optimization_constraints (8 rows)

**Purpose:** Constraints for optimization algorithms (future LP/MIP solvers)

**Schema:**
```sql
CREATE TYPE constraint_type AS ENUM (
    'CAPACITY',
    'BUDGET',
    'SERVICE_LEVEL',
    'LEAD_TIME'
);

CREATE TABLE optimization_constraints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    constraint_code VARCHAR(50) UNIQUE NOT NULL,
    constraint_name VARCHAR(200) NOT NULL,
    constraint_type constraint_type NOT NULL,
    min_value DECIMAL(15, 2),
    max_value DECIMAL(15, 2),
    unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Examples:**
- Max production cost per unit: $5.00
- Min service level: 95%
- Max lead time: 14 days

**Validation:**
- `COUNT(*) = 8`
- min_value ≤ max_value where both present

---

## Phase 4: Historical Data (3,462 rows)

### Tables Created

#### 4.1 historical_events (6 rows)

**Purpose:** Major events affecting supply/demand

**Schema:**
```sql
CREATE TYPE event_type AS ENUM (
    'PANDEMIC',
    'SEASONAL',
    'SUPPLY_DISRUPTION',
    'GEOPOLITICAL',
    'REGULATORY'
);

CREATE TABLE historical_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_code VARCHAR(50) UNIQUE NOT NULL,
    event_name VARCHAR(200) NOT NULL,
    event_type event_type NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    affected_items TEXT,  -- JSON array of item codes
    affected_regions TEXT,  -- JSON array of region codes
    impact_description TEXT,
    demand_impact_multiplier DECIMAL(5, 2),  -- 1.5 = +50% demand
    supply_impact_multiplier DECIMAL(5, 2),  -- 0.8 = -20% supply
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Events:**
1. COVID-19 (March 2020 - Dec 2021) - demand +200% for PARA500
2. Flu Season 2021-Q4 (Oct 2021 - Feb 2022) - demand +25%
3. Supply Crisis (Aug 2021 - Nov 2021) - supply -30%
4. Flu Season 2022-Q4 (Oct 2022 - Feb 2023) - demand +25%
5. Russia-Ukraine War (Feb 2022 - ongoing) - supply -15%
6. Flu Season 2023-Q4 (Oct 2023 - Feb 2024) - demand +25%

**Validation:**
- `COUNT(*) = 6`
- start_date < end_date (where end_date not NULL)

---

#### 4.2 demand_plans (864 rows)

**Purpose:** Historical demand (2020-2025, monthly)

**Schema:**
```sql
CREATE TYPE bucket_type AS ENUM ('MONTHLY', 'WEEKLY', 'DAILY');
CREATE TYPE plan_type AS ENUM ('HISTORICAL', 'FORECAST');

CREATE TABLE demand_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id),
    location_id UUID NOT NULL REFERENCES location_nodes(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    bucket_type bucket_type NOT NULL,
    plan_type plan_type NOT NULL,
    quantity INTEGER NOT NULL,
    scenario_id UUID,  -- For what-if analysis
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:**
- 3 items (PARA500, IBUP400, AZITH500)
- 4 regions
- 72 months (2020-01 to 2025-12)
- **Total: 3 × 4 × 72 = 864 rows**

**Data Source:** Kaggle "Global Pharmacy Sales 2020-2025" dataset (real pharmaceutical sales data)

**Validation:**
- `COUNT(*) = 864`
- quantity ≥ 0
- period_start < period_end

---

#### 4.3 supply_plans (648 rows)

**Purpose:** Historical production output

**Schema:**
```sql
CREATE TABLE supply_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id),
    location_id UUID NOT NULL REFERENCES location_nodes(id),  -- Which plant
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    bucket_type bucket_type NOT NULL,
    plan_type plan_type NOT NULL,
    quantity INTEGER NOT NULL,
    scenario_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:**
- 3 items
- 3 production locations (subset of plants)
- 72 months
- **Total: 3 × 3 × 72 = 648 rows**

**Validation:**
- `COUNT(*) = 648`
- quantity ≥ 0
- Aligns with plant_capacities (monthly output ≤ 30 × daily capacity)

---

#### 4.4 inventory_movements (1,944 rows)

**Purpose:** Historical warehouse transfers

**Schema:**
```sql
CREATE TYPE movement_type AS ENUM (
    'TRANSFER_IN',
    'TRANSFER_OUT',
    'PRODUCTION',
    'CONSUMPTION',
    'ADJUSTMENT'
);

CREATE TABLE inventory_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id),
    location_id UUID NOT NULL REFERENCES location_nodes(id),
    movement_type movement_type NOT NULL,
    quantity INTEGER NOT NULL,
    movement_date DATE NOT NULL,
    reference_id UUID,  -- Link to transfer/production record
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:**
- 3 items
- 18 locations
- 36 months (last 3 years, more recent = more transfers)
- ~**3 movements/location/month avg = 1,944 rows**

**Validation:**
- `COUNT(*) ≈ 1,944`
- TRANSFER_IN has matching TRANSFER_OUT at different location

---

## Phase 5: Current State (56 rows)

### Tables Created

#### 5.1 current_inventory (56 rows)

**Purpose:** Current inventory snapshot (as of today)

**Schema:**
```sql
CREATE TABLE current_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id),
    location_id UUID NOT NULL REFERENCES location_nodes(id),
    quantity_on_hand INTEGER NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    UNIQUE(item_id, location_id)
);
```

**Coverage:**
- 3 finished goods × 8 warehouses = 24 FG rows
- 8 raw materials × 4 plant warehouses = 32 RM rows
- **Total: 56 rows**

**Data Logic:**
- Calculated from Phase 4 (last month supply_plans + inventory_movements)
- Realistic quantities (FAST SKUs higher than SLOW)

**Validation:**
- `COUNT(*) = 56`
- quantity_on_hand ≥ 0
- All item/location pairs unique

---

## Phase 6: Provenance (148 rows)

### Tables Created

#### 6.1 inventory_provenance (56 rows)

**Purpose:** Trust and source tracking for inventory data

**Schema:**
```sql
CREATE TYPE trust_level AS ENUM ('high', 'medium', 'low');
CREATE TYPE verification_method AS ENUM ('system_count', 'manual_count', 'estimated', 'derived');

CREATE TABLE inventory_provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_id UUID NOT NULL REFERENCES current_inventory(id),
    data_source VARCHAR(200),  -- "WMS_system", "manual_entry", etc.
    trust_level trust_level NOT NULL,
    verification_method verification_method NOT NULL,
    last_verified_at TIMESTAMP,
    verified_by VARCHAR(200),
    data_age_hours INTEGER,  -- How old is this data?
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** 1 provenance record per inventory row (56)

**Validation:**
- `COUNT(*) = 56`
- All inventory_id exist in current_inventory
- data_age_hours ≥ 0

---

#### 6.2 demand_provenance (72 rows)

**Purpose:** Trust tracking for demand forecasts

**Schema:**
```sql
CREATE TYPE forecast_method AS ENUM ('ml_model', 'statistical', 'manual', 'hybrid');

CREATE TABLE demand_provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    demand_plan_id UUID NOT NULL REFERENCES demand_plans(id),
    forecast_method forecast_method NOT NULL,
    trust_level trust_level NOT NULL,
    model_accuracy_pct DECIMAL(5, 2),  -- Historical accuracy
    overridden_by_planner BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** Sample of 72 recent demand plans (last 6 months)

**Validation:**
- `COUNT(*) = 72`
- model_accuracy between 0-100

---

#### 6.3 manual_adjustments (20 rows)

**Purpose:** Audit trail for human overrides

**Schema:**
```sql
CREATE TABLE manual_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_table VARCHAR(100) NOT NULL,  -- "current_inventory", "demand_plans"
    target_id UUID NOT NULL,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    adjustment_reason TEXT,
    adjusted_by VARCHAR(200) NOT NULL,
    adjustment_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** 20 historical manual adjustments (inventory corrections, forecast overrides)

**Validation:**
- `COUNT(*) = 20`
- adjustment_date ≤ NOW()

---

## Phase 7: Goals & Targets (15 rows)

### Tables Created

#### 7.1 service_level_goals (4 rows)

**Purpose:** Delivery performance targets

**Schema:**
```sql
CREATE TABLE service_level_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_code VARCHAR(50) UNIQUE NOT NULL,
    goal_name VARCHAR(200) NOT NULL,
    target_pct DECIMAL(5, 2) NOT NULL,  -- 95.0 = 95%
    scope VARCHAR(200),  -- "All regions", "FAST SKUs only"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Goals:**
- On-time delivery: 95%
- In-stock availability: 98%
- Order fill rate: 97%
- Perfect order rate: 90%

**Validation:**
- `COUNT(*) = 4`
- target_pct between 0-100

---

#### 7.2 inventory_goals (5 rows)

**Purpose:** Inventory level targets

**Schema:**
```sql
CREATE TABLE inventory_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_code VARCHAR(50) UNIQUE NOT NULL,
    goal_name VARCHAR(200) NOT NULL,
    target_days_supply INTEGER,
    applies_to_category sku_category,  -- FAST or SLOW
    applies_to_location_type location_type,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Goals:**
- FAST SKUs max inventory: 30 days
- SLOW SKUs max inventory: 60 days
- Raw materials safety stock: 5 days
- Finished goods safety stock (FAST): 15 days
- Finished goods safety stock (SLOW): 5 days

**Validation:**
- `COUNT(*) = 5`
- target_days_supply > 0

---

#### 7.3 cost_goals (3 rows)

**Purpose:** Cost optimization targets

**Schema:**
```sql
CREATE TABLE cost_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_code VARCHAR(50) UNIQUE NOT NULL,
    goal_name VARCHAR(200) NOT NULL,
    target_value DECIMAL(15, 2) NOT NULL,
    unit VARCHAR(50),  -- "USD_per_unit", "percent"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Goals:**
- Max production cost per unit: $5.00
- Max transportation cost per unit: $0.50
- Target inventory carrying cost: 15% of value per year

**Validation:**
- `COUNT(*) = 3`
- target_value > 0

---

#### 7.4 operational_goals (3 rows)

**Purpose:** Operational efficiency targets

**Schema:**
```sql
CREATE TABLE operational_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_code VARCHAR(50) UNIQUE NOT NULL,
    goal_name VARCHAR(200) NOT NULL,
    target_value DECIMAL(15, 2) NOT NULL,
    unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Goals:**
- Max production lead time: 7 days
- Min batch size: 10,000 units
- Max order cycle time: 3 days

**Validation:**
- `COUNT(*) = 3`

---

## Phase 8: User Context (120 rows)

### Tables Created

#### 8.1 users (20 rows)

**Purpose:** User accounts for personalization

**Schema:**
```sql
CREATE TYPE user_role AS ENUM (
    'EXECUTIVE',
    'PLANT_MANAGER',
    'SC_MANAGER',
    'DEMAND_PLANNER',
    'WH_MANAGER',
    'ANALYST'
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(200) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role user_role NOT NULL,
    region_id UUID REFERENCES regions(id),
    location_id UUID REFERENCES location_nodes(id),  -- For plant/wh managers
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Users:**
- 3 Executives
- 4 Plant Managers (1 per region)
- 4 Supply Chain Managers (1 per region)
- 3 Demand Planners
- 4 Warehouse Managers
- 2 Analysts

**Total: 20 users**

**Validation:**
- `COUNT(*) = 20`
- All emails unique

---

#### 8.2 user_preferences (25 rows)

**Purpose:** Personalization settings

**Schema:**
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    UNIQUE(user_id, preference_key)
);
```

**Preference Keys:**
- `ui_format`: "table" | "chart" | "executive_summary"
- `notifications_enabled`: "true" | "false"
- `default_time_range`: "7days" | "30days" | "90days"
- `preferred_units`: "metric" | "imperial"
- `dashboard_layout`: JSON string

**Coverage:** ~1-2 preferences per user (25 rows)

**Validation:**
- `COUNT(*) = 25`
- All user_id exist in users

---

#### 8.3 interaction_history (75 rows)

**Purpose:** User query history for context

**Schema:**
```sql
CREATE TABLE interaction_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    interaction_type VARCHAR(50),  -- "query", "action", "view"
    interaction_content TEXT,
    response_content TEXT,
    interaction_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** Last 30 days of queries, ~3-4 per user (75 rows)

**Validation:**
- `COUNT(*) = 75`
- interaction_timestamp ≤ NOW()

---

## Phase 9: Outcomes & Feedback (140 rows)

### Tables Created

#### 9.1 agent_recommendations (50 rows)

**Purpose:** AI agent recommendations history

**Schema:**
```sql
CREATE TABLE agent_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_code VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    recommendation_type VARCHAR(100),  -- "order", "transfer", "adjust_forecast"
    recommendation_text TEXT NOT NULL,
    confidence_score DECIMAL(5, 2),  -- 0-100
    generated_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** 50 historical recommendations (past 60 days)

**Validation:**
- `COUNT(*) = 50`
- confidence_score between 0-100

---

#### 9.2 recommendation_outcomes (35 rows)

**Purpose:** What happened after recommendation

**Schema:**
```sql
CREATE TYPE outcome_status AS ENUM (
    'ACCEPTED',
    'REJECTED',
    'PARTIALLY_ACCEPTED',
    'PENDING'
);

CREATE TABLE recommendation_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID NOT NULL REFERENCES agent_recommendations(id),
    outcome_status outcome_status NOT NULL,
    action_taken TEXT,
    actual_result TEXT,  -- "Stockout prevented", "Cost saved $1,200"
    outcome_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** 35 of 50 recommendations have outcomes (15 still pending)

**Validation:**
- `COUNT(*) = 35`
- All recommendation_id exist

---

#### 9.3 user_feedback (55 rows)

**Purpose:** User ratings and comments

**Schema:**
```sql
CREATE TYPE feedback_sentiment AS ENUM ('positive', 'neutral', 'negative');

CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID NOT NULL REFERENCES agent_recommendations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    sentiment feedback_sentiment NOT NULL,
    rating INTEGER,  -- 1-5 stars
    comment TEXT,
    feedback_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    CHECK (rating BETWEEN 1 AND 5)
);
```

**Coverage:** 55 feedback records (some recommendations have multiple users' feedback)

**Validation:**
- `COUNT(*) = 55`
- rating between 1-5

---

## Phase 10: Exceptions & Alerts (22 rows)

### Tables Created

#### 10.1 exception_rules (9 rows)

**Purpose:** Detection rules for proactive monitoring

**Schema:**
```sql
CREATE TYPE exception_type AS ENUM (
    'STOCKOUT_RISK',
    'EXCESS_INVENTORY',
    'SAFETY_STOCK_BREACH',
    'QUALITY_DEVIATION',
    'DEMAND_SPIKE',
    'DEMAND_DROP',
    'LATE_DELIVERY',
    'COMPLIANCE_DEADLINE'
);

CREATE TYPE severity_level AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW');

CREATE TABLE exception_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    exception_type exception_type NOT NULL,
    severity severity_level NOT NULL,
    applies_to_item_id UUID REFERENCES items(id),  -- NULL = all items
    applies_to_location_id UUID REFERENCES location_nodes(id),
    threshold_value DECIMAL(15, 2),
    threshold_unit VARCHAR(50),  -- "days", "percent", "kg"
    condition_sql TEXT,
    notify_users TEXT,  -- JSON array of user IDs
    auto_escalate_hours INTEGER,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Rules:**
- Stockout risk < 2 days → CRITICAL
- Stockout risk 2-5 days → HIGH
- Safety stock breach → HIGH
- Excess inventory > 60 days → MEDIUM
- Quality deviation > 10% → HIGH
- Demand spike > 150% → HIGH
- Demand drop < 50% → MEDIUM
- Late delivery > 2 days → HIGH
- Compliance deadline < 10 days → HIGH

**Validation:**
- `COUNT(*) = 9`
- All enabled rules have thresholds

---

#### 10.2 active_exceptions (8 rows)

**Purpose:** Current alerts requiring attention

**Schema:**
```sql
CREATE TYPE exception_status AS ENUM ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'DISMISSED');

CREATE TABLE active_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exception_rule_id UUID NOT NULL REFERENCES exception_rules(id),
    exception_type exception_type NOT NULL,
    severity severity_level NOT NULL,
    status exception_status DEFAULT 'ACTIVE',
    affected_item_id UUID REFERENCES items(id),
    affected_location_id UUID REFERENCES location_nodes(id),
    affected_period DATE,
    detected_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    current_value DECIMAL(15, 2),
    threshold_value DECIMAL(15, 2),
    deviation_pct DECIMAL(5, 2),
    alert_title VARCHAR(200) NOT NULL,
    alert_message TEXT NOT NULL,
    recommended_actions TEXT,  -- JSON array
    assigned_to_user_id UUID REFERENCES users(id),
    assigned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** 8 active alerts (mix of CRITICAL/HIGH/MEDIUM)

**Example:**
- CRITICAL: Stockout risk API-PARA at Plant North (2 days remaining)
- HIGH: Safety stock breach PARA500 at Regional WH East
- MEDIUM: Excess inventory AZITH500 at Regional WH South

**Validation:**
- `COUNT(*) = 8`
- detected_at ≤ NOW()
- resolved_at > acknowledged_at (if both set)

---

#### 10.3 exception_history (5 rows)

**Purpose:** Resolved alerts for learning

**Schema:**
```sql
CREATE TABLE exception_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    active_exception_id UUID NOT NULL,  -- Link to original active_exception
    exception_type exception_type NOT NULL,
    severity severity_level NOT NULL,
    status exception_status NOT NULL,
    affected_item_code VARCHAR(50),
    affected_location_name VARCHAR(200),
    detected_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    duration_hours INTEGER,
    alert_message TEXT NOT NULL,
    resolution_action TEXT,
    resolved_by_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

**Coverage:** 5 resolved historical alerts (stockouts prevented, quality issues fixed)

**Validation:**
- `COUNT(*) = 5`
- status = 'RESOLVED'
- resolved_at NOT NULL

---

## Summary: All Phases

| Phase | Tables | Total Rows | Script Count |
|-------|--------|------------|--------------|
| 1 | 3 | 37 | 4 (3 gen + 1 val) |
| 2 | 3 | 51 | 4 (3 gen + 1 val) |
| 3 | 3 | 32 | 4 (3 gen + 1 val) |
| 4 | 4 | 3,462 | 7 (6 gen + 1 val) |
| 5 | 1 | 56 | 2 (1 gen + 1 val) |
| 6 | 3 | 148 | 4 (3 gen + 1 val) |
| 7 | 4 | 15 | 5 (4 gen + 1 val) |
| 8 | 3 | 120 | 4 (3 gen + 1 val) |
| 9 | 3 | 140 | 4 (3 gen + 1 val) |
| 10 | 3 | 22 | 4 (3 gen + 1 val) |

**Grand Total:**
- **30 tables**
- **4,083 rows**
- **42 Python scripts**

---

## Database Size Estimates

**Storage:**
- Master/Relationships/Rules: ~50 KB
- Historical data: ~5 MB (Kaggle dataset)
- Current state/Provenance: ~100 KB
- Goals/User/Feedback: ~200 KB
- Exceptions: ~50 KB

**Total DB size:** ~6 MB (tiny, optimized for mock data)

---

## Notes for Developers

1. **All IDs are UUIDs** - Do not use `serial` or `integer` for primary keys
2. **Foreign keys enforced** - Database will reject orphan rows
3. **Enums used** - String constants defined at DB level, not just application level
4. **Audit fields everywhere** - Every table has created_at, updated_at, created_by, is_active, version
5. **Soft deletes** - Use `is_active = FALSE` instead of `DELETE`
6. **Versioning** - Increment `version` on UPDATE for optimistic locking

---

**Last Updated:** 2026-07-20  
**Schema Version:** 1.0  
**Total Tables:** 30  
**Total Rows:** 4,083
