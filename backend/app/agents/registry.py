import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from app.execution.domain_analyzer import analyze_user_prompt, DomainSpec

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
        capabilities=["requirement_decomposition", "business_rule_extraction", "acceptance_criteria", "entity_modeling", "traceability_mapping"],
        tools=["nlp_analyzer", "domain_knowledge_base", "traceability_matrix"],
        restrictions=["cannot_write_code", "cannot_deploy"],
        default_confidence=0.98,
        avatar_color="#8B5CF6"
    ),
    "architect_agent": AgentMetadata(
        agent_id="architect_agent",
        name="Chief Architect",
        role="System & API Architect",
        capabilities=["system_architecture", "api_design", "data_modeling", "tech_stack_selection", "component_topology"],
        tools=["openapi_generator", "architecture_designer", "tradeoff_analyzer"],
        restrictions=["cannot_deploy_without_testing", "cannot_bypass_security"],
        default_confidence=0.96,
        avatar_color="#3B82F6"
    ),
    "database_agent": AgentMetadata(
        agent_id="database_agent",
        name="Database Engineer",
        role="Data Persistence & Transaction Lead",
        capabilities=["schema_design", "acid_transactions", "foreign_keys", "unique_constraints", "query_optimization", "migration_management"],
        tools=["sql_generator", "migration_engine", "integrity_checker"],
        restrictions=["cannot_modify_prod_without_backup", "cannot_bypass_constraints"],
        default_confidence=0.97,
        avatar_color="#06B6D4"
    ),
    "backend_agent": AgentMetadata(
        agent_id="backend_agent",
        name="Backend Engineer",
        role="API & Core Logic Developer",
        capabilities=["fastapi_development", "jwt_auth", "service_layer", "transactional_logic", "api_debugging", "orm_bridge"],
        tools=["python_interpreter", "pydantic_validator", "orm_bridge"],
        restrictions=["cannot_deploy_production", "cannot_change_security_policy_without_review"],
        default_confidence=0.95,
        avatar_color="#10B981"
    ),
    "frontend_agent": AgentMetadata(
        agent_id="frontend_agent",
        name="Frontend Engineer",
        role="UI/UX & Client Application Specialist",
        capabilities=["react_development", "tailwind_css", "state_management", "api_client_integration", "responsive_ui", "lcd_canvas_rendering"],
        tools=["vite_bundler", "component_library", "axios_client"],
        restrictions=["cannot_access_database_directly", "cannot_modify_backend_contracts"],
        default_confidence=0.94,
        avatar_color="#EC4899"
    ),
    "security_agent": AgentMetadata(
        agent_id="security_agent",
        name="Security & AppSec Lead",
        role="AppSec & Threat Mitigation Officer",
        capabilities=["vulnerability_scanning", "secrets_detection", "owasp_top_10", "jwt_hardening", "ast_sanitization", "input_injection_defense"],
        tools=["ast_scanner", "secret_finder", "auth_gate_enforcer"],
        restrictions=["cannot_bypass_compliance_rules"],
        default_confidence=0.99,
        avatar_color="#F43F5E"
    ),
    "compliance_agent": AgentMetadata(
        agent_id="compliance_agent",
        name="Regulatory Compliance Officer",
        role="Governance & Data Privacy Specialist",
        capabilities=["hipaa_compliance", "gdpr_data_privacy", "audit_logging", "consent_verification", "pii_anonymization"],
        tools=["policy_engine", "audit_trail_validator", "pii_masker"],
        restrictions=["cannot_alter_audit_records", "mandatory_review_for_sensitive_data"],
        default_confidence=0.98,
        avatar_color="#A855F7"
    ),
    "payment_agent": AgentMetadata(
        agent_id="payment_agent",
        name="Payment & FinTech Specialist",
        role="Transactions & Payment Systems Lead",
        capabilities=["payment_gateway_integration", "pci_dss_compliance", "idempotent_transactions", "checkout_state_machine", "ledger_reconciliation"],
        tools=["transaction_simulator", "idempotency_validator", "pci_checker"],
        restrictions=["cannot_store_raw_card_numbers", "cannot_bypass_idempotency"],
        default_confidence=0.97,
        avatar_color="#10B981"
    ),
    "data_engineer_agent": AgentMetadata(
        agent_id="data_engineer_agent",
        name="Data Pipelines Engineer",
        role="ETL & Feature Pipeline Specialist",
        capabilities=["data_ingestion", "feature_preprocessing", "schema_validation", "dataset_cleaning", "streaming_pipelines"],
        tools=["data_cleanser", "schema_validator", "feature_transformer"],
        restrictions=["cannot_expose_raw_pii", "cannot_mutate_source_records"],
        default_confidence=0.96,
        avatar_color="#F97316"
    ),
    "ml_engineer_agent": AgentMetadata(
        agent_id="ml_engineer_agent",
        name="Machine Learning Engineer",
        role="Model Architecture & Training Lead",
        capabilities=["model_training", "hyperparameter_tuning", "model_serialization", "feature_store_integration", "inference_pipeline"],
        tools=["model_trainer", "scikit_pipeline", "weight_serializer"],
        restrictions=["cannot_deploy_unvalidated_models", "must_log_training_artifacts"],
        default_confidence=0.95,
        avatar_color="#8B5CF6"
    ),
    "model_eval_agent": AgentMetadata(
        agent_id="model_eval_agent",
        name="Model Evaluation Specialist",
        role="AI Verification & Robustness Lead",
        capabilities=["metric_evaluation", "drift_detection", "confusion_matrix_analysis", "bias_detection", "adversarial_testing"],
        tools=["metric_evaluator", "drift_detector", "adversarial_probe"],
        restrictions=["cannot_approve_model_below_accuracy_threshold"],
        default_confidence=0.97,
        avatar_color="#EC4899"
    ),
    "math_engine_agent": AgentMetadata(
        agent_id="math_engine_agent",
        name="Mathematical & Algorithmic Specialist",
        role="Numerical Accuracy & Engine Lead",
        capabilities=["ast_expression_parsing", "ieee_754_precision", "arithmetic_precedence", "zero_division_guard", "scientific_computation"],
        tools=["ast_math_evaluator", "precision_analyzer", "formula_validator"],
        restrictions=["cannot_execute_arbitrary_code", "must_prevent_zero_division"],
        default_confidence=0.99,
        avatar_color="#38BDF8"
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
        capabilities=["stack_trace_analysis", "race_condition_detection", "arithmetic_fault_diagnosis", "toctou_diagnosis", "evidence_synthesis"],
        tools=["log_analyzer", "ast_diff_inspector", "trace_debugger"],
        restrictions=["cannot_apply_fixes_directly"],
        default_confidence=0.98,
        avatar_color="#E11D48"
    ),
    "repair_agent": AgentMetadata(
        agent_id="repair_agent",
        name="Autonomous Repair Engineer",
        role="Surgical Bug Fix Specialist",
        capabilities=["surgical_patching", "ast_refactoring", "atomic_locking", "defensive_error_handling", "diff_generation"],
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
    Dynamically forms an optimal engineering team based on the Problem Requirement and Engineering Contract.
    The swarm is NOT a fixed set; agents are assembled according to specific technical, algorithmic,
    domain, and compliance needs, with explainable requirement-grounded selection reasoning.
    """
    @staticmethod
    def form_team(contract: Dict[str, Any], domain: str = "Healthcare", user_prompt: str = "") -> List[Dict[str, Any]]:
        query_text = f"{user_prompt} {domain} {contract.get('project_name', '')}".strip()
        spec: DomainSpec = analyze_user_prompt(query_text)
        
        lower_prompt = query_text.lower()
        selected: List[Dict[str, Any]] = []
        assigned_roles: List[str] = []
        custom_reasons: Dict[str, str] = {}

        # -------------------------------------------------------------
        # 1. MATHEMATICAL & CALCULATOR UTILITY ARCHETYPE
        # -------------------------------------------------------------
        if spec.ui_type == "CALCULATOR" or bool(re.search(r'\b(calculator|calc|arithmetic|algebra|math)\b', lower_prompt)):
            assigned_roles = [
                "requirements_agent",
                "architect_agent",
                "math_engine_agent",
                "frontend_agent",
                "testing_agent",
                "debugger_agent",
                "repair_agent",
                "deployment_agent"
            ]
            custom_reasons = {
                "requirements_agent": "Decomposes mathematical operations, standard and scientific functional requirements, and formalizes the Zero-Division Safety Invariant (BR-001).",
                "architect_agent": "Designs the AST safe expression evaluation topology, input tokenization pipeline, and IEEE-754 precision boundaries.",
                "math_engine_agent": "Selected because arithmetic and scientific calculations require specialized AST evaluation, operator precedence rules, and safe mathematical sandboxing.",
                "frontend_agent": "Selected to engineer the tactile virtual keypad, responsive dual-line LCD display with glowing formula tape, and memory register controls.",
                "testing_agent": "Selected to generate requirement-based arithmetic assertion suites, precedence checks, and verify the Zero-Division Safety Invariant (BR-001).",
                "debugger_agent": "Selected to trap unhandled arithmetic runtime exceptions, ZeroDivisionError faults, and floating-point precision drifts.",
                "repair_agent": "Selected to synthesize surgical AST patches with defensive denominator validation to prevent application crashes.",
                "deployment_agent": "Selected to package the high-speed calculator microservice into an isolated staging container with health check validation."
            }

        # -------------------------------------------------------------
        # 2. HEALTHCARE & HOSPITAL CLINICAL ARCHETYPE
        # -------------------------------------------------------------
        elif bool(re.search(r'\b(hospital|doctor|patient|clinic|health|medical|appointment)\b', lower_prompt)):
            assigned_roles = [
                "requirements_agent",
                "architect_agent",
                "database_agent",
                "backend_agent",
                "frontend_agent",
                "security_agent",
                "compliance_agent",
                "testing_agent",
                "debugger_agent",
                "repair_agent",
                "deployment_agent"
            ]
            custom_reasons = {
                "requirements_agent": "Decomposes patient registration, doctor schedules, slot booking workflows, and the double-booking concurrency invariant (BR-001).",
                "architect_agent": "Designs multi-tiered healthcare portal architecture, relational doctor-patient schemas, and authenticated REST endpoints.",
                "database_agent": "Selected because appointment booking demands strict transactional consistency, foreign key integrity, and unique composite slot constraints.",
                "backend_agent": "Selected to build the appointment scheduling services, slot reservation logic, and JWT authentication layer.",
                "frontend_agent": "Selected to engineer the patient portal, doctor directories, interactive calendar slot selector, and appointment booking views.",
                "security_agent": "Selected because healthcare applications manage sensitive patient records and medical appointments, requiring strict JWT route protection.",
                "compliance_agent": "Selected to enforce HIPAA/PII privacy guidelines, sensitive health record safeguards, and immutable medical audit trails.",
                "testing_agent": "Selected to generate concurrency test suites simulating simultaneous patient booking attempts for the same doctor and time slot (BR-001).",
                "debugger_agent": "Selected to analyze TOCTOU race conditions and appointment scheduling transaction conflicts under concurrent load.",
                "repair_agent": "Selected to implement atomic slot reservation with database-level isolation to eliminate double-booking.",
                "deployment_agent": "Selected to containerize the healthcare platform, execute staging deployments, and perform automated health check verification."
            }

        # -------------------------------------------------------------
        # 3. TODO & PRODUCTIVITY TASK MANAGEMENT ARCHETYPE
        # -------------------------------------------------------------
        elif spec.ui_type == "TODO" or bool(re.search(r'\b(todo|tasks?|kanban|productivity)\b', lower_prompt)):
            assigned_roles = [
                "requirements_agent",
                "architect_agent",
                "database_agent",
                "backend_agent",
                "frontend_agent",
                "testing_agent",
                "debugger_agent",
                "repair_agent",
                "deployment_agent"
            ]
            custom_reasons = {
                "requirements_agent": "Decomposes task lifecycles, priority ordering, deadline rules, and status transition invariants.",
                "architect_agent": "Designs responsive task management schema, filtering REST endpoints, and status state machine.",
                "database_agent": "Selected to model task tables, tag relationships, cascade deletions, and index deadline queries.",
                "backend_agent": "Selected to implement task CRUD endpoints, priority sort filters, and completion status toggles.",
                "frontend_agent": "Selected to engineer interactive task boards, status filters, tactile completion checkboxes, and quick-add inputs.",
                "testing_agent": "Selected to generate acceptance test suites for task creation, state toggling, and boundary validation.",
                "debugger_agent": "Selected to diagnose state synchronization anomalies and orphaned task relations.",
                "repair_agent": "Selected to enforce atomic task updates and idempotent status transitions.",
                "deployment_agent": "Selected to deploy the task application to staging and verify system responsiveness."
            }

        # -------------------------------------------------------------
        # 4. E-COMMERCE, STORE & MARKETPLACE ARCHETYPE
        # -------------------------------------------------------------
        elif bool(re.search(r'\b(ecommerce|e-commerce|shop|store|cart|checkout|inventory|orders?|products?)\b', lower_prompt)):
            assigned_roles = [
                "requirements_agent",
                "architect_agent",
                "database_agent",
                "backend_agent",
                "frontend_agent",
                "payment_agent",
                "security_agent",
                "testing_agent",
                "debugger_agent",
                "repair_agent",
                "deployment_agent"
            ]
            custom_reasons = {
                "requirements_agent": "Decomposes product catalog, shopping cart, checkout workflows, and the non-negative inventory constraint (BR-001).",
                "architect_agent": "Designs scalable e-commerce microservices, shopping cart session cache, and order fulfillment topology.",
                "database_agent": "Selected to enforce atomic stock decrements, inventory constraints, and foreign key integrity across orders and products.",
                "backend_agent": "Selected to build product search, shopping cart APIs, order placement queues, and inventory allocation services.",
                "frontend_agent": "Selected to engineer the dynamic storefront, product catalog, cart drawer, and responsive checkout flows.",
                "payment_agent": "Selected to manage secure checkout payment gateways, idempotency keys, and PCI-DSS compliance.",
                "security_agent": "Selected to guard checkout flows against CSRF, order tampering, price manipulation, and credential stuffing.",
                "testing_agent": "Selected to execute concurrency tests simulating flash-sales attempting to purchase the last available stock item.",
                "debugger_agent": "Selected to diagnose inventory decrement race conditions and payment settlement anomalies.",
                "repair_agent": "Selected to implement atomic conditional SQL stock decrements to guarantee stock never drops below zero.",
                "deployment_agent": "Selected to containerize the storefront and deploy verified staging instances with health verification."
            }

        # -------------------------------------------------------------
        # 5. MACHINE LEARNING & DATA PIPELINE ARCHETYPE
        # -------------------------------------------------------------
        elif bool(re.search(r'\b(ml|machine\s+learning|models?|predictions?|datasets?|train(?:ing)?)\b', lower_prompt)):
            assigned_roles = [
                "requirements_agent",
                "architect_agent",
                "data_engineer_agent",
                "ml_engineer_agent",
                "model_eval_agent",
                "backend_agent",
                "frontend_agent",
                "testing_agent",
                "debugger_agent",
                "repair_agent",
                "deployment_agent"
            ]
            custom_reasons = {
                "requirements_agent": "Formalizes ML objectives, target variables, metric thresholds, and inference latency requirements.",
                "architect_agent": "Designs asynchronous training pipelines, serialized model registries, and low-latency prediction endpoints.",
                "data_engineer_agent": "Selected to build data ingestion pipelines, feature cleaning transformers, and dataset validation routines.",
                "ml_engineer_agent": "Selected to architect machine learning model pipelines, train predictors, and serialize inference weights.",
                "model_eval_agent": "Selected to evaluate model accuracy, precision/recall, confusion matrices, and monitor for inference data drift.",
                "backend_agent": "Selected to build high-throughput prediction REST endpoints and model serving microservices.",
                "frontend_agent": "Selected to build interactive ML performance dashboards, metric visualizations, and live prediction playgrounds.",
                "testing_agent": "Selected to test adversarial feature edge cases, malformed schema inputs, and latency benchmarks.",
                "debugger_agent": "Selected to diagnose model convergence failures, feature mismatch bugs, and inference anomalies.",
                "repair_agent": "Selected to surgically patch feature engineering pipelines and defensive inference fallback mechanisms.",
                "deployment_agent": "Selected to containerize the ML serving application and orchestrate staging health checks."
            }

        # -------------------------------------------------------------
        # 6. DYNAMIC GENERAL ARCHETYPE (CUSTOM / ARBITRARY USER PROMPTS)
        # -------------------------------------------------------------
        else:
            assigned_roles = [
                "requirements_agent",
                "architect_agent",
                "database_agent",
                "backend_agent",
                "frontend_agent",
                "security_agent",
                "testing_agent",
                "debugger_agent",
                "repair_agent",
                "deployment_agent"
            ]
            custom_reasons = {
                "requirements_agent": f"Formalizes user requirements for {spec.project_name} into acceptance criteria and boundary invariants.",
                "architect_agent": f"Designs modular system topology, REST contracts, and data persistence for {spec.item_plural}.",
                "database_agent": f"Selected to enforce transactional consistency, relational constraints, and audit logging for {spec.item_singular} operations.",
                "backend_agent": f"Selected to implement core {spec.domain} business logic, {spec.action_name} actions, and API service layers.",
                "frontend_agent": f"Selected to build the {spec.catalog_title} interface, interactive {spec.action_label} views, and real-time status feeds.",
                "security_agent": f"Selected to enforce JWT route authorization, cryptographic security, and OWASP protections across {spec.project_name}.",
                "testing_agent": f"Selected to generate automated concurrency tests validating the {spec.concurrency_invariant_title} ({spec.concurrency_rule}).",
                "debugger_agent": f"Selected to analyze test execution traces, diagnose edge-case failures, and isolate root causes.",
                "repair_agent": f"Selected to apply precision code patches ensuring full regression compliance with acceptance criteria.",
                "deployment_agent": f"Selected to package {spec.project_name} into an isolated staging container with automated health probing."
            }

        # Build list of agent dictionaries
        for role_key in assigned_roles:
            meta = AVAILABLE_AGENTS.get(role_key)
            if not meta:
                continue
            reason = custom_reasons.get(role_key, f"Specialized {meta.role} selected to address domain requirements.")
            selected.append({
                "agent_id": meta.agent_id,
                "name": meta.name,
                "role": meta.role,
                "capabilities": meta.capabilities,
                "tools": meta.tools,
                "restrictions": meta.restrictions,
                "confidence": meta.default_confidence,
                "avatar_color": meta.avatar_color,
                "selection_reason": reason
            })

        return selected
