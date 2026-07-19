# SNOP Data Generator - Implementation Guide

**For AI Agents & API Developers**

This document explains WHAT we implemented, WHY we chose these 10 phases, and HOW the generated data enables agentic AI in SNOP application.

---

## Executive Summary

**What:** 4,083 rows across 10 data pattern types  
**Why:** Enable AI agents to answer questions, detect patterns, recommend actions, warn proactively  
**How:** Production-grade mock data with real-world patterns (COVID spikes, flu seasons, supply disruptions)

---

## Why These 10 Phases?

### The 12 Data Pattern Framework

Agentic AI requires **12 distinct data pattern types** to function at human-level competence. Think of these as the "senses" an agent needs:

| # | Pattern Type | Agent Capability | Status |
|---|--------------|------------------|--------|
| 1 | Master Data | "What entities exist?" | ✅ Phase 1 |
| 2 | Historical Data | "What happened before?" | ✅ Phase 4 |
| 3 | Relationships | "How are things connected?" | ✅ Phase 2 |
| 4 | Rules & Constraints | "What's allowed/forbidden?" | ✅ Phase 3 |
| 5 | Provenance | "How trustworthy is this data?" | ✅ Phase 6 |
| 6 | Current State | "What's happening now?" | ✅ Phase 5 |
| 7 | Goals & Targets | "What should I optimize for?" | ✅ Phase 7 |
| 8 | User Context | "Who am I talking to?" | ✅ Phase 8 |
| 9 | Outcomes & Feedback | "Did my last suggestion work?" | ✅ Phase 9 |
| 10 | External/Reference | "What's happening outside our system?" | ⏸️ Deferred |
| 11 | Predictions/Forecasts | "What will happen next?" | ⏸️ Deferred |
| 12 | Exceptions & Alerts | "What needs attention NOW?" | ✅ Phase 10 |

### Why We Implemented 10, Not 12

**Implemented (10 types):**  
Core foundation for AI agent MVP. Without these, agents are **non-functional**:
- Can't answer basic questions (no master data)
- Can't detect patterns (no historical data)
- Can't learn (no feedback loop)
- Can't personalize (no user context)
- Can't warn proactively (no exceptions)

**Deferred (2 types):**  
Advanced features that **enhance** but don't **block** agent deployment:
- **External/Reference Data** (supplier catalogs, market indices) - Agent can recommend "order from Supplier A" without knowing Supplier A's phone number
- **Predictions/Forecasts** (ML model outputs) - Agent can use historical patterns for now; add ML later

**Decision Rationale:**  
Ship working agent MVP with 10 types → gather user feedback → add types 11-12 based on actual needs.

---

## Phase-by-Phase: What & Why

### Phase 1: Master Data (37 rows)

**What:**
- 4 Regions (NORTH, EAST, WEST, SOUTH)
- 18 Location nodes (plants, warehouses, subcontractors, distributors)
- 11 Items (3 finished goods + 8 raw materials)

**Why:**
Foundation for ALL other data. Every other phase references these IDs.

**Agent Use Case:**
```
User: "What's inventory at Plant North?"
Agent: [Queries location_nodes WHERE name LIKE '%Plant North%']
        [Finds ID: uuid-123]
        [Queries inventory WHERE location_id = uuid-123]
```

Without Phase 1: Agent can't resolve "Plant North" → query fails.

---

### Phase 2: Relationships (51 rows)

**What:**
- 9 BOMs (Bill of Materials: how to make finished goods from raw materials)
- 24 Transportation lanes (which locations can ship to which)
- 18 Plant capacities (how many units each plant can make per day)

**Why:**
Enables graph traversal. Agent needs to know:
- "To make PARA500, I need 0.0005kg API-PARA + 0.00015kg Starch"
- "To move goods from Plant North to Regional WH East, use Lane-007 (2 days transit)"
- "Plant North can make 50,000 units/day of PARA500"

**Agent Use Case:**
```
User: "Can Plant North fulfill 100k units of PARA500?"
Agent: [Checks plant_capacities: 50k/day capacity]
        [Answer: "Yes, but needs 2 days (100k ÷ 50k/day)"]
        
User: "What raw materials needed?"
Agent: [Queries BOMs for PARA500]
        [Answer: "50kg API-PARA, 15kg Starch, 20kg MCC"]
```

---

### Phase 3: Rules & Constraints (32 rows)

**What:**
- 9 Inventory rules (safety stock minimums)
- 15 Validation rules (data quality checks)
- 8 Optimization constraints (business limits)

**Why:**
Agent must respect business rules. Without this:
- Agent recommends 0 safety stock → stockouts happen
- Agent suggests invalid order quantity → system rejects
- Agent ignores cost constraints → CFO angry

**Agent Use Case:**
```
User: "What's minimum inventory for PARA500 at Regional WH?"
Agent: [Queries inventory_rules WHERE item = PARA500 AND type = FAST]
        [Answer: "15 days supply (FAST SKU rule)"]
        
User: "Can I reduce safety stock to 5 days?"
Agent: "No. Business rule RULE-001 requires 15 days for FAST SKUs."
```

---

### Phase 4: Historical Data (3,462 rows)

**What:**
- 6 Historical events (COVID-19, flu seasons, supply crisis, Russia-Ukraine war)
- 864 Demand plans (2020-2025, monthly data, 3 SKUs × 4 regions × 72 months)
- 648 Supply plans (production output)
- 1,944 Inventory movements (warehouse transfers)

**Why:**
Pattern detection. Agent learns:
- Demand spikes every December (flu season)
- COVID caused 200% spike in PARA500 demand
- Russia-Ukraine war disrupted supply April 2022

**Uses Real Data:** Kaggle "Global Pharmacy Sales 2020-2025" dataset (not synthetic)

**Agent Use Case:**
```
User: "Why is demand forecast high for December?"
Agent: [Queries historical_events WHERE period = December]
        [Finds: Flu Season events every December 2020-2024]
        [Queries demand_plans: avg +25% spike in Dec]
        [Answer: "Historical pattern: flu season drives 25% demand increase"]
```

---

### Phase 5: Current State (56 rows)

**What:**
- Current inventory snapshot (24 finished goods + 32 raw materials)
- Calculated from Phase 4 historical data + simulated recent movements

**Why:**
"What's happening NOW?" is the most common agent query.

**Agent Use Case:**
```
User: "Current inventory of PARA500?"
Agent: [Queries current_inventory WHERE item = PARA500]
        [Answer: "Plant North WH: 25,000 units
                  Regional WH North: 18,000 units
                  Regional WH East: 12,000 units
                  ..."]
```

---

### Phase 6: Provenance (148 rows)

**What:**
- Inventory provenance (who entered, when, trust level)
- Demand provenance (forecast source, verification method)
- Manual adjustments (audit trail for human edits)

**Why:**
Trust scoring. Agent needs to know:
- "This inventory count was manually entered 3 hours ago (trust: medium)"
- "This forecast came from ML model, verified by planner (trust: high)"
- "This adjustment was made by analyst John, overriding system (trust: low)"

**Agent Use Case:**
```
User: "How confident are you in this inventory number?"
Agent: [Queries inventory_provenance]
        [Finds: source = "system_count", trust_level = "high", last_verified = 2 hours ago]
        [Answer: "High confidence. System-counted 2 hours ago, auto-verified."]
```

---

### Phase 7: Goals & Targets (15 rows)

**What:**
- 4 Service level goals (95% on-time delivery)
- 5 Inventory goals (30 days max for SLOW SKUs)
- 3 Cost goals (production cost targets)
- 3 Operational goals (batch size, lead time)

**Why:**
Optimization direction. When agent makes recommendations, it needs to know:
- Minimize cost OR maximize service level?
- Prefer local production OR subcontractor?
- Target inventory: high (reduce stockouts) OR low (reduce holding cost)?

**Agent Use Case:**
```
User: "Should I increase safety stock?"
Agent: [Checks goals: service_level_target = 95%]
        [Checks current: service_level_actual = 92%]
        [Answer: "Yes. Current 92% < target 95%. Recommend +20% safety stock."]
```

---

### Phase 8: User Context (120 rows)

**What:**
- 20 Users (executives, plant managers, planners, analysts)
- 25 User preferences (chart vs table, metric units, notification settings)
- 75 Interaction history (what user asked before, when)

**Why:**
Personalization. Same question, different answers:
- **Supply chain manager** (wants high-level KPIs) vs **Analyst** (wants raw data table)
- **Demand planner** (cares about forecast accuracy) vs **Plant manager** (cares about production capacity)

**Agent Use Case:**
```
User: "Show me inventory status"

[User = Supply Chain Manager]
Agent: [Checks preferences: format = "executive_summary"]
        [Returns: "PARA500: 85% of target (GOOD), IBUP400: 60% (LOW), ..."]

[User = Warehouse Analyst]  
Agent: [Checks preferences: format = "detailed_table"]
        [Returns: CSV table with 56 rows, all SKUs × locations]
```

---

### Phase 9: Outcomes & Feedback (140 rows)

**What:**
- 50 Agent recommendations (past suggestions made by AI)
- 35 Recommendation outcomes (what happened after)
- 55 User feedback (thumbs up/down, comments)

**Why:**
Learning loop. Agent improves over time:
- Recommendation #42: "Order 500kg API-PARA" → User accepted → Outcome: Stockout prevented → Feedback: ✓ Helpful
- Recommendation #43: "Transfer goods via Lane-12" → User rejected → Feedback: "Lane-12 is slow, use Lane-8" → Agent learns: avoid Lane-12

**Agent Use Case:**
```
Agent generates recommendation: "Order from Supplier B (cheaper)"
[Checks feedback history: 3 past recommendations for Supplier B → 2 rejected]
[Rejection reasons: "Supplier B is slow", "Quality issues"]
[Agent adjusts: "Order from Supplier A (faster, higher quality) despite +10% cost"]
```

---

### Phase 10: Exceptions & Alerts (22 rows)

**What:**
- 9 Exception rules (when to trigger alerts)
- 8 Active exceptions (current alerts needing attention)
- 5 Exception history (resolved alerts)

**Why:**
**Proactive vs Reactive.** This is the difference between:
- **Reactive:** User asks "Is there a stockout?" → Agent checks → "Yes, stockout in 2 days"
- **Proactive:** Agent monitors background → Detects stockout risk → Alerts user BEFORE they ask

**Agent Use Case:**
```
[Background monitoring - no user query]

Agent: [Runs every 5 minutes]
        [Queries current_inventory JOIN inventory_rules]
        [Finds: Plant North - API-PARA: 80kg, consumption 40kg/day → 2 days left]
        [Checks exception_rules: RULE-001 triggers when stockout < 2 days]
        [Creates active_exception: severity = CRITICAL]
        [Sends alert: "⚠️ CRITICAL: API-PARA stockout in 2 days at Plant North"]
        
User sees alert in dashboard (not via chat query).
```

---

## How Agents Use This Data

### Query Patterns

**1. Simple Lookup**
```sql
-- "What's current inventory of PARA500?"
SELECT location_name, quantity_on_hand
FROM current_inventory ci
JOIN location_nodes ln ON ci.location_id = ln.id
WHERE item_code = 'PARA500';
```

**2. Pattern Detection**
```sql
-- "Does demand spike in December?"
SELECT 
    EXTRACT(MONTH FROM period_start) as month,
    AVG(quantity) as avg_demand
FROM demand_plans
WHERE item_code = 'PARA500'
GROUP BY EXTRACT(MONTH FROM period_start)
ORDER BY avg_demand DESC;
```

**3. Relationship Traversal**
```sql
-- "What raw materials needed to make 10,000 units PARA500?"
SELECT 
    i.name as material,
    b.quantity_per_unit * 10000 as total_needed_kg,
    ci.quantity_on_hand as current_stock
FROM boms b
JOIN items i ON b.child_item_id = i.id
LEFT JOIN current_inventory ci ON i.id = ci.item_id
WHERE b.parent_item_id = (SELECT id FROM items WHERE code = 'PARA500');
```

**4. Trust-Weighted Aggregation**
```sql
-- "Avg inventory (high-trust sources only)"
SELECT AVG(quantity)
FROM current_inventory ci
JOIN inventory_provenance ip ON ci.id = ip.inventory_id
WHERE ip.trust_level = 'high';
```

**5. Proactive Monitoring**
```sql
-- "Find all critical stockout risks"
SELECT 
    ln.name as location,
    i.code as item,
    ci.quantity_on_hand,
    ir.safety_stock_min,
    (ci.quantity_on_hand / ir.safety_stock_min) as days_remaining
FROM current_inventory ci
JOIN location_nodes ln ON ci.location_id = ln.id
JOIN items i ON ci.item_id = i.id
JOIN inventory_rules ir ON i.id = ir.item_id
WHERE (ci.quantity_on_hand / ir.safety_stock_min) < 2.0;
```

---

## What's NOT in This Data (Deferred Features)

### Phase 11: External/Reference Data

**What it would include:**
- Supplier catalog (15 suppliers with contact info, pricing, lead times)
- Holiday calendar (US holidays, flu season peaks)
- Regulatory updates (FDA rules, GMP requirements)
- Market data (API price indices, industry forecasts)

**Why deferred:**
- Agent can recommend actions without external context
- "Order more API-PARA" works even if agent doesn't know supplier phone numbers
- Can add later when integration with supplier systems is ready

**Impact:** Reduces agent sophistication, not functionality.

---

### Phase 12: Predictions/Forecasts (originally Phase 11)

**What it would include:**
- ML model outputs (demand forecast for next 6 months)
- Predictive alerts ("Stockout risk 85% in 2 weeks")
- What-if scenario results ("If we add 20% capacity, stockout risk drops to 12%")

**Why deferred:**
- Requires training ML models first (not just data generation)
- Agent can use historical patterns as proxy: "December demand was +25% last 3 years → likely +25% this year"
- More valuable after gathering real user queries (train model on actual usage patterns)

**Impact:** Agent uses simple heuristics instead of ML predictions. Good enough for MVP.

---

## Data Quality Standards

All generated data follows these production standards:

**1. UUID Primary Keys**
- Security: Non-guessable IDs
- Distribution: Globally unique (safe for multi-tenant future)
- Example: `550e8400-e29b-41d4-a716-446655440000`

**2. Auditable Base Pattern**
Every table has:
```python
created_at: datetime      # When row created
updated_at: datetime      # Last modification
created_by: str          # Who/what created it ("generate_regions.py")
is_active: bool          # Soft delete flag
version: int             # Optimistic locking
```

**3. Foreign Key Integrity**
- Every relationship enforced at DB level
- No orphan rows (e.g., BOM pointing to non-existent item)
- Validation scripts check before moving to next phase

**4. Business Rule Compliance**
- BOM quantities realistic (0.0005kg for 500mg tablet, not 500kg)
- Inventory non-negative
- Safety stock ≤ max stock
- Dates logical (effective_from < effective_to)

**5. Real-World Patterns**
- Historical data from Kaggle (not random noise)
- Event timing realistic (COVID peak March 2020, not July)
- Demand seasonality (flu season Dec-Feb, not summer)

---

## Using This Data for API Development

### Recommended API Endpoints

Based on agent query patterns, build these endpoints:

**Inventory:**
- `GET /api/inventory/current` → Phase 5 data
- `GET /api/inventory/history` → Phase 4 movements
- `GET /api/inventory/provenance/{id}` → Phase 6 trust data

**Demand/Supply:**
- `GET /api/demand/historical` → Phase 4 demand_plans
- `GET /api/supply/plans` → Phase 4 supply_plans
- `GET /api/events/historical` → Phase 4 historical_events

**Alerts:**
- `GET /api/exceptions/active` → Phase 10 active alerts
- `POST /api/exceptions/{id}/acknowledge` → Update Phase 10 status
- `GET /api/exceptions/rules` → Phase 10 detection rules

**Goals:**
- `GET /api/goals/targets` → Phase 7 all goals
- `GET /api/goals/performance` → Compare Phase 7 targets vs Phase 5 actuals

**User:**
- `GET /api/users/{id}/preferences` → Phase 8 personalization
- `POST /api/users/{id}/interactions` → Log to Phase 8 history

**Recommendations:**
- `POST /api/recommendations` → Agent writes to Phase 9
- `POST /api/recommendations/{id}/feedback` → User feedback to Phase 9
- `GET /api/recommendations/outcomes` → Phase 9 learning data

---

## Summary for AI Agents (Claude Code)

**When building SNOP APIs, remember:**

1. **10 phases = 10 data types** - Each type serves specific agent capability
2. **Dependency order matters** - Phase N depends on Phase N-1 IDs
3. **UUID primary keys** - Don't use integers, use UUIDs everywhere
4. **Provenance tracking** - Every data point has trust level, source, timestamp
5. **Proactive alerts** - Phase 10 enables background monitoring, not just Q&A
6. **Learning loop** - Phase 9 captures feedback for continuous improvement
7. **Personalization** - Phase 8 customizes responses per user role
8. **Real historical data** - Phase 4 uses Kaggle dataset, not synthetic

**This data is production-grade mock data.** It's realistic enough to:
- Train AI agents on real patterns
- Demo to customers without embarrassment
- Test APIs under realistic load (4,083 rows)
- Validate business logic before connecting real ERP

**It's NOT production data.** Don't use for:
- Real business decisions
- Compliance reporting
- Customer shipments

---

## Next Steps After Data Generation

1. **Verify data loaded:** `psql -d snop_db -c "SELECT COUNT(*) FROM regions;"`
2. **Build API endpoints** using schema from `PHASE_DETAILS.md`
3. **Connect AI agent** to APIs (not directly to DB)
4. **Test agent queries:**
   - "What's current inventory?"
   - "Why does demand spike in December?"
   - "Any critical alerts?"
5. **Gather feedback** → Update Phase 9 outcomes table
6. **Iterate** → Add Phases 11-12 when needed

---

**Generated:** 2026-07-20  
**Total Rows:** 4,083  
**Phases:** 10 of 12 (83% complete)  
**Production-Ready:** Yes (for mock data)
