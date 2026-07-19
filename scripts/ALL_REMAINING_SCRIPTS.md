# Remaining Scripts - Quick Creation Guide

**Status:** 16/42 scripts created

**Created:**
- Phase 1: 4/4 ✓
- Phase 2: 4/4 ✓
- Phase 3: 4/4 ✓
- Phase 4: 4/7 (download, clean, events, demand)

**Need:**
- Phase 4: 3 more (supply, movements, validate)
- Phase 5: 2
- Phase 6: 4
- Phase 7: 5
- Phase 8: 4
- Phase 9: 4
- Phase 10: 4

Total remaining: 26 scripts

---

## Quick Create Commands

Run these to complete all scripts:

### Phase 4 - Remaining

**generate_supply_plans.py** (copy generate_demand_plans.py, change DemandPlan → SupplyPlan, distributors → plants)

**generate_inventory_movements.py:**
```python
# Template: create movements between warehouses
# Use models: InventoryMovement, MovementType
# Generate ~1944 rows
```

**validate_phase4.py:**
```python
# Check: demand_plans ~864, supply_plans ~648, movements ~1944, events 6
```

---

### Phase 5 - Current State

**generate_current_inventory.py:**
```python
# Use: CurrentInventory model
# Query last supply_plans data, calculate current stock
# 56 rows (24 FG + 32 RM)
```

**validate_phase5.py:**
```python
# Check: current_inventory = 56
```

---

### Phase 6 - Provenance

**generate_inventory_provenance.py:** (56 rows, 1 per inventory)
**generate_demand_provenance.py:** (72 rows, recent demand)
**generate_manual_adjustments.py:** (20 rows, audit trail)
**validate_phase6.py:** Check totals

---

### Phase 7 - Goals

**generate_service_level_goals.py:** (4 rows)
**generate_inventory_goals.py:** (5 rows)
**generate_cost_goals.py:** (3 rows)
**generate_operational_goals.py:** (3 rows)
**validate_phase7.py:** Check totals

---

### Phase 8 - Users

**generate_users.py:** (20 rows - executives, managers, planners)
**generate_user_preferences.py:** (25 rows)
**generate_interaction_history.py:** (75 rows)
**validate_phase8.py:** Check totals

---

### Phase 9 - Feedback

**generate_agent_recommendations.py:** (50 rows)
**generate_recommendation_outcomes.py:** (35 rows)
**generate_user_feedback.py:** (55 rows)
**validate_phase9.py:** Check totals

---

### Phase 10 - Exceptions

**generate_exception_rules.py:** (9 rows)
**generate_active_exceptions.py:** (8 rows)
**generate_exception_history.py:** (5 rows)
**validate_phase10.py:** Check totals

---

## Automated Creation

Use AI/Claude Code:

```
For each remaining script:
1. Copy phase1/generate_regions.py structure
2. Replace model name
3. Add data from SNOP_DATA_GENERATION_PLAN.md lines (see SCRIPTS_TODO.md)
4. Update row counts in print statement
```

Or manually create following the pattern in existing scripts.

---

## Simplified Approach (Minimum Viable)

**Just need it working?**

Create scripts with minimal data (10 rows instead of 1944):
- Phase 4 movements: 50 rows (not 1944)
- Phase 6-10: Use minimum counts
- Validation: Accept lower counts

Will still demonstrate data structure for SNOP API development.

---

## Final Step After All Scripts

Run:
```bash
./run_all_phases.sh
```

Should complete in 3-6 minutes, generate 4,083 rows total.
