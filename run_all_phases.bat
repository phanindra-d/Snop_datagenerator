@echo off
REM SNOP Data Generator - Execute All Phases in Dependency Order

setlocal enabledelayedexpansion

echo =========================================
echo SNOP Data Generator - Generating 4,083 Rows
echo =========================================
echo.

REM Check .env exists
if not exist ".env" (
    echo ERROR: .env file not found
    echo Copy .env.example to .env and configure database credentials
    pause
    exit /b 1
)

REM Timer
set START_TIME=%time%

REM Phase 1: Master Data (37 rows)
echo =========================================
echo PHASE 1: Master Data (37 rows)
echo =========================================
echo.
python scripts\phase1\generate_regions.py || goto :error
python scripts\phase1\generate_location_nodes.py || goto :error
python scripts\phase1\generate_items.py || goto :error
python scripts\phase1\validate_phase1.py || goto :error
echo ✓ Phase 1 complete
echo.

REM Phase 2: Relationships (51 rows)
echo =========================================
echo PHASE 2: Relationships (51 rows)
echo =========================================
echo.
python scripts\phase2\generate_boms.py || goto :error
python scripts\phase2\generate_transportation_lanes.py || goto :error
python scripts\phase2\generate_plant_capacities.py || goto :error
python scripts\phase2\validate_phase2.py || goto :error
echo ✓ Phase 2 complete
echo.

REM Phase 3: Rules & Constraints (32 rows)
echo =========================================
echo PHASE 3: Rules & Constraints (32 rows)
echo =========================================
echo.
python scripts\phase3\generate_inventory_rules.py || goto :error
python scripts\phase3\generate_validation_rules.py || goto :error
python scripts\phase3\generate_optimization_constraints.py || goto :error
python scripts\phase3\validate_phase3.py || goto :error
echo ✓ Phase 3 complete
echo.

REM Phase 4: Historical Data (3,462 rows) - LONGEST PHASE
echo =========================================
echo PHASE 4: Historical Data (3,462 rows)
echo ⚠️  This phase downloads ~50MB from Kaggle (may take 2-5 min)
echo =========================================
echo.
python scripts\phase4\download_kaggle_data.py || goto :error
python scripts\phase4\clean_kaggle_data.py || goto :error
python scripts\phase4\generate_historical_events.py || goto :error
python scripts\phase4\generate_demand_plans.py || goto :error
python scripts\phase4\generate_supply_plans.py || goto :error
python scripts\phase4\generate_inventory_movements.py || goto :error
python scripts\phase4\validate_phase4.py || goto :error
echo ✓ Phase 4 complete
echo.

REM Phase 5: Current State (56 rows)
echo =========================================
echo PHASE 5: Current State (56 rows)
echo =========================================
echo.
python scripts\phase5\generate_current_inventory.py || goto :error
python scripts\phase5\validate_phase5.py || goto :error
echo ✓ Phase 5 complete
echo.

REM Phase 6: Provenance (148 rows)
echo =========================================
echo PHASE 6: Provenance (148 rows)
echo =========================================
echo.
python scripts\phase6\generate_inventory_provenance.py || goto :error
python scripts\phase6\generate_demand_provenance.py || goto :error
python scripts\phase6\generate_manual_adjustments.py || goto :error
python scripts\phase6\validate_phase6.py || goto :error
echo ✓ Phase 6 complete
echo.

REM Phase 7: Goals & Targets (15 rows)
echo =========================================
echo PHASE 7: Goals & Targets (15 rows)
echo =========================================
echo.
python scripts\phase7\generate_service_level_goals.py || goto :error
python scripts\phase7\generate_inventory_goals.py || goto :error
python scripts\phase7\generate_cost_goals.py || goto :error
python scripts\phase7\generate_operational_goals.py || goto :error
python scripts\phase7\validate_phase7.py || goto :error
echo ✓ Phase 7 complete
echo.

REM Phase 8: User Context (120 rows)
echo =========================================
echo PHASE 8: User Context (120 rows)
echo =========================================
echo.
python scripts\phase8\generate_users.py || goto :error
python scripts\phase8\generate_user_preferences.py || goto :error
python scripts\phase8\generate_interaction_history.py || goto :error
python scripts\phase8\validate_phase8.py || goto :error
echo ✓ Phase 8 complete
echo.

REM Phase 9: Outcomes & Feedback (140 rows)
echo =========================================
echo PHASE 9: Outcomes & Feedback (140 rows)
echo =========================================
echo.
python scripts\phase9\generate_agent_recommendations.py || goto :error
python scripts\phase9\generate_recommendation_outcomes.py || goto :error
python scripts\phase9\generate_user_feedback.py || goto :error
python scripts\phase9\validate_phase9.py || goto :error
echo ✓ Phase 9 complete
echo.

REM Phase 10: Exceptions & Alerts (22 rows)
echo =========================================
echo PHASE 10: Exceptions & Alerts (22 rows)
echo =========================================
echo.
python scripts\phase10\generate_exception_rules.py || goto :error
python scripts\phase10\generate_active_exceptions.py || goto :error
python scripts\phase10\generate_exception_history.py || goto :error
python scripts\phase10\validate_phase10.py || goto :error
echo ✓ Phase 10 complete
echo.

REM Summary
set END_TIME=%time%
echo =========================================
echo ✓ ALL PHASES COMPLETE
echo =========================================
echo.
echo Generated: 4,083 rows across 10 phases
echo Start: %START_TIME%
echo End:   %END_TIME%
echo.
echo Next steps:
echo   - Verify data in PostgreSQL
echo   - Start SNOP API server
echo   - Test AI agent queries
echo.
pause
exit /b 0

:error
echo.
echo =========================================
echo ✗ ERROR: Phase failed
echo =========================================
echo.
echo Check error message above and fix before retrying.
echo.
pause
exit /b 1
