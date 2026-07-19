#!/bin/bash
# SNOP Data Generator - Execute All Phases in Dependency Order

set -e  # Exit on first error

echo "========================================="
echo "SNOP Data Generator - Generating 4,083 Rows"
echo "========================================="
echo ""

# Check .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found"
    echo "Copy .env.example to .env and configure database credentials"
    exit 1
fi

# Timer
START_TIME=$(date +%s)

# Phase 1: Master Data (37 rows)
echo "========================================="
echo "PHASE 1: Master Data (37 rows)"
echo "========================================="
echo ""
python3 scripts/phase1/generate_regions.py
python3 scripts/phase1/generate_location_nodes.py
python3 scripts/phase1/generate_items.py
python3 scripts/phase1/validate_phase1.py
echo "✓ Phase 1 complete"
echo ""

# Phase 2: Relationships (51 rows)
echo "========================================="
echo "PHASE 2: Relationships (51 rows)"
echo "========================================="
echo ""
python3 scripts/phase2/generate_boms.py
python3 scripts/phase2/generate_transportation_lanes.py
python3 scripts/phase2/generate_plant_capacities.py
python3 scripts/phase2/validate_phase2.py
echo "✓ Phase 2 complete"
echo ""

# Phase 3: Rules & Constraints (32 rows)
echo "========================================="
echo "PHASE 3: Rules & Constraints (32 rows)"
echo "========================================="
echo ""
python3 scripts/phase3/generate_inventory_rules.py
python3 scripts/phase3/generate_validation_rules.py
python3 scripts/phase3/generate_optimization_constraints.py
python3 scripts/phase3/validate_phase3.py
echo "✓ Phase 3 complete"
echo ""

# Phase 4: Historical Data (3,462 rows) - LONGEST PHASE
echo "========================================="
echo "PHASE 4: Historical Data (3,462 rows)"
echo "⚠️  This phase downloads ~50MB from Kaggle (may take 2-5 min)"
echo "========================================="
echo ""
python3 scripts/phase4/download_kaggle_data.py
python3 scripts/phase4/clean_kaggle_data.py
python3 scripts/phase4/generate_historical_events.py
python3 scripts/phase4/generate_demand_plans.py
python3 scripts/phase4/generate_supply_plans.py
python3 scripts/phase4/generate_inventory_movements.py
python3 scripts/phase4/validate_phase4.py
echo "✓ Phase 4 complete"
echo ""

# Phase 5: Current State (56 rows)
echo "========================================="
echo "PHASE 5: Current State (56 rows)"
echo "========================================="
echo ""
python3 scripts/phase5/generate_current_inventory.py
python3 scripts/phase5/validate_phase5.py
echo "✓ Phase 5 complete"
echo ""

# Phase 6: Provenance (148 rows)
echo "========================================="
echo "PHASE 6: Provenance (148 rows)"
echo "========================================="
echo ""
python3 scripts/phase6/generate_inventory_provenance.py
python3 scripts/phase6/generate_demand_provenance.py
python3 scripts/phase6/generate_manual_adjustments.py
python3 scripts/phase6/validate_phase6.py
echo "✓ Phase 6 complete"
echo ""

# Phase 7: Goals & Targets (15 rows)
echo "========================================="
echo "PHASE 7: Goals & Targets (15 rows)"
echo "========================================="
echo ""
python3 scripts/phase7/generate_service_level_goals.py
python3 scripts/phase7/generate_inventory_goals.py
python3 scripts/phase7/generate_cost_goals.py
python3 scripts/phase7/generate_operational_goals.py
python3 scripts/phase7/validate_phase7.py
echo "✓ Phase 7 complete"
echo ""

# Phase 8: User Context (120 rows)
echo "========================================="
echo "PHASE 8: User Context (120 rows)"
echo "========================================="
echo ""
python3 scripts/phase8/generate_users.py
python3 scripts/phase8/generate_user_preferences.py
python3 scripts/phase8/generate_interaction_history.py
python3 scripts/phase8/validate_phase8.py
echo "✓ Phase 8 complete"
echo ""

# Phase 9: Outcomes & Feedback (140 rows)
echo "========================================="
echo "PHASE 9: Outcomes & Feedback (140 rows)"
echo "========================================="
echo ""
python3 scripts/phase9/generate_agent_recommendations.py
python3 scripts/phase9/generate_recommendation_outcomes.py
python3 scripts/phase9/generate_user_feedback.py
python3 scripts/phase9/validate_phase9.py
echo "✓ Phase 9 complete"
echo ""

# Phase 10: Exceptions & Alerts (22 rows)
echo "========================================="
echo "PHASE 10: Exceptions & Alerts (22 rows)"
echo "========================================="
echo ""
python3 scripts/phase10/generate_exception_rules.py
python3 scripts/phase10/generate_active_exceptions.py
python3 scripts/phase10/generate_exception_history.py
python3 scripts/phase10/validate_phase10.py
echo "✓ Phase 10 complete"
echo ""

# Summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo "========================================="
echo "✓ ALL PHASES COMPLETE"
echo "========================================="
echo ""
echo "Generated: 4,083 rows across 10 phases"
echo "Time: ${MINUTES}m ${SECONDS}s"
echo ""
echo "Next steps:"
echo "  - Verify data: psql -d snop_db -c 'SELECT COUNT(*) FROM regions;'"
echo "  - Start SNOP API server"
echo "  - Test AI agent queries"
echo ""
