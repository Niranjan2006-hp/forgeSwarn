from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    requirement: str = Field(..., description="Natural language software requirement")
    application_type: str = Field(default="Web Application")
    tech_preference: str = Field(default="FastAPI + React")
    deployment_target: str = Field(default="Docker / Local")
    autonomy_level: str = Field(default="HIGH")
    is_demo_mode: bool = Field(default=True)
    llm_provider: str = Field(default="mock")

class RequirementSchema(BaseModel):
    id: str
    req_type: str
    code: str
    title: str
    description: str
    priority: str
    status: str

    class Config:
        from_attributes = True

class EngineeringContractSchema(BaseModel):
    id: str
    project_id: str
    content_json: Dict[str, Any]
    version: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AgentSchema(BaseModel):
    id: str
    agent_id: str
    name: str
    role: str
    status: str
    selection_reason: Optional[str] = None
    capabilities: List[str] = []
    tools: List[str] = []
    restrictions: List[str] = []
    workload: int = 0
    confidence: float = 0.95
    avatar_color: str = "#06B6D4"

    class Config:
        from_attributes = True

class AgentMessageSchema(BaseModel):
    id: str
    sender_name: str
    recipient: str
    content: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True

class ArtifactSchema(BaseModel):
    id: str
    filename: str
    file_type: str
    content: str
    created_by: str
    version: int
    updated_at: datetime

    class Config:
        from_attributes = True

class DecisionSchema(BaseModel):
    id: str
    decision: str
    alternatives: List[str] = []
    reason: str
    participating_agents: List[str] = []
    confidence: float = 0.95
    affected_components: List[str] = []
    timestamp: datetime

    class Config:
        from_attributes = True

class TestCaseSchema(BaseModel):
    id: str
    test_id: str
    requirement_id: Optional[str] = None
    category: str
    title: str
    description: Optional[str] = None
    expected_outcome: str
    status: str
    execution_time_ms: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class BugSchema(BaseModel):
    id: str
    test_id: Optional[str] = None
    requirement_id: Optional[str] = None
    title: str
    severity: str
    status: str
    root_cause: Optional[str] = None
    evidence: Optional[str] = None
    affected_component: Optional[str] = None
    recommended_fix: Optional[str] = None
    diagnosed_by: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RepairAttemptSchema(BaseModel):
    id: str
    bug_id: str
    strategy: str
    diff: Optional[str] = None
    files_changed: List[str] = []
    tests_before: str = ""
    tests_after: str = ""
    success: bool = False
    repaired_by: str = "Repair Agent"
    timestamp: datetime

    class Config:
        from_attributes = True

class DeploymentSchema(BaseModel):
    id: str
    target: str
    environment: str
    status: str
    app_url: Optional[str] = None
    container_id: Optional[str] = None
    health_check_status: str
    smoke_tests_passed: bool = False
    logs: Optional[str] = None
    deployed_at: datetime

    class Config:
        from_attributes = True

class ProjectEventSchema(BaseModel):
    id: str
    event_type: str
    source: str
    message: str
    details: Dict[str, Any] = {}
    level: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ProjectMetricsSchema(BaseModel):
    requirement_coverage: float = 0.0
    test_pass_rate: float = 0.0
    autonomous_repair_rate: float = 0.0
    human_interventions: int = 0
    deployment_success_rate: float = 0.0
    total_requirements: int = 0
    implemented_requirements: int = 0
    total_tests: int = 0
    passed_tests: int = 0
    total_bugs: int = 0
    repaired_bugs: int = 0

class ProjectResponse(BaseModel):
    id: str
    name: str
    raw_requirement: str
    domain: str
    application_type: str
    tech_preference: str
    deployment_target: str
    autonomy_level: str
    status: str
    is_demo_mode: bool
    llm_provider: str
    risk_level: str
    approval_required: bool
    approved_by_user: bool
    app_url: Optional[str] = None
    app_port: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    metrics: Optional[ProjectMetricsSchema] = None

    class Config:
        from_attributes = True

class ApproveRequest(BaseModel):
    approved: bool = True
    comment: Optional[str] = None
