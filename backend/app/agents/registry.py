from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class AgentMetadata:
    agent_id: str
    name: str
    role: str
    capabilities: List[str]
    tools: List[str]
    restrictions: List[str]
    default_confidence: float = 0.95
    avatar_color: str = "#06B6D4"

AVAILABLE_AGENTS: Dict[str, AgentMetadata] = {
    "requirements_agent": AgentMetadata(
        agent_id="requirements_agent",
        name="Requirements Analyst",
        role="Product & Domain Analyst",
        capabilities=["requirement_decomposition", "business_rule_extraction", "acceptance_criteria", "entity_modeling"],
        tools=["nlp_analyzer", "domain_knowledge_base", "traceability_matrix"],
        restrictions=["cannot_write_code", "cannot_deploy"],
        default_confidence=0.98,
        avatar_color="#8B5CF6"
    ),
    "architect_agent": AgentMetadata(
        agent_id="architect_agent",
        name="Chief Architect",
        role="System & API Architect",
        capabilities=["system_architecture", "api_design", "data_modeling", "tech_stack_selection"],
        tools=["openapi_generator", "architecture_designer", "tradeoff_analyzer"],
        restrictions=["cannot_deploy_without_testing", "cannot_bypass_security"],
        default_confidence=0.96,
        avatar_color="#3B82F6"
    ),
    "database_agent": AgentMetadata(
        agent_id="database_agent",
        name="Database Engineer",
        role="Data Persistence & Transaction Lead",
        capabilities=["schema_design", "acid_transactions", "foreign_keys", "unique_constraints", "query_optimization"],
        tools=["sql_generator", "migration_engine", "integrity_checker"],
        restrictions=["cannot_modify_prod_without_backup", "cannot_bypass_constraints"],
        default_confidence=0.97,
        avatar_color="#06B6D4"
    ),
    "backend_agent": AgentMetadata(
        agent_id="backend_agent",
        name="Backend Engineer",
        role="API & Business Logic Developer",
        capabilities=["fastapi_development", "jwt_auth", "service_layer", "transactional_booking", "api_debugging"],
        tools=["python_interpreter", "pydantic_validator", "orm_bridge"],
        restrictions=["cannot_deploy_production", "cannot_change_security_policy_without_review"],
        default_confidence=0.95,
        avatar_color="#10B981"
    ),
    "frontend_agent": AgentMetadata(
        agent_id="frontend_agent",
        name="Frontend Engineer",
        role="UI/UX & Client Application Developer",
        capabilities=["react_development", "tailwind_css", "state_management", "api_client_integration", "responsive_ui"],
        tools=["vite_bundler", "component_library", "axios_client"],
        restrictions=["cannot_access_database_directly", "cannot_modify_backend_contracts"],
        default_confidence=0.94,
        avatar_color="#EC4899"
    ),
    "security_agent": AgentMetadata(
        agent_id="security_agent",
        name="Security & Compliance Lead",
        role="AppSec & Data Protection Officer",
        capabilities=["vulnerability_scanning", "secrets_detection", "owasp_top_10", "hipaa_compliance", "jwt_hardening"],
        tools=["ast_scanner", "secret_finder", "auth_gate_enforcer"],
        restrictions=["cannot_bypass_compliance_rules"],
        default_confidence=0.99,
        avatar_color="#F43F5E"
    ),
    "testing_agent": AgentMetadata(
        agent_id="testing_agent",
        name="QA & Test Automation Lead",
        role="Requirement-Based Testing Engineer",
        capabilities=["acceptance_testing", "concurrency_testing", "pytest_automation", "regression_testing", "boundary_testing"],
        tools=["pytest_runner", "concurrency_simulator", "coverage_tracker"],
        restrictions=["cannot_falsify_results", "cannot_modify_code_directly"],
        default_confidence=0.96,
        avatar_color="#F59E0B"
    ),
    "debugger_agent": AgentMetadata(
        agent_id="debugger_agent",
        name="Root Cause Diagnostic Lead",
        role="Diagnostic & Incident Investigator",
        capabilities=["stack_trace_analysis", "race_condition_detection", "toctou_diagnosis", "evidence_synthesis"],
        tools=["log_analyzer", "ast_diff_inspector", "trace_debugger"],
        restrictions=["cannot_apply_fixes_directly"],
        default_confidence=0.98,
        avatar_color="#E11D48"
    ),
    "repair_agent": AgentMetadata(
        agent_id="repair_agent",
        name="Autonomous Repair Engineer",
        role="Surgical Bug Fix Specialist",
        capabilities=["surgical_patching", "ast_refactoring", "atomic_locking", "diff_generation"],
        tools=["code_patcher", "ast_rewriter", "safe_editor"],
        restrictions=["must_pass_regression_tests", "smallest_safe_change_only"],
        default_confidence=0.95,
        avatar_color="#14B8A6"
    ),
    "deployment_agent": AgentMetadata(
        agent_id="deployment_agent",
        name="DevOps & Site Reliability Engineer",
        role="Containerization & Staging Lead",
        capabilities=["docker_build", "docker_compose", "health_probing", "staging_deployment", "automated_rollback"],
        tools=["docker_cli", "health_checker", "process_manager"],
        restrictions=["cannot_deploy_failing_build", "requires_approval_for_prod"],
        default_confidence=0.97,
        avatar_color="#6366F1"
    )
}

class TeamFormationEngine:
    """
    Dynamically forms an optimal engineering team based on the Engineering Contract.
    Provides explainable selection reasoning for every agent selected.
    """
    @staticmethod
    def form_team(contract: Dict[str, Any], domain: str = "Healthcare") -> List[Dict[str, Any]]:
        selected: List[Dict[str, Any]] = []
        
        # Base core engineering team for any full-stack app
        base_roles = ["requirements_agent", "architect_agent", "database_agent", "backend_agent", "frontend_agent", "testing_agent", "debugger_agent", "repair_agent", "deployment_agent"]
        
        reasons = {
            "requirements_agent": "Selected to formalize natural-language prompts into rigid functional requirements and acceptance criteria.",
            "architect_agent": "Selected to design modular service layers, entity relations, and REST contracts.",
            "database_agent": "Selected because appointment booking demands strict relational consistency and ACID uniqueness constraints.",
            "backend_agent": "Selected to build the FastAPI business logic, authentication handlers, and slot booking services.",
            "frontend_agent": "Selected to engineer the patient portal, appointment booking views, and doctor directories.",
            "testing_agent": "Selected to generate requirement-based concurrency test cases for double-booking prevention (BR-001).",
            "debugger_agent": "Selected to perform deep root cause diagnosis upon test failures and identify race conditions.",
            "repair_agent": "Selected to apply surgical code repairs and maintain zero regressions.",
            "deployment_agent": "Selected to containerize the application, execute staging deployments, and perform health check verification."
        }
        
        for agent_key in base_roles:
            meta = AVAILABLE_AGENTS[agent_key]
            selected.append({
                "agent_id": meta.agent_id,
                "name": meta.name,
                "role": meta.role,
                "capabilities": meta.capabilities,
                "tools": meta.tools,
                "restrictions": meta.restrictions,
                "confidence": meta.default_confidence,
                "avatar_color": meta.avatar_color,
                "selection_reason": reasons.get(agent_key, "Core software engineering capability requirement.")
            })
            
        # Domain-driven dynamic additions (Healthcare, Fintech, ML, etc.)
        is_healthcare = "health" in domain.lower() or "hospital" in domain.lower() or "medical" in domain.lower()
        if is_healthcare:
            sec_meta = AVAILABLE_AGENTS["security_agent"]
            selected.append({
                "agent_id": sec_meta.agent_id,
                "name": sec_meta.name,
                "role": sec_meta.role,
                "capabilities": sec_meta.capabilities,
                "tools": sec_meta.tools,
                "restrictions": sec_meta.restrictions,
                "confidence": sec_meta.default_confidence,
                "avatar_color": sec_meta.avatar_color,
                "selection_reason": "Security & Compliance Agent selected because the healthcare platform processes sensitive patient records, medical appointments, and requires strict HIPAA/PII access boundaries."
            })
            
        return selected
