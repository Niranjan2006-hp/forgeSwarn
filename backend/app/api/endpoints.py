import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Project, Requirement, EngineeringContract, Agent, AgentMessage,
    Artifact, Decision, TestCase, Bug, RepairAttempt, Deployment, ProjectEvent
)
from app.schemas.project import (
    ProjectCreate, ProjectResponse, RequirementSchema, RequirementCreate,
    EngineeringContractSchema, AgentSchema, AgentMessageSchema,
    ArtifactSchema, DecisionSchema, TestCaseSchema, BugSchema,
    RepairAttemptSchema, DeploymentSchema, ProjectEventSchema,
    ProjectMetricsSchema, ApproveRequest
)
from app.orchestrator.orchestrator import SwarmOrchestrator
from app.orchestrator.events import event_broadcaster
from app.deployment.manager import DeploymentManager

router = APIRouter()

def calculate_metrics(project: Project, db: Session) -> ProjectMetricsSchema:
    total_reqs = db.query(Requirement).filter(Requirement.project_id == project.id).count()
    impl_reqs = db.query(Requirement).filter(Requirement.project_id == project.id, Requirement.status == "VERIFIED").count()
    req_cov = round((impl_reqs / total_reqs * 100), 1) if total_reqs > 0 else 0.0

    total_tests = db.query(TestCase).filter(TestCase.project_id == project.id).count()
    passed_tests = db.query(TestCase).filter(TestCase.project_id == project.id, TestCase.status == "PASSED").count()
    test_rate = round((passed_tests / total_tests * 100), 1) if total_tests > 0 else 0.0

    total_bugs = db.query(Bug).filter(Bug.project_id == project.id).count()
    repaired_bugs = db.query(Bug).filter(Bug.project_id == project.id, Bug.status == "REPAIRED").count()
    repair_rate = round((repaired_bugs / total_bugs * 100), 1) if total_bugs > 0 else (100.0 if total_bugs == 0 and total_tests > 0 else 0.0)

    total_deps = db.query(Deployment).filter(Deployment.project_id == project.id).count()
    succ_deps = db.query(Deployment).filter(Deployment.project_id == project.id, Deployment.status == "HEALTHY").count()
    dep_rate = round((succ_deps / total_deps * 100), 1) if total_deps > 0 else (100.0 if project.status == "COMPLETED" else 0.0)

    return ProjectMetricsSchema(
        requirement_coverage=req_cov,
        test_pass_rate=test_rate,
        autonomous_repair_rate=repair_rate,
        human_interventions=1 if project.approved_by_user else 0,
        deployment_success_rate=dep_rate,
        total_requirements=total_reqs,
        implemented_requirements=impl_reqs,
        total_tests=total_tests,
        passed_tests=passed_tests,
        total_bugs=total_bugs,
        repaired_bugs=repaired_bugs
    )

@router.get("/health")
def health_check():
    return {"status": "HEALTHY", "platform": "ForgeSwarm Autonomous Engineering Swarm", "version": "1.0.0"}

@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    proj = Project(
        name=data.name,
        raw_requirement=data.requirement,
        application_type=data.application_type,
        tech_preference=data.tech_preference,
        deployment_target=data.deployment_target,
        autonomy_level=data.autonomy_level,
        is_demo_mode=data.is_demo_mode,
        llm_provider=data.llm_provider,
        domain="Healthcare" if ("hospital" in data.requirement.lower() or "patient" in data.requirement.lower()) else "Enterprise"
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    
    # Calculate baseline metrics
    resp = ProjectResponse.model_validate(proj)
    resp.metrics = calculate_metrics(proj, db)
    return resp

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    out = []
    for p in projects:
        resp = ProjectResponse.model_validate(p)
        resp.metrics = calculate_metrics(p, db)
        out.append(resp)
    return out

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Auto-ensure staging server is online for completed projects
    if proj.status == "COMPLETED" and project_id not in DeploymentManager._running_processes:
        from app.execution.workspace import ProjectWorkspace
        ws = ProjectWorkspace(project_id)
        if (ws.root_path / "app" / "main.py").exists():
            dep_res = DeploymentManager.deploy_staging(project_id, ws)
            if dep_res.get("app_url"):
                proj.app_url = dep_res["app_url"]
                proj.app_port = dep_res["port"]
                db.commit()

    resp = ProjectResponse.model_validate(proj)
    resp.metrics = calculate_metrics(proj, db)
    return resp

@router.post("/projects/{project_id}/start")
async def start_engineering_pipeline(project_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    async def run_pipeline_task(p_id: str):
        from app.core.database import SessionLocal
        task_db = SessionLocal()
        try:
            p = task_db.query(Project).filter(Project.id == p_id).first()
            if p:
                orchestrator = SwarmOrchestrator(task_db, p)
                await orchestrator.run_full_pipeline()
        finally:
            task_db.close()

    background_tasks.add_task(run_pipeline_task, project_id)
    return {"message": "Swarm pipeline started successfully", "project_id": project_id, "status": "STARTED"}

@router.get("/projects/{project_id}/agents", response_model=List[AgentSchema])
def get_project_agents(project_id: str, db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.project_id == project_id).all()
    return agents

@router.get("/projects/{project_id}/events", response_model=List[ProjectEventSchema])
def get_project_events(project_id: str, db: Session = Depends(get_db)):
    events = db.query(ProjectEvent).filter(ProjectEvent.project_id == project_id).order_by(ProjectEvent.timestamp.asc()).all()
    return events

@router.get("/projects/{project_id}/messages", response_model=List[AgentMessageSchema])
def get_project_messages(project_id: str, db: Session = Depends(get_db)):
    return db.query(AgentMessage).filter(AgentMessage.project_id == project_id).order_by(AgentMessage.created_at.asc()).all()

@router.get("/projects/{project_id}/requirements", response_model=List[RequirementSchema])
def get_project_requirements(project_id: str, db: Session = Depends(get_db)):
    return db.query(Requirement).filter(Requirement.project_id == project_id).all()

@router.post("/projects/{project_id}/requirements", response_model=RequirementSchema, status_code=201)
def add_project_requirement(project_id: str, data: RequirementCreate, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    count = db.query(Requirement).filter(Requirement.project_id == project_id, Requirement.req_type == data.req_type).count() + 1
    prefix = "FR" if data.req_type == "FUNCTIONAL" else ("BR" if data.req_type == "BUSINESS_RULE" else "SEC")
    code = f"{prefix}-{count:03d}"

    req = Requirement(
        project_id=project_id,
        req_type=data.req_type,
        code=code,
        title=data.title,
        description=data.description,
        priority=data.priority,
        status="PENDING"
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.get("/projects/{project_id}/contract")
def get_project_contract(project_id: str, db: Session = Depends(get_db)):
    contract = db.query(EngineeringContract).filter(EngineeringContract.project_id == project_id).first()
    if not contract:
        return {"status": "PENDING", "content_json": {}}
    return contract.content_json

@router.get("/projects/{project_id}/artifacts", response_model=List[ArtifactSchema])
def get_project_artifacts(project_id: str, db: Session = Depends(get_db)):
    return db.query(Artifact).filter(Artifact.project_id == project_id).all()

@router.get("/projects/{project_id}/artifacts/{filename}")
def get_project_artifact_content(project_id: str, filename: str, db: Session = Depends(get_db)):
    art = db.query(Artifact).filter(Artifact.project_id == project_id, Artifact.filename == filename).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {"filename": art.filename, "content": art.content, "file_type": art.file_type}

@router.get("/projects/{project_id}/tests", response_model=List[TestCaseSchema])
def get_project_tests(project_id: str, db: Session = Depends(get_db)):
    return db.query(TestCase).filter(TestCase.project_id == project_id).all()

@router.get("/projects/{project_id}/bugs", response_model=List[BugSchema])
def get_project_bugs(project_id: str, db: Session = Depends(get_db)):
    return db.query(Bug).filter(Bug.project_id == project_id).all()

@router.get("/projects/{project_id}/repairs", response_model=List[RepairAttemptSchema])
def get_project_repairs(project_id: str, db: Session = Depends(get_db)):
    return db.query(RepairAttempt).filter(RepairAttempt.project_id == project_id).all()

@router.get("/projects/{project_id}/decisions", response_model=List[DecisionSchema])
def get_project_decisions(project_id: str, db: Session = Depends(get_db)):
    return db.query(Decision).filter(Decision.project_id == project_id).all()

@router.get("/projects/{project_id}/deployment", response_model=List[DeploymentSchema])
def get_project_deployment(project_id: str, db: Session = Depends(get_db)):
    return db.query(Deployment).filter(Deployment.project_id == project_id).all()

@router.post("/projects/{project_id}/approve")
def approve_high_risk_gate(project_id: str, req: ApproveRequest, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    proj.approved_by_user = req.approved
    proj.approval_required = False
    db.commit()
    return {"message": "Approval recorded", "approved": req.approved}

@router.post("/projects/{project_id}/stop")
def stop_project_deployment(project_id: str, db: Session = Depends(get_db)):
    DeploymentManager.stop_deployment(project_id)
    return {"message": "Deployment stopped", "project_id": project_id}

@router.get("/projects/{project_id}/stream")
async def stream_project_events(project_id: str):
    """
    Server-Sent Events (SSE) stream delivering real-time agent activity and state changes.
    """
    async def event_generator():
        async for evt in event_broadcaster.subscribe(project_id):
            yield f"data: {json.dumps(evt)}\n\n"
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
