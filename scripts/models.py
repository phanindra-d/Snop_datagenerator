"""
Shared SQLAlchemy models for all SNOP data generation scripts
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Numeric, Text, Date, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

Base = declarative_base()

# Enums
class LocationType(str, enum.Enum):
    PLANT = "PLANT"
    WAREHOUSE_PLANT = "WAREHOUSE_PLANT"
    WAREHOUSE_REGIONAL = "WAREHOUSE_REGIONAL"
    DISTRIBUTOR = "DISTRIBUTOR"
    SUBCONTRACTOR = "SUBCONTRACTOR"

class ItemType(str, enum.Enum):
    FINISHED_GOOD = "FINISHED_GOOD"
    RAW_MATERIAL = "RAW_MATERIAL"
    SEMI_FINISHED = "SEMI_FINISHED"
    EXCIPIENT = "EXCIPIENT"

class SKUCategory(str, enum.Enum):
    FAST = "FAST"
    SLOW = "SLOW"

class RuleType(str, enum.Enum):
    SAFETY_STOCK = "SAFETY_STOCK"
    MAX_STOCK = "MAX_STOCK"
    REORDER_POINT = "REORDER_POINT"

class ValidationType(str, enum.Enum):
    RANGE_CHECK = "RANGE_CHECK"
    MANDATORY_FIELD = "MANDATORY_FIELD"
    RELATIONSHIP_CHECK = "RELATIONSHIP_CHECK"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"

class ConstraintType(str, enum.Enum):
    CAPACITY = "CAPACITY"
    BUDGET = "BUDGET"
    SERVICE_LEVEL = "SERVICE_LEVEL"
    LEAD_TIME = "LEAD_TIME"

class EventType(str, enum.Enum):
    PANDEMIC = "PANDEMIC"
    SEASONAL = "SEASONAL"
    SUPPLY_DISRUPTION = "SUPPLY_DISRUPTION"
    GEOPOLITICAL = "GEOPOLITICAL"
    REGULATORY = "REGULATORY"

class BucketType(str, enum.Enum):
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    DAILY = "DAILY"

class PlanType(str, enum.Enum):
    HISTORICAL = "HISTORICAL"
    FORECAST = "FORECAST"

class MovementType(str, enum.Enum):
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    PRODUCTION = "PRODUCTION"
    CONSUMPTION = "CONSUMPTION"
    ADJUSTMENT = "ADJUSTMENT"

class TrustLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class VerificationMethod(str, enum.Enum):
    SYSTEM_COUNT = "system_count"
    MANUAL_COUNT = "manual_count"
    ESTIMATED = "estimated"
    DERIVED = "derived"

class ForecastMethod(str, enum.Enum):
    ML_MODEL = "ml_model"
    STATISTICAL = "statistical"
    MANUAL = "manual"
    HYBRID = "hybrid"

class UserRole(str, enum.Enum):
    EXECUTIVE = "EXECUTIVE"
    PLANT_MANAGER = "PLANT_MANAGER"
    SC_MANAGER = "SC_MANAGER"
    DEMAND_PLANNER = "DEMAND_PLANNER"
    WH_MANAGER = "WH_MANAGER"
    ANALYST = "ANALYST"

class OutcomeStatus(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PARTIALLY_ACCEPTED = "PARTIALLY_ACCEPTED"
    PENDING = "PENDING"

class FeedbackSentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class ExceptionType(str, enum.Enum):
    STOCKOUT_RISK = "STOCKOUT_RISK"
    EXCESS_INVENTORY = "EXCESS_INVENTORY"
    SAFETY_STOCK_BREACH = "SAFETY_STOCK_BREACH"
    QUALITY_DEVIATION = "QUALITY_DEVIATION"
    DEMAND_SPIKE = "DEMAND_SPIKE"
    DEMAND_DROP = "DEMAND_DROP"
    LATE_DELIVERY = "LATE_DELIVERY"
    COMPLIANCE_DEADLINE = "COMPLIANCE_DEADLINE"

class SeverityLevel(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ExceptionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

# Models - Phase 1
class Region(Base):
    __tablename__ = "regions"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class LocationNode(Base):
    __tablename__ = "location_nodes"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    type = Column(SQLEnum(LocationType), nullable=False)
    region_id = Column(PG_UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class Item(Base):
    __tablename__ = "items"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(SQLEnum(ItemType), nullable=False)
    volume_category = Column(SQLEnum(SKUCategory))
    unit_of_measure = Column(String(20), nullable=False)
    default_supplier_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

# Phase 2
class BOM(Base):
    __tablename__ = "boms"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    child_item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    quantity_per_unit = Column(Numeric(12, 6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    __table_args__ = (UniqueConstraint('parent_item_id', 'child_item_id', name='uq_bom_parent_child'),)

class TransportationLane(Base):
    __tablename__ = "transportation_lanes"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"), nullable=False)
    to_location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"), nullable=False)
    transit_time_days = Column(Numeric(4, 1), nullable=False)
    cost_per_unit = Column(Numeric(10, 2))
    mode = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    __table_args__ = (
        UniqueConstraint('from_location_id', 'to_location_id', name='uq_lane_from_to'),
        CheckConstraint('from_location_id != to_location_id', name='chk_no_self_loop')
    )

class PlantCapacity(Base):
    __tablename__ = "plant_capacities"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"), nullable=False)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    capacity_per_day = Column(Integer, nullable=False)
    is_owned = Column(Boolean, default=True)
    outsourcing_premium = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    __table_args__ = (UniqueConstraint('location_id', 'item_id', name='uq_plant_item_capacity'),)

# Phase 3
class InventoryRule(Base):
    __tablename__ = "inventory_rules"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code = Column(String(50), unique=True, nullable=False)
    rule_type = Column(SQLEnum(RuleType), nullable=False)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"))
    location_type = Column(SQLEnum(LocationType))
    min_days_supply = Column(Integer)
    max_days_supply = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class ValidationRule(Base):
    __tablename__ = "validation_rules"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code = Column(String(50), unique=True, nullable=False)
    rule_name = Column(String(200), nullable=False)
    validation_type = Column(SQLEnum(ValidationType), nullable=False)
    target_table = Column(String(100))
    condition_sql = Column(Text)
    error_message = Column(Text)
    severity = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class OptimizationConstraint(Base):
    __tablename__ = "optimization_constraints"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    constraint_code = Column(String(50), unique=True, nullable=False)
    constraint_name = Column(String(200), nullable=False)
    constraint_type = Column(SQLEnum(ConstraintType), nullable=False)
    min_value = Column(Numeric(15, 2))
    max_value = Column(Numeric(15, 2))
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

# Phase 4
class HistoricalEvent(Base):
    __tablename__ = "historical_events"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_code = Column(String(50), unique=True, nullable=False)
    event_name = Column(String(200), nullable=False)
    event_type = Column(SQLEnum(EventType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    affected_items = Column(Text)
    affected_regions = Column(Text)
    impact_description = Column(Text)
    demand_impact_multiplier = Column(Numeric(5, 2))
    supply_impact_multiplier = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class DemandPlan(Base):
    __tablename__ = "demand_plans"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    bucket_type = Column(SQLEnum(BucketType), nullable=False)
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    quantity = Column(Integer, nullable=False)
    scenario_id = Column(PG_UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class SupplyPlan(Base):
    __tablename__ = "supply_plans"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    bucket_type = Column(SQLEnum(BucketType), nullable=False)
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    quantity = Column(Integer, nullable=False)
    scenario_id = Column(PG_UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"), nullable=False)
    movement_type = Column(SQLEnum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    movement_date = Column(Date, nullable=False)
    reference_id = Column(PG_UUID(as_uuid=True))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

# Phase 5
class CurrentInventory(Base):
    __tablename__ = "current_inventory"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"), nullable=False)
    quantity_on_hand = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    __table_args__ = (UniqueConstraint('item_id', 'location_id', name='uq_inventory_item_location'),)

# Phase 6
class InventoryProvenance(Base):
    __tablename__ = "inventory_provenance"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(PG_UUID(as_uuid=True), ForeignKey("current_inventory.id"), nullable=False)
    data_source = Column(String(200))
    trust_level = Column(SQLEnum(TrustLevel), nullable=False)
    verification_method = Column(SQLEnum(VerificationMethod), nullable=False)
    last_verified_at = Column(DateTime)
    verified_by = Column(String(200))
    data_age_hours = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class DemandProvenance(Base):
    __tablename__ = "demand_provenance"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demand_plan_id = Column(PG_UUID(as_uuid=True), ForeignKey("demand_plans.id"), nullable=False)
    forecast_method = Column(SQLEnum(ForecastMethod), nullable=False)
    trust_level = Column(SQLEnum(TrustLevel), nullable=False)
    model_accuracy_pct = Column(Numeric(5, 2))
    overridden_by_planner = Column(Boolean, default=False)
    override_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class ManualAdjustment(Base):
    __tablename__ = "manual_adjustments"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_table = Column(String(100), nullable=False)
    target_id = Column(PG_UUID(as_uuid=True), nullable=False)
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    adjustment_reason = Column(Text)
    adjusted_by = Column(String(200), nullable=False)
    adjustment_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

# Phase 7
class ServiceLevelGoal(Base):
    __tablename__ = "service_level_goals"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_code = Column(String(50), unique=True, nullable=False)
    goal_name = Column(String(200), nullable=False)
    target_pct = Column(Numeric(5, 2), nullable=False)
    scope = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class InventoryGoal(Base):
    __tablename__ = "inventory_goals"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_code = Column(String(50), unique=True, nullable=False)
    goal_name = Column(String(200), nullable=False)
    target_days_supply = Column(Integer)
    applies_to_category = Column(SQLEnum(SKUCategory))
    applies_to_location_type = Column(SQLEnum(LocationType))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class CostGoal(Base):
    __tablename__ = "cost_goals"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_code = Column(String(50), unique=True, nullable=False)
    goal_name = Column(String(200), nullable=False)
    target_value = Column(Numeric(15, 2), nullable=False)
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class OperationalGoal(Base):
    __tablename__ = "operational_goals"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_code = Column(String(50), unique=True, nullable=False)
    goal_name = Column(String(200), nullable=False)
    target_value = Column(Numeric(15, 2), nullable=False)
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

# Phase 8
class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(200), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    region_id = Column(PG_UUID(as_uuid=True), ForeignKey("regions.id"))
    location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    __table_args__ = (UniqueConstraint('user_id', 'preference_key', name='uq_user_pref_key'),)

class InteractionHistory(Base):
    __tablename__ = "interaction_history"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String(50))
    interaction_content = Column(Text)
    response_content = Column(Text)
    interaction_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

# Phase 9
class AgentRecommendation(Base):
    __tablename__ = "agent_recommendations"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_code = Column(String(50), unique=True, nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recommendation_type = Column(String(100))
    recommendation_text = Column(Text, nullable=False)
    confidence_score = Column(Numeric(5, 2))
    generated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class RecommendationOutcome(Base):
    __tablename__ = "recommendation_outcomes"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(PG_UUID(as_uuid=True), ForeignKey("agent_recommendations.id"), nullable=False)
    outcome_status = Column(SQLEnum(OutcomeStatus), nullable=False)
    action_taken = Column(Text)
    actual_result = Column(Text)
    outcome_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(PG_UUID(as_uuid=True), ForeignKey("agent_recommendations.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sentiment = Column(SQLEnum(FeedbackSentiment), nullable=False)
    rating = Column(Integer)
    comment = Column(Text)
    feedback_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    __table_args__ = (CheckConstraint('rating BETWEEN 1 AND 5', name='chk_rating_range'),)

# Phase 10
class ExceptionRule(Base):
    __tablename__ = "exception_rules"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code = Column(String(50), unique=True, nullable=False)
    rule_name = Column(String(200), nullable=False)
    exception_type = Column(SQLEnum(ExceptionType), nullable=False)
    severity = Column(SQLEnum(SeverityLevel), nullable=False)
    applies_to_item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"))
    applies_to_location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"))
    threshold_value = Column(Numeric(15, 2))
    threshold_unit = Column(String(50))
    condition_sql = Column(Text)
    notify_users = Column(Text)
    auto_escalate_hours = Column(Integer)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class ActiveException(Base):
    __tablename__ = "active_exceptions"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exception_rule_id = Column(PG_UUID(as_uuid=True), ForeignKey("exception_rules.id"), nullable=False)
    exception_type = Column(SQLEnum(ExceptionType), nullable=False)
    severity = Column(SQLEnum(SeverityLevel), nullable=False)
    status = Column(SQLEnum(ExceptionStatus), default=ExceptionStatus.ACTIVE)
    affected_item_id = Column(PG_UUID(as_uuid=True), ForeignKey("items.id"))
    affected_location_id = Column(PG_UUID(as_uuid=True), ForeignKey("location_nodes.id"))
    affected_period = Column(Date)
    detected_at = Column(DateTime, nullable=False)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    current_value = Column(Numeric(15, 2))
    threshold_value = Column(Numeric(15, 2))
    deviation_pct = Column(Numeric(5, 2))
    alert_title = Column(String(200), nullable=False)
    alert_message = Column(Text, nullable=False)
    recommended_actions = Column(Text)
    assigned_to_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

class ExceptionHistory(Base):
    __tablename__ = "exception_history"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    active_exception_id = Column(PG_UUID(as_uuid=True), nullable=False)
    exception_type = Column(SQLEnum(ExceptionType), nullable=False)
    severity = Column(SQLEnum(SeverityLevel), nullable=False)
    status = Column(SQLEnum(ExceptionStatus), nullable=False)
    affected_item_code = Column(String(50))
    affected_location_name = Column(String(200))
    detected_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime)
    duration_hours = Column(Integer)
    alert_message = Column(Text, nullable=False)
    resolution_action = Column(Text)
    resolved_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(200))
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
