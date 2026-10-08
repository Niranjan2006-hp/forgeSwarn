import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_id():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="engineer")
    created_at = Column(DateTime, default=utc_now)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    name = Column(String(255), nullable=False)
    raw_requirement = Column(Text, nullable=False)
    domain = Column(String(100), default="General")
    application_type = Column(String(100), default="Web Application")
    tech_preference = Column(String(100), default="FastAPI + React")
    deployment_target = Column(String(100), default="Docker / Local")
    autonomy_level = Column(String(50), default="HIGH")  # LOW, MEDIUM, HIGH
    status = Column(String(50), default="CREATED", index=True)
    # CREATED, ANALYZING, CONTRACT_GENERATED, TEAM_FORMED, ARCHITECTING, DEVELOPING,
    # INTEGRATING, TESTING, FAILURE_DETECTED, DIAGNOSING, REPAIRING, REGRESSION_TESTING,
    # SECURITY_REVIEW, STAGING, DEPLOYING, COMPLETED, FAILED, ROLLED_BACK
    
    is_demo_mode = Column(Boolean, default=True)
    llm_provider = Column(String(50), default="mock")
    
    # Risk and approval
    risk_level = Column(String(50), default="LOW")
    approval_required = Column(Boolean, default=False)
    approved_by_user = Column(Boolean, default=False)
    
    # Deployment result
    app_url = Column(String(255), nullable=True)
    app_port = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    # Relationships
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    contract = relationship("EngineeringContract", back_populates="project", uselist=False, cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="project", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="project", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="project", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    bugs = relationship("Bug", back_populates="project", cascade="all, delete-orphan")
    repairs = relationship("RepairAttempt", back_populates="project", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="project", cascade="all, delete-orphan")
    events = relationship("ProjectEvent", back_populates="project", cascade="all, delete-orphan")

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    req_type = Column(String(50), default="FUNCTIONAL")  # FUNCTIONAL, BUSINESS_RULE, SECURITY, NON_FUNCTIONAL
    code = Column(String(50), nullable=False)  # FR-001, BR-001, SEC-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), default="HIGH")
    status = Column(String(50), default="PENDING")  # PENDING, IMPLEMENTED, VERIFIED, FAILED
    
    project = relationship("Project", back_populates="requirements")

class EngineeringContract(Base):
    __tablename__ = "engineering_contracts"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, unique=True)
    content_json = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    status = Column(String(50), default="DRAFT")  # DRAFT, APPROVED, LOCKED
    created_at = Column(DateTime, default=utc_now)
    
    project = relationship("Project", back_populates="contract")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False)  # architect, backend, frontend, database, tester, debugger, etc.
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    status = Column(String(50), default="IDLE")  # IDLE, WORKING, COMPLETED, FAILED
    selection_reason = Column(Text, nullable=True)
    capabilities = Column(JSON, default=list)  # list of strings
    tools = Column(JSON, default=list)
    restrictions = Column(JSON, default=list)
    workload = Column(Integer, default=0)
    confidence = Column(Float, default=0.95)
    avatar_color = Column(String(50), default="#06B6D4")
    
    project = relationship("Project", back_populates="agents")
    tasks = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")
    messages = relationship("AgentMessage", back_populates="agent", cascade="all, delete-orphan")

class AgentTask(Base):
    __tablename__ = "agent_tasks"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    risk_level = Column(String(50), default="LOW")
    result_summary = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    agent = relationship("Agent", back_populates="tasks")

class AgentMessage(Base):
    __tablename__ = "agent_messages"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True)
    sender_name = Column(String(100), nullable=False)
    recipient = Column(String(100), default="ALL")
    content = Column(Text, nullable=False)
    category = Column(String(50), default="STATUS")  # STATUS, ARCHITECTURE, PROPOSAL, WARNING, ERROR, CONSENSUS
    created_at = Column(DateTime, default=utc_now)
    
    agent = relationship("Agent", back_populates="messages")

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)  # e.g., requirements.json, architecture.md
    file_type = Column(String(50), default="json")
    content = Column(Text, nullable=False)
    created_by = Column(String(100), default="Orchestrator")
    version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    project = relationship("Project", back_populates="artifacts")

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    decision = Column(String(255), nullable=False)
    alternatives = Column(JSON, default=list)
    reason = Column(Text, nullable=False)
    participating_agents = Column(JSON, default=list)
    confidence = Column(Float, default=0.95)
    affected_components = Column(JSON, default=list)
    timestamp = Column(DateTime, default=utc_now)
    
    project = relationship("Project", back_populates="decisions")

class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    test_id = Column(String(50), nullable=False)  # e.g. TC-FR-001, TC-BR-001
    requirement_id = Column(String(50), nullable=True)  # link to FR-001 / BR-001
    category = Column(String(50), default="FUNCTIONAL")  # FUNCTIONAL, API, CONCURRENCY, SECURITY, REGRESSION
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    expected_outcome = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, PASSED, FAILED
    execution_time_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    project = relationship("Project", back_populates="test_cases")

class Bug(Base):
    __tablename__ = "bugs"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    test_id = Column(String(50), nullable=True)
    requirement_id = Column(String(50), nullable=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(50), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), default="OPEN")  # OPEN, DIAGNOSED, REPAIRING, REPAIRED, CLOSED
    root_cause = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    affected_component = Column(String(255), nullable=True)
    recommended_fix = Column(Text, nullable=True)
    diagnosed_by = Column(String(100), default="Debugger Agent")
    detected_at = Column(DateTime, default=utc_now)
    resolved_at = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="bugs")

class RepairAttempt(Base):
    __tablename__ = "repair_attempts"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    bug_id = Column(String(36), ForeignKey("bugs.id"), nullable=False)
    strategy = Column(Text, nullable=False)
    diff = Column(Text, nullable=True)
    files_changed = Column(JSON, default=list)
    tests_before = Column(String(50), default="")  # e.g. "14/18 passed"
    tests_after = Column(String(50), default="")   # e.g. "18/18 passed"
    success = Column(Boolean, default=False)
    repaired_by = Column(String(100), default="Repair Agent")
    timestamp = Column(DateTime, default=utc_now)
    
    project = relationship("Project", back_populates="repairs")

class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    target = Column(String(50), default="STAGING")  # STAGING, PRODUCTION
    environment = Column(String(50), default="Docker")
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, HEALTHY, UNHEALTHY, ROLLED_BACK
    app_url = Column(String(255), nullable=True)
    container_id = Column(String(100), nullable=True)
    health_check_status = Column(String(50), default="UNKNOWN")  # PASS, FAIL, UNKNOWN
    smoke_tests_passed = Column(Boolean, default=False)
    logs = Column(Text, nullable=True)
    deployed_at = Column(DateTime, default=utc_now)
    
    project = relationship("Project", back_populates="deployments")

class ProjectEvent(Base):
    __tablename__ = "project_events"
    
    id = Column(String(36), primary_key=True, default=gen_id)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # project.created, test.failed, repair.started, etc.
    source = Column(String(100), default="Orchestrator")
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    level = Column(String(50), default="INFO")  # INFO, SUCCESS, WARNING, ERROR
    timestamp = Column(DateTime, default=utc_now)
    
    project = relationship("Project", back_populates="events")
