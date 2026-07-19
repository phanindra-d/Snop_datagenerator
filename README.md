# SNOP Data Generator

Production-grade data generation system for SNOP (Sales & Operations Planning) application to enable Agentic AI agents.

## Overview

This folder contains all scripts and documentation to generate **4,083 rows** of enterprise-quality mock data across **10 data pattern types** that enable AI agents to function effectively.

### What Gets Generated

| Phase | Data Pattern Type | Rows | Description |
|-------|-------------------|------|-------------|
| 1 | Master Data | 37 | Core entities: regions, locations, items/SKUs |
| 2 | Relationships | 51 | BOMs, transportation lanes, capacities |
| 3 | Rules & Constraints | 32 | Inventory rules, validation rules, optimization constraints |
| 4 | Historical Data | 3,462 | Time-series demand/supply with real events (COVID, flu seasons) |
| 5 | Current State | 56 | Current inventory snapshot |
| 6 | Provenance | 148 | Data lineage, trust levels, source tracking |
| 7 | Goals & Targets | 15 | Service levels, inventory targets, cost goals |
| 8 | User Context | 120 | Users, preferences, interaction history |
| 9 | Outcomes & Feedback | 140 | Agent recommendations, outcomes, user feedback |
| 10 | Exceptions & Alerts | 22 | Active alerts, exception rules, history |

**Total: 4,083 rows**

---

## Why These 10 Phases?

### Design Philosophy: AI Agent Data Requirements

Agentic AI requires **12 data pattern types** to function effectively. We implemented **10 of 12** in this version:

#### ✅ Implemented (10 types)

1. **Master Data** - Foundation entities agents reference
2. **Historical Data** - Past patterns agents learn from (with real Kaggle dataset)
3. **Relationships** - Graph connections agents traverse
4. **Rules & Constraints** - Boundaries agents respect
5. **Provenance** - Trust signals agents use for confidence scoring
6. **Current State** - Real-time snapshot agents query
7. **Goals & Targets** - Objectives agents optimize toward
8. **User Context** - Personalization data agents adapt behavior with
9. **Outcomes & Feedback** - Learning loop for agent improvement
10. **Exceptions & Alerts** - Proactive monitoring (agent warns BEFORE problems)

#### ⏸️ Deferred to Future (2 types)

11. **External/Reference Data** - Supplier catalogs, market data, regulations
12. **Predictions/Forecasts** - ML model outputs, demand forecasts

**Rationale:** 10 implemented types provide complete foundation for agent MVP. Types 11-12 add advanced capabilities but aren't blocking for initial agent deployment.

---

## What This Generates

### Business Domain: Pharmaceutical Manufacturing Supply Chain

**Products:**
- PARA500 (Paracetamol 500mg) - Fast-moving
- IBUP400 (Ibuprofen 400mg) - Fast-moving
- AZITH500 (Azithromycin 500mg) - Slow-moving

**Geography:**
- 4 Regions: NORTH, EAST, WEST, SOUTH (NEWS pattern)
- 4 Company plants (1 per region)
- 2 Subcontractors
- 8 Warehouses (4 plant, 4 regional)
- 4 Distributors

**Timeline:**
- Historical: 2020-2025 (6 years)
- Real events: COVID-19, flu seasons, supply crisis, Russia-Ukraine war
- Data source: Kaggle "Global Pharmacy Sales Dataset 2020-2025"

**Data Quality:**
- UUID primary keys (production-grade)
- Auditable base pattern (created_at, updated_at, created_by, is_active, version)
- Foreign key integrity enforced
- Validation scripts included per phase

---

## Database Setup

### Prerequisites

**PostgreSQL 14+** (local or cloud)

Supported platforms:
- Local: PostgreSQL on Windows/Mac/Linux
- Cloud: AWS RDS, Azure Database, Google Cloud SQL, Supabase, Neon, etc.

### Configuration

Create `.env` file in `snop_data_generator/` folder:

```bash
# PostgreSQL Connection
DB_HOST=localhost          # or cloud hostname (e.g., xxx.rds.amazonaws.com)
DB_PORT=5432
DB_NAME=snop_db
DB_USER=postgres
DB_PASSWORD=your_password

# Optional: Full connection string (overrides above if set)
# DATABASE_URL=postgresql://user:password@host:port/dbname
```

**Security Note:** `.env` is gitignored. Never commit credentials.

---

## Installation

### 1. Install Dependencies

**Windows:**
```bash
.\install_dependencies.bat
```

**Mac/Linux:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

This installs:
- Python packages: `psycopg2-binary`, `sqlalchemy`, `pandas`, `numpy`, `python-dotenv`, `kaggle`
- Kaggle CLI (for historical data download)

### 2. Kaggle API Setup (for Phase 4 only)

Phase 4 downloads real pharmacy sales data from Kaggle.

**Steps:**
1. Create Kaggle account at https://www.kaggle.com
2. Go to Account → API → "Create New API Token"
3. Downloads `kaggle.json` file
4. Place in:
   - Windows: `C:\Users\<YourName>\.kaggle\kaggle.json`
   - Mac/Linux: `~/.kaggle/kaggle.json`
5. Set permissions (Mac/Linux only):
   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

**Note:** If you skip this, Phase 4 will fail. Other phases run independently.

---

## Usage

### Run All Phases (Recommended)

**Windows:**
```bash
.\run_all_phases.bat
```

**Mac/Linux:**
```bash
chmod +x run_all_phases.sh
./run_all_phases.sh
```

This executes phases **in dependency order** with validation after each phase. Stops on first error.

### Run Individual Phases

```bash
# Phase 1: Master Data
python scripts/phase1/generate_regions.py
python scripts/phase1/generate_location_nodes.py
python scripts/phase1/generate_items.py
python scripts/phase1/validate_phase1.py

# Phase 2: Relationships
python scripts/phase2/generate_boms.py
python scripts/phase2/generate_transportation_lanes.py
python scripts/phase2/generate_plant_capacities.py
python scripts/phase2/validate_phase2.py

# ... (see run_all_phases.sh for complete order)
```

**⚠️ IMPORTANT:** Phases must run in order (1→2→3→4→5→6→7→8→9→10). Phase N depends on Phase N-1 data.

---

## Execution Order & Dependencies

```
Phase 1 (Master Data)
    ↓ [Regions, LocationNodes, Items]
Phase 2 (Relationships)
    ↓ [BOMs, TransportationLanes, PlantCapacities]
Phase 3 (Rules & Constraints)
    ↓ [InventoryRules, ValidationRules, OptimizationConstraints]
Phase 4 (Historical Data) ← downloads Kaggle dataset
    ↓ [HistoricalEvents, DemandPlans, SupplyPlans, InventoryMovements]
Phase 5 (Current State) ← uses Phase 4 for baseline
    ↓ [CurrentInventory]
Phase 6 (Provenance)
    ↓ [InventoryProvenance, DemandProvenance, ManualAdjustments]
Phase 7 (Goals & Targets)
    ↓ [ServiceLevelGoals, InventoryGoals, CostGoals, OperationalGoals]
Phase 8 (User Context)
    ↓ [Users, UserPreferences, InteractionHistory]
Phase 9 (Outcomes & Feedback)
    ↓ [AgentRecommendations, RecommendationOutcomes, UserFeedback]
Phase 10 (Exceptions & Alerts)
    ↓ [ExceptionRules, ActiveExceptions, ExceptionHistory]
```

**Total runtime:** ~5-10 minutes (depends on Kaggle download speed in Phase 4)

---

## For AI Agents (Claude Code / Other Agents)

### Purpose

This data enables AI agents in SNOP application to:

1. **Answer questions** - "What's current inventory of PARA500 at Plant North?"
2. **Detect patterns** - "Demand spikes every December (flu season)"
3. **Make recommendations** - "Order 500kg API-PARA from Supplier A (5-day lead time)"
4. **Warn proactively** - "Stockout risk in 3 days at Regional WH East"
5. **Explain reasoning** - "High trust (verified source), data age 2 hours"
6. **Learn from feedback** - "User rejected last recommendation, adjust model"
7. **Personalize** - "Supply chain manager prefers tabular format, demand planner prefers charts"

### API Integration Points

When building SNOP API endpoints, agents need access to:

**Read APIs (query data):**
- `GET /api/inventory/current` - Phase 5 data
- `GET /api/demand/historical` - Phase 4 data
- `GET /api/exceptions/active` - Phase 10 data
- `GET /api/goals/targets` - Phase 7 data
- `GET /api/users/{id}/preferences` - Phase 8 data

**Write APIs (create recommendations):**
- `POST /api/recommendations` - Writes to Phase 9 tables
- `POST /api/exceptions/{id}/acknowledge` - Updates Phase 10 status
- `POST /api/adjustments/manual` - Writes to Phase 6 provenance

**Agent Context APIs:**
- `GET /api/provenance/{entity}/{id}` - Phase 6 (trust scoring)
- `GET /api/feedback/{recommendation_id}` - Phase 9 (learning loop)

### Schema Access

All table schemas documented in:
- `docs/PHASE_DETAILS.md` - Full schema definitions per phase
- `docs/IMPLEMENTATION_GUIDE.md` - Business logic, validation rules

**Database:** PostgreSQL with SQLAlchemy models (UUID primary keys, auditable base pattern)

---

## Validation

Each phase includes validation script:

```bash
# Example: Validate Phase 1
python scripts/phase1/validate_phase1.py
```

**Checks:**
- Row counts match expected
- Foreign keys valid
- No NULL in required fields
- Business rules enforced (e.g., BOM quantities > 0)
- Data consistency (e.g., safety stock ≤ max stock)

**Output:**
```
✓ Phase 1 Master Data validated
  - regions: 4 rows
  - location_nodes: 18 rows
  - items: 11 rows
  - All foreign keys valid
  - No NULL violations
```

---

## Folder Structure

```
snop_data_generator/
├── README.md                      # This file
├── .env                           # Database credentials (create this)
├── .env.example                   # Template for .env
├── install_dependencies.sh        # Mac/Linux dependency installer
├── install_dependencies.bat       # Windows dependency installer
├── run_all_phases.sh              # Mac/Linux execution script
├── run_all_phases.bat             # Windows execution script
├── requirements.txt               # Python dependencies
├── docs/
│   ├── PHASE_DETAILS.md           # Deep-dive per phase (schemas, business logic)
│   ├── IMPLEMENTATION_GUIDE.md    # Implementation notes, rationale, decisions
│   └── KAGGLE_DATASET.md          # Info about historical data source
└── scripts/
    ├── phase1/                    # Master Data
    │   ├── generate_regions.py
    │   ├── generate_location_nodes.py
    │   ├── generate_items.py
    │   └── validate_phase1.py
    ├── phase2/                    # Relationships
    │   ├── generate_boms.py
    │   ├── generate_transportation_lanes.py
    │   ├── generate_plant_capacities.py
    │   └── validate_phase2.py
    ├── phase3/                    # Rules & Constraints
    │   ├── generate_inventory_rules.py
    │   ├── generate_validation_rules.py
    │   ├── generate_optimization_constraints.py
    │   └── validate_phase3.py
    ├── phase4/                    # Historical Data
    │   ├── download_kaggle_data.py
    │   ├── clean_kaggle_data.py
    │   ├── generate_historical_events.py
    │   ├── generate_demand_plans.py
    │   ├── generate_supply_plans.py
    │   ├── generate_inventory_movements.py
    │   └── validate_phase4.py
    ├── phase5/                    # Current State
    │   ├── generate_current_inventory.py
    │   └── validate_phase5.py
    ├── phase6/                    # Provenance
    │   ├── generate_inventory_provenance.py
    │   ├── generate_demand_provenance.py
    │   ├── generate_manual_adjustments.py
    │   └── validate_phase6.py
    ├── phase7/                    # Goals & Targets
    │   ├── generate_service_level_goals.py
    │   ├── generate_inventory_goals.py
    │   ├── generate_cost_goals.py
    │   ├── generate_operational_goals.py
    │   └── validate_phase7.py
    ├── phase8/                    # User Context
    │   ├── generate_users.py
    │   ├── generate_user_preferences.py
    │   ├── generate_interaction_history.py
    │   └── validate_phase8.py
    ├── phase9/                    # Outcomes & Feedback
    │   ├── generate_agent_recommendations.py
    │   ├── generate_recommendation_outcomes.py
    │   ├── generate_user_feedback.py
    │   └── validate_phase9.py
    └── phase10/                   # Exceptions & Alerts
        ├── generate_exception_rules.py
        ├── generate_active_exceptions.py
        ├── generate_exception_history.py
        └── validate_phase10.py
```

---

## Troubleshooting

### "Database connection failed"
- Check `.env` credentials
- Verify PostgreSQL running: `psql -U postgres -c "SELECT version();"`
- Test connection: `python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://user:pass@host/db'); print(engine.connect())"`

### "Kaggle API error" (Phase 4)
- Verify `~/.kaggle/kaggle.json` exists
- Check permissions: `ls -la ~/.kaggle/` (should be 600)
- Test: `kaggle datasets list`

### "Foreign key violation"
- Phases ran out of order
- Drop database, recreate, run `run_all_phases.sh` from start

### "Row count mismatch"
- Script interrupted mid-execution
- Drop affected tables, re-run that phase

---

## Contributing

When adding new phases or modifying data:

1. Update schemas in `docs/PHASE_DETAILS.md`
2. Add generation script to `scripts/phase{N}/`
3. Add validation script
4. Update `run_all_phases.sh` execution order
5. Update row counts in this README
6. Test full pipeline: `./run_all_phases.sh`

---

## License

Internal use only. Not for public distribution.

---

## Support

Questions? Contact the SNOP development team or refer to:
- `docs/PHASE_DETAILS.md` - Technical schemas
- `docs/IMPLEMENTATION_GUIDE.md` - Business logic
- `SNOP_DATA_GENERATION_PLAN.md` (root folder) - Original planning document
