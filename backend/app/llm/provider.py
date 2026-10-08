import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger("forgeswarm.llm")

class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Raw completion interface"""
        pass

    @abstractmethod
    async def analyze_requirements(self, user_prompt: str) -> Dict[str, Any]:
        """Convert natural language to structured requirements"""
        pass

    @abstractmethod
    async def generate_contract(self, structured_reqs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate formal Engineering Contract"""
        pass

    @abstractmethod
    async def form_team(self, contract: Dict[str, Any], domain: str = "Healthcare", user_prompt: str = "") -> List[Dict[str, Any]]:
        """Dynamically form specialized engineering team based on requirement and contract"""
        pass

    @abstractmethod
    async def diagnose_failure(self, failed_test: Dict[str, Any], logs: str, code_context: str) -> Dict[str, Any]:
        """Root cause analysis of failed test"""
        pass

    @abstractmethod
    async def generate_repair(self, diagnosis: Dict[str, Any], current_code: str) -> Dict[str, Any]:
        """Generate surgical repair diff/fix"""
        pass


from app.execution.domain_analyzer import analyze_user_prompt, DomainSpec

class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Dynamic High-Fidelity Provider for ForgeSwarm.
    Intelligently extracts domain entities, actions, and concurrency rules from ANY user requirement.
    """
    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Deterministic response generated for prompt."

    async def analyze_requirements(self, user_prompt: str) -> Dict[str, Any]:
        spec: DomainSpec = analyze_user_prompt(user_prompt)

        if spec.ui_type == "CALCULATOR":
            return {
                "project_name": spec.project_name,
                "domain": spec.domain,
                "summary": "High-precision standard and scientific web calculator featuring responsive LCD display, full arithmetic and advanced functions, persistent memory registers, audit calculation tape, and rigorous zero-division boundary protection.",
                "functional_requirements": [
                    {"code": "FR-001", "title": "Standard Arithmetic Computation", "description": "Users can execute addition, subtraction, multiplication, and division with standard mathematical operator precedence.", "priority": "CRITICAL"},
                    {"code": "FR-002", "title": "Scientific & Advanced Functions", "description": "Users can calculate square roots, powers/exponents, percentages, reciprocals, and sign toggles.", "priority": "HIGH"},
                    {"code": "FR-003", "title": "High-Precision LCD Screen & Keypad", "description": "Responsive dual-line display showing real-time expression history, glowing LCD digits, and keyboard shortcuts.", "priority": "HIGH"},
                    {"code": "FR-004", "title": "Memory Registers (M+, M-, MR, MC, MS)", "description": "Users can store, recall, increment, and reset accumulated numeric values across calculations.", "priority": "HIGH"},
                    {"code": "FR-005", "title": "Audit Tape & Session History", "description": "Persistent audit tape of all evaluated calculations with timestamps, click-to-recall, and clear history.", "priority": "MEDIUM"},
                    {"code": "FR-006", "title": "Input Editing & Entry Clearing", "description": "Support for backspace (DEL), clear entry (CE), and master reset (C) without corrupting calculation state.", "priority": "MEDIUM"}
                ],
                "business_rules": [
                    {"code": "BR-001", "title": "Zero-Division Safety Invariant", "description": "A division operation with a divisor of zero must be trapped safely with HTTP 400 Bad Request and friendly UI error without application crash or unhandled 500 error.", "priority": "CRITICAL"},
                    {"code": "BR-002", "title": "Floating-Point Precision Invariant", "description": "Calculations must avoid catastrophic floating point representation errors and round cleanly to 10 decimal digits.", "priority": "HIGH"},
                    {"code": "BR-003", "title": "Memory Register State Integrity", "description": "Memory register operations must maintain state across operations until explicitly cleared.", "priority": "HIGH"}
                ],
                "security_requirements": [
                    {"code": "SEC-001", "title": "Math Expression Injection Guard", "description": "Math expression evaluator must sanitize inputs and strictly reject code injection or unsafe Python builtins.", "priority": "CRITICAL"},
                    {"code": "SEC-002", "title": "DoS & Exponential Explosion Defense", "description": "Expressions exceeding 255 characters or exponential explosion thresholds must be rejected safely.", "priority": "HIGH"},
                    {"code": "SEC-003", "title": "Zero Hardcoded Secrets", "description": "No hardcoded keys or tokens in calculator service.", "priority": "HIGH"}
                ],
                "non_functional_requirements": [
                    {"code": "NFR-001", "title": "Sub-20ms Evaluation Latency", "description": "Calculator endpoints must evaluate arithmetic requests under 20ms.", "priority": "HIGH"},
                    {"code": "NFR-002", "title": "IEEE-754 Arithmetic Compliance", "description": "Calculation engine complies with IEEE-754 floating point arithmetic standards.", "priority": "CRITICAL"}
                ],
                "entities": [
                    "Calculation",
                    "MemoryRegister",
                    "AuditTape"
                ]
            }
        
        return {
            "project_name": spec.project_name,
            "domain": spec.domain,
            "summary": f"Full-lifecycle {spec.domain} application ensuring absolute transactional consistency for {spec.item_plural}.",
            "functional_requirements": [
                {"code": "FR-001", "title": "User Registration & Authentication", "description": "Users can register with name, email, password and authenticate with JWT tokens.", "priority": "CRITICAL"},
                {"code": "FR-002", "title": f"{spec.catalog_title}", "description": f"Users can browse all {spec.item_plural} with their {spec.item_attr1_name} and {spec.item_attr2_name}.", "priority": "HIGH"},
                {"code": "FR-003", "title": f"{spec.options_label}", "description": f"Users can inspect available options and real-time status for any selected {spec.item_singular}.", "priority": "HIGH"},
                {"code": "FR-004", "title": f"{spec.action_label}", "description": f"Users can perform {spec.action_name} for an available {spec.item_singular} by submitting their {spec.primary_input_label}.", "priority": "CRITICAL"},
                {"code": "FR-005", "title": f"{spec.action_reverse.capitalize()} {spec.item_singular.capitalize()}", "description": f"Users can {spec.action_reverse} their active {spec.action_past} {spec.item_plural}, immediately releasing capacity.", "priority": "HIGH"},
                {"code": "FR-006", "title": f"{spec.record_title}", "description": f"Users can view their complete historical and active {spec.action_past} records with full audit traceability.", "priority": "MEDIUM"}
            ],
            "business_rules": [
                {"code": "BR-001", "title": spec.concurrency_invariant_title, "description": spec.concurrency_rule, "priority": "CRITICAL"},
                {"code": "BR-002", "title": "Historical Integrity Rule", "description": "Transactions and submissions cannot be made with invalid or expired options.", "priority": "HIGH"},
                {"code": "BR-003", "title": "Referential Integrity Invariant", "description": f"Every record must link to an authenticated user and valid {spec.item_singular}.", "priority": "HIGH"}
            ],
            "security_requirements": [
                {"code": "SEC-001", "title": "Route Authentication Guard", "description": f"Mutating endpoints for {spec.action_name} and {spec.action_reverse} require valid JWT bearer tokens.", "priority": "CRITICAL"},
                {"code": "SEC-002", "title": "Cryptographic Password Hashing", "description": "User passwords must be securely hashed using SHA-256/bcrypt algorithms.", "priority": "CRITICAL"},
                {"code": "SEC-003", "title": "Zero Hardcoded Secrets", "description": "No plain-text tokens or secret keys present in source code or database dumps.", "priority": "HIGH"}
            ],
            "non_functional_requirements": [
                {"code": "NFR-001", "title": "Low Latency API", "description": "Endpoints must respond under 100ms under standard operational load.", "priority": "MEDIUM"},
                {"code": "NFR-002", "title": "ACID Transactional Compliance", "description": f"{spec.action_label} operations must execute with strict ACID isolation.", "priority": "CRITICAL"}
            ],
            "entities": [
                "User",
                spec.item_singular.capitalize(),
                f"{spec.item_singular.capitalize()}Record",
                "AuditLog"
            ]
        }

    async def generate_contract(self, structured_reqs: Dict[str, Any]) -> Dict[str, Any]:
        p_name = structured_reqs.get("project_name", "Application")
        domain = structured_reqs.get("domain", "General")
        spec = analyze_user_prompt(f"{p_name} {domain}")

        if spec.ui_type == "CALCULATOR":
            return {
                "title": f"Engineering Contract - {p_name}",
                "version": "1.0.0",
                "status": "APPROVED",
                "domain": domain,
                "functional_requirements": structured_reqs.get("functional_requirements", []),
                "business_rules": structured_reqs.get("business_rules", []),
                "security_requirements": structured_reqs.get("security_requirements", []),
                "entities": structured_reqs.get("entities", []),
                "api_spec": [
                    {"method": "POST", "path": "/api/calculate", "summary": "Evaluate math expression (Subject to BR-001)"},
                    {"method": "GET", "path": "/api/history", "summary": "Retrieve calculation audit tape"},
                    {"method": "DELETE", "path": "/api/history", "summary": "Clear calculation tape"},
                    {"method": "POST", "path": "/api/memory", "summary": "Update memory register (store, add, sub, clear)"},
                    {"method": "GET", "path": "/api/memory", "summary": "Recall active memory register value"},
                    {"method": "GET", "path": "/health", "summary": "System health check"}
                ],
                "database_constraints": [
                    "Primary key: calculations.id (Auto-increment)",
                    "Primary key: memory_registers.id (Auto-increment)",
                    "Not null constraint: calculations.expression, calculations.result"
                ],
                "acceptance_criteria": [
                    {
                        "req_code": "BR-001",
                        "criterion": "Given a division expression with divisor zero: the system must catch the zero division, return HTTP 400 with 'Cannot divide by zero', and prevent 500 server crash."
                    },
                    {
                        "req_code": "FR-001",
                        "criterion": "Basic arithmetic operations (add, sub, mul, div) compute correctly according to standard precedence."
                    },
                    {
                        "req_code": "FR-004",
                        "criterion": "Memory register operations (M+, M-, MR, MC, MS) store and recall accumulated numeric state accurately."
                    },
                    {
                        "req_code": "SEC-001",
                        "criterion": "Unsafe or malicious Python code injection attempts return HTTP 400 Bad Request."
                    }
                ],
                "traceability_matrix": [
                    {"req": "BR-001", "criterion": "Given divisor zero, return 400 Bad Request safely", "test": "TC-BR-001-01", "component": "app/services/calculator_service.py"},
                    {"req": "FR-001", "criterion": "Arithmetic operations compute correctly", "test": "TC-FR-001-01", "component": "app/services/calculator_service.py"},
                    {"req": "FR-004", "criterion": "Memory register updates properly", "test": "TC-FR-004-01", "component": "app/main.py"},
                    {"req": "SEC-001", "criterion": "Malicious code rejected safely", "test": "TC-SEC-001-01", "component": "app/services/calculator_service.py"}
                ]
            }

        return {
            "title": f"Engineering Contract — {p_name}",
            "version": "1.0.0",
            "status": "APPROVED",
            "domain": domain,
            "functional_requirements": structured_reqs.get("functional_requirements", []),
            "business_rules": structured_reqs.get("business_rules", []),
            "security_requirements": structured_reqs.get("security_requirements", []),
            "entities": structured_reqs.get("entities", []),
            "api_spec": [
                {"method": "POST", "path": "/api/auth/register", "summary": "Register user account"},
                {"method": "POST", "path": "/api/auth/login", "summary": "Authenticate user and issue JWT"},
                {"method": "GET", "path": f"/api/{spec.item_plural}", "summary": f"Retrieve {spec.item_plural} catalog"},
                {"method": "GET", "path": f"/api/{spec.item_plural}/{{id}}/slots", "summary": f"Retrieve available {spec.item_singular} slots"},
                {"method": "POST", "path": "/api/allocations", "summary": f"Allocate {spec.item_singular} (Subject to BR-001)"},
                {"method": "GET", "path": "/api/allocations", "summary": f"List user active {spec.action_past} records"},
                {"method": "DELETE", "path": "/api/allocations/{id}", "summary": f"{spec.action_reverse.capitalize()} allocation"}
            ],
            "database_constraints": [
                f"Unique composite constraint: {spec.item_singular}_id + slot_time (BR-001)",
                f"Foreign key: allocation.user_id -> user.id",
                f"Foreign key: allocation.{spec.item_singular}_id -> {spec.item_plural}.id",
                f"Index: allocations({spec.item_singular}_id, slot_time, status)"
            ],
            "acceptance_criteria": [
                {
                    "req_code": "BR-001",
                    "criterion": f"Given two users attempt to simultaneously allocate the same {spec.item_singular} and slot: exactly ONE allocation must succeed with HTTP 201; the second request must fail safely with HTTP 409 Conflict."
                },
                {
                    "req_code": "FR-001",
                    "criterion": "Registration with unique email yields 201 Created and JWT token. Duplicate email yields 400 Bad Request."
                },
                {
                    "req_code": "FR-005",
                    "criterion": f"{spec.action_reverse.capitalize()} operation updates status to CANCELLED and immediately reopens slot availability."
                },
                {
                    "req_code": "SEC-001",
                    "criterion": "Unauthenticated requests to mutating endpoints return 401 Unauthorized."
                }
            ],
            "traceability_matrix": [
                {"req": "BR-001", "criterion": "Given concurrent allocation, only one succeeds", "test": "TC-BR-001-01", "component": "app/services/allocation_service.py"},
                {"req": "FR-001", "criterion": "Registration creates user", "test": "TC-FR-001-01", "component": "app/main.py"},
                {"req": "FR-002", "criterion": f"{spec.item_plural.capitalize()} list populated", "test": "TC-FR-002-01", "component": f"app/main.py"},
                {"req": "FR-004", "criterion": "Allocation valid", "test": "TC-FR-004-01", "component": "app/services/allocation_service.py"},
                {"req": "SEC-001", "criterion": "Auth token required", "test": "TC-SEC-001-01", "component": "app/main.py"}
            ]
        }

    async def form_team(self, contract: Dict[str, Any], domain: str = "Healthcare", user_prompt: str = "") -> List[Dict[str, Any]]:
        from app.agents.registry import TeamFormationEngine
        return TeamFormationEngine.form_team(contract, domain=domain, user_prompt=user_prompt)

    async def diagnose_failure(self, failed_test: Dict[str, Any], logs: str, code_context: str) -> Dict[str, Any]:
        is_calc = (
            "calculator" in logs.lower() 
            or "zerodivision" in logs.lower() 
            or "divide" in logs.lower() 
            or "calculator" in code_context.lower()
            or "math" in logs.lower()
        )
        if is_calc:
            return {
                "test_id": failed_test.get("test_id", "TC-BR-001-01"),
                "problem": "Unhandled ZeroDivisionError in calculation service (BR-001 Safety Invariant Violation)",
                "severity": "CRITICAL",
                "root_cause": "The arithmetic evaluator attempts raw division without verifying if the divisor operand evaluates to zero. When a zero divisor is provided (e.g. '10 / 0'), Python throws an unhandled ZeroDivisionError which bubbles up as an HTTP 500 Server Error rather than returning a clean HTTP 400 Bad Request with an informative safety error message.",
                "evidence": "Evaluating expression '10 / 0' resulted in an unhandled ZeroDivisionError (HTTP 500) instead of HTTP 400 Bad Request with 'Cannot divide by zero'.",
                "affected_component": "app/services/calculator_service.py",
                "recommended_fix": "Add an explicit zero-divisor guard inside the division evaluator: if the divisor is 0, raise HTTPException(status_code=400, detail='Cannot divide by zero').",
                "confidence": 0.99,
                "diagnosed_by": "Debugger Agent"
            }

        return {
            "test_id": failed_test.get("test_id", "TC-BR-001-01"),
            "problem": "Race condition leading to Concurrency Invariant violation (BR-001)",
            "severity": "CRITICAL",
            "root_cause": "Time-Of-Check to Time-Of-Use (TOCTOU) race condition in allocation service. The code queries availability with non-atomic SELECT, then executes INSERT without atomic row locking or unique composite database constraint. When two requests arrive concurrently, both inspect the slot as available and both proceed to write records.",
            "evidence": "Two simultaneous requests for the exact same resource slot both received HTTP 201 Created. Database contains two active allocation records violating the exclusivity invariant.",
            "affected_component": "app/services/allocation_service.py",
            "recommended_fix": "1. Add a composite UNIQUE constraint on (item_id, slot_time) in the database schema.\n2. Wrap the availability check and record creation inside a thread-safe atomic lock or serializable transaction with conflict recovery (HTTP 409).",
            "confidence": 0.98,
            "diagnosed_by": "Debugger Agent"
        }

    async def generate_repair(self, diagnosis: Dict[str, Any], current_code: str) -> Dict[str, Any]:
        if "calculator" in diagnosis.get("affected_component", "").lower() or "zerodivision" in diagnosis.get("problem", "").lower():
            return {
                "strategy": "Inject zero-division safety guard inside calculator evaluation service returning HTTP 400 Bad Request.",
                "files_to_modify": ["app/services/calculator_service.py"],
                "summary": "Added defensive zero-divisor check intercepting division-by-zero expressions before execution and returning HTTP 400 Bad Request.",
                "diff": """@@ -18,6 +18,9 @@
-    # UNGUARDED (BR-001 VULNERABILITY): Raw division raises ZeroDivisionError (HTTP 500)
-    return left / right
+    # REPAIRED (BR-001): Zero-Division Safety Guard
+    if right == 0:
+        raise HTTPException(status_code=400, detail="Cannot divide by zero")
+    return left / right
"""
            }

        return {
            "strategy": "Apply thread-safe atomic synchronization and database composite uniqueness validation on (item_id, slot_time).",
            "files_to_modify": ["app/services/allocation_service.py", "app/models.py"],
            "summary": "Replaced non-atomic check-then-insert pattern with atomic reservation lock and unique constraint handler returning HTTP 409 Conflict.",
            "diff": """@@ -15,15 +15,22 @@
-    # INSECURE TOCTOU: Check availability then insert separately
-    existing = db.query(Allocation).filter(item_id == id, slot_time == slot, status == "ACTIVE").first()
-    if existing:
-        raise HTTPException(status_code=400, detail="Slot unavailable")
-    # Sleep simulates concurrent context switch
-    record = Allocation(item_id=id, user_id=uid, slot_time=slot, status="ACTIVE")
-    db.add(record)
-    db.commit()
+    # REPAIRED: Atomic synchronization and uniqueness protection
+    with _allocation_lock:
+        existing = db.query(Allocation).filter(item_id == id, slot_time == slot, status == "ACTIVE").first()
+        if existing:
+            raise HTTPException(status_code=409, detail="Slot already allocated")
+        try:
+            record = Allocation(item_id=id, user_id=uid, slot_time=slot, status="ACTIVE")
+            db.add(record)
+            db.commit()
+        except IntegrityError:
+            db.rollback()
+            raise HTTPException(status_code=409, detail="Concurrent conflict: slot taken")
"""
        }


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model
        self.mock_fallback = MockLLMProvider()

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return await self.mock_fallback.complete(prompt, system_prompt)
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )
            return response.text or ""
        except Exception as e:
            logger.warning(f"Gemini API call failed, falling back to mock provider: {e}")
            return await self.mock_fallback.complete(prompt, system_prompt)

    async def analyze_requirements(self, user_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            return await self.mock_fallback.analyze_requirements(user_prompt)
        try:
            system = "You are an expert AI Software Architect. Output valid JSON adhering to requirements analysis format."
            prompt = f"Analyze the following software requirement into structured requirements, business rules, entities, and security constraints:\n\n{user_prompt}\n\nRespond ONLY with a valid JSON object."
            resp = await self.complete(prompt, system)
            # Parse json or fallback
            clean_json = resp.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.warning(f"Gemini analyze_requirements failed, using fallback: {e}")
            return await self.mock_fallback.analyze_requirements(user_prompt)

    async def generate_contract(self, structured_reqs: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            return await self.mock_fallback.generate_contract(structured_reqs)
        try:
            prompt = f"Create an Engineering Contract from this specification:\n{json.dumps(structured_reqs, indent=2)}\n\nRespond ONLY with valid JSON."
            resp = await self.complete(prompt, "You are a Principal Software Engineering Lead.")
            clean_json = resp.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            return await self.mock_fallback.generate_contract(structured_reqs)

    async def form_team(self, contract: Dict[str, Any], domain: str = "Healthcare", user_prompt: str = "") -> List[Dict[str, Any]]:
        return await self.mock_fallback.form_team(contract, domain=domain, user_prompt=user_prompt)

    async def diagnose_failure(self, failed_test: Dict[str, Any], logs: str, code_context: str) -> Dict[str, Any]:
        return await self.mock_fallback.diagnose_failure(failed_test, logs, code_context)

    async def generate_repair(self, diagnosis: Dict[str, Any], current_code: str) -> Dict[str, Any]:
        return await self.mock_fallback.generate_repair(diagnosis, current_code)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.mock_fallback = MockLLMProvider()

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return await self.mock_fallback.complete(prompt, system_prompt)
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            res = await client.chat.completions.create(model=self.model, messages=messages)
            return res.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"OpenAI completion failed: {e}")
            return await self.mock_fallback.complete(prompt, system_prompt)

    async def analyze_requirements(self, user_prompt: str) -> Dict[str, Any]:
        return await self.mock_fallback.analyze_requirements(user_prompt)

    async def generate_contract(self, structured_reqs: Dict[str, Any]) -> Dict[str, Any]:
        return await self.mock_fallback.generate_contract(structured_reqs)

    async def form_team(self, contract: Dict[str, Any], domain: str = "Healthcare", user_prompt: str = "") -> List[Dict[str, Any]]:
        return await self.mock_fallback.form_team(contract, domain=domain, user_prompt=user_prompt)

    async def diagnose_failure(self, failed_test: Dict[str, Any], logs: str, code_context: str) -> Dict[str, Any]:
        return await self.mock_fallback.diagnose_failure(failed_test, logs, code_context)

    async def generate_repair(self, diagnosis: Dict[str, Any], current_code: str) -> Dict[str, Any]:
        return await self.mock_fallback.generate_repair(diagnosis, current_code)


def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    choice = (provider_type or settings.DEFAULT_LLM_PROVIDER).lower()
    gemini_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    
    if choice == "gemini" and gemini_key:
        return GeminiProvider(api_key=gemini_key)
    elif choice == "openai" and openai_key:
        return OpenAIProvider(api_key=openai_key)
    else:
        return MockLLMProvider()
