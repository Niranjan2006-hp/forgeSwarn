import pytest
from app.agents.registry import TeamFormationEngine, AVAILABLE_AGENTS

def test_calculator_team_formation():
    prompt = "build an calculator app"
    team = TeamFormationEngine.form_team({}, domain="Mathematics & Utilities", user_prompt=prompt)
    agent_ids = [a["agent_id"] for a in team]
    
    # Mathematical calculator needs Math Engine, Frontend LCD, Testing, Debugger, Repair
    assert "math_engine_agent" in agent_ids
    assert "frontend_agent" in agent_ids
    assert "testing_agent" in agent_ids
    assert "debugger_agent" in agent_ids
    assert "repair_agent" in agent_ids
    
    # Must NOT have unnecessary relational/compliance agents
    assert "database_agent" not in agent_ids
    assert "compliance_agent" not in agent_ids
    assert "payment_agent" not in agent_ids
    assert "ml_engineer_agent" not in agent_ids
    
    # Verify requirement-grounded selection reason
    math_agent = next(a for a in team if a["agent_id"] == "math_engine_agent")
    assert "AST evaluation" in math_agent["selection_reason"]
    
    test_agent = next(a for a in team if a["agent_id"] == "testing_agent")
    assert "Zero-Division Safety Invariant" in test_agent["selection_reason"]

def test_healthcare_team_formation():
    prompt = "Build me a hospital appointment management system where patients book slots with doctors"
    team = TeamFormationEngine.form_team({}, domain="Healthcare", user_prompt=prompt)
    agent_ids = [a["agent_id"] for a in team]
    
    # Healthcare demands security, compliance, ACID database, backend, frontend, testing, etc.
    assert "database_agent" in agent_ids
    assert "security_agent" in agent_ids
    assert "compliance_agent" in agent_ids
    assert "backend_agent" in agent_ids
    assert "frontend_agent" in agent_ids
    assert "testing_agent" in agent_ids
    
    # Must NOT have math engine or ML agents
    assert "math_engine_agent" not in agent_ids
    assert "ml_engineer_agent" not in agent_ids
    
    # Verify HIPAA/PII reasoning
    comp_agent = next(a for a in team if a["agent_id"] == "compliance_agent")
    assert "HIPAA" in comp_agent["selection_reason"]
    
    db_agent = next(a for a in team if a["agent_id"] == "database_agent")
    assert "appointment booking" in db_agent["selection_reason"].lower()

def test_ecommerce_team_formation():
    prompt = "Build an e-commerce clothing store with checkout and cart and product catalog"
    team = TeamFormationEngine.form_team({}, domain="E-Commerce", user_prompt=prompt)
    agent_ids = [a["agent_id"] for a in team]
    
    # E-Commerce demands Payment & FinTech, Security, Database, Backend, Frontend
    assert "payment_agent" in agent_ids
    assert "security_agent" in agent_ids
    assert "database_agent" in agent_ids
    assert "backend_agent" in agent_ids
    assert "frontend_agent" in agent_ids
    
    pay_agent = next(a for a in team if a["agent_id"] == "payment_agent")
    assert "PCI-DSS" in pay_agent["selection_reason"] or "payment" in pay_agent["selection_reason"].lower()

def test_ml_pipeline_team_formation():
    prompt = "Build a machine learning fraud detection pipeline with model training and prediction endpoint"
    team = TeamFormationEngine.form_team({}, domain="AI & Machine Learning", user_prompt=prompt)
    agent_ids = [a["agent_id"] for a in team]
    
    # ML demands Data Engineer, ML Engineer, Model Evaluation
    assert "data_engineer_agent" in agent_ids
    assert "ml_engineer_agent" in agent_ids
    assert "model_eval_agent" in agent_ids
    assert "backend_agent" in agent_ids
    
    ml_agent = next(a for a in team if a["agent_id"] == "ml_engineer_agent")
    assert "training" in ml_agent["selection_reason"].lower() or "model" in ml_agent["selection_reason"].lower()

def test_todo_team_formation():
    prompt = "Build a todo task management application with kanban tags and deadlines"
    team = TeamFormationEngine.form_team({}, domain="Productivity", user_prompt=prompt)
    agent_ids = [a["agent_id"] for a in team]
    
    assert "database_agent" in agent_ids
    assert "backend_agent" in agent_ids
    assert "frontend_agent" in agent_ids
    assert "payment_agent" not in agent_ids
    assert "compliance_agent" not in agent_ids
    assert "math_engine_agent" not in agent_ids

def test_dynamic_custom_car_rental_team_formation():
    prompt = "Build a car rental system where users reserve vehicles and check return dates"
    team = TeamFormationEngine.form_team({}, domain="Vehicle Rental", user_prompt=prompt)
    agent_ids = [a["agent_id"] for a in team]
    
    # Must dynamically select database, backend, frontend, security, testing, debugger, repair, deployment
    assert "database_agent" in agent_ids
    assert "backend_agent" in agent_ids
    assert "frontend_agent" in agent_ids
    assert "security_agent" in agent_ids
    
    # Selection reasons must reference vehicles / rental entities dynamically
    fe_agent = next(a for a in team if a["agent_id"] == "frontend_agent")
    assert "vehicle" in fe_agent["selection_reason"].lower() or "rental" in fe_agent["selection_reason"].lower()
    
    test_agent = next(a for a in team if a["agent_id"] == "testing_agent")
    assert "double-booking" in test_agent["selection_reason"].lower() or "concurrency" in test_agent["selection_reason"].lower()
