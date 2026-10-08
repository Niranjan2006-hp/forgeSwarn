# ForgeSwarm — Autonomous AI Engineering Team

> **"Don't give AI a coding task. Give it a product requirement."**

ForgeSwarm is a multi-agent AI software engineering platform that transforms high-level natural language requirements into tested, verified, and deployable applications. Unlike standard coding assistants that abandon the user the moment a race condition or syntax defect emerges, ForgeSwarm operates like an autonomous software engineering organization.

---

## 🌟 Core Innovation: The Closed Engineering Loop

```
REQUIREMENT ANALYSIS
         │
         ▼
ENGINEERING CONTRACT (Acceptance Criteria & Invariants)
         │
         ▼
DYNAMIC TEAM FORMATION (Explainable Capability Selection)
         │
         ▼
SYSTEM ARCHITECTURE (Schema, REST Specs, ACID Boundaries)
         │
         ▼
CODE DEVELOPMENT (FastAPI, React, SQLAlchemy)
         │
         ▼
REQUIREMENT-BASED TESTING (Concurrency Probes)
         │
         ▼
FAILURE DETECTION ──► ROOT CAUSE DIAGNOSIS (TOCTOU Race Condition)
                             │
                             ▼
                      AUTONOMOUS SURGICAL REPAIR (Locking & Uniqueness)
                             │
                             ▼
                      FULL REGRESSION VERIFICATION (17/17 Passed)
                             │
                             ▼
                      SECURITY AUDIT GATE (Secrets, Auth, SQLi)
                             │
                             ▼
                      STAGING SANDBOX DEPLOYMENT & HEALTH CHECKS
```

---

## 🏥 Main Demonstration: Hospital Appointment Management System

### User Requirement:
> *"Build a hospital appointment platform where patients can register, view doctors, check available appointment slots, book appointments, and cancel appointments. A doctor must never have two patients booked for the same time slot."*

### Autonomous Execution Summary:
1. **Understand & Formalize**:
   - Decomposed into **6 Functional Requirements** (`FR-001` to `FR-006`), **3 Business Rules** (`BR-001` to `BR-003`), and **3 Security Invariants** (`SEC-001` to `SEC-003`).
   - Established strict acceptance criteria in the **Engineering Contract** (`engineering_contract.json`).
2. **Dynamically Form Swarm**:
   - **Requirements Analyst**, **Chief Architect**, **Database Engineer**, **Backend Engineer**, **Frontend Engineer**, **AppSec Officer**, **QA Automation Lead**, **Debugger Lead**, **Repair Specialist**, and **DevOps Engineer**.
   - Explainable reasoning logged for each agent.
3. **Architecture & Initial Build**:
   - Synthesized REST endpoints and SQLite/PostgreSQL schemas with explicit transactional requirements.
   - Built full-stack application with interactive patient booking portal.
4. **Deliberate Failure & Detection**:
   - Concurrency probe simulated two simultaneous bookings for Dr. Sharma at 10:00 AM.
   - Initial code used a non-atomic availability check (`SELECT` then `INSERT`).
   - Testing Swarm caught the invariant violation: **FAILURE DETECTED on TC-BR-001**.
5. **Diagnostic Root Cause Analysis**:
   - **Debugger Agent** diagnosed a Time-Of-Check to Time-Of-Use (TOCTOU) race condition with stack traces and evidence.
6. **Surgical Self-Repair**:
   - **Repair Agent** applied thread-safe reservation locking and composite uniqueness constraint on `(doctor_id, appointment_time)`.
7. **Regression Verification**:
   - Full regression suite re-executed: **17 / 17 tests passed (100% green)**.
8. **Security Gate & Deployment**:
   - Static AST audit verified zero hardcoded secrets, password hashing (`SEC-002`), and auth guards (`SEC-001`).
   - Staging deployed to local sandbox (`http://127.0.0.1:8005`).
   - Automated `/health` check and smoke tests passed!

---

## 🛠 Technology Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React, Recharts, Axios, React Router
- **Backend**: Python 3.12/3.14, FastAPI, SQLAlchemy 2.0, Pydantic 2.0, HTTPX, Pytest
- **Database**: SQLite (local staging/dev) / PostgreSQL (production)
- **AI Abstraction**: `LLMProvider` layer with `MockLLMProvider` (deterministic 100% offline demo mode) and `GeminiProvider` / `OpenAIProvider`.
- **Live Stream**: Server-Sent Events (SSE) and WebSockets for real-time dashboard events.

---

## 🚀 Quick Start Guide

### Prerequisites:
- Python 3.10+
- Node.js 18+

### 1. Launch All Services (Windows)
Double-click:
```bash
scripts\start_all.bat
```
Or run the backend and frontend in separate terminals:

#### Terminal 1 — Backend:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 — Frontend Dashboard:
```bash
cd frontend
npm run dev
```

Visit the Engineering Dashboard at:
👉 **`http://localhost:5173`**

---

### 2. Standalone CLI Verification
You can execute the entire closed engineering loop from the command line:
```bash
python scripts/run_demo.py
```

---

## 📊 Traceability Matrix

| Requirement | Category | Description | Test Case | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FR-001** | Functional | Patient registration & authentication | `TC-FR-001-01` | **VERIFIED** |
| **FR-002** | Functional | Clinical doctor directory | `TC-FR-002-01` | **VERIFIED** |
| **FR-003** | Functional | Real-time open slot inspection | `TC-FR-003-01` | **VERIFIED** |
| **FR-004** | Functional | Appointment slot booking | `TC-FR-004-01` | **VERIFIED** |
| **FR-005** | Functional | Appointment cancellation & slot release | `TC-FR-005-01` | **VERIFIED** |
| **FR-006** | Functional | Patient historical reservations | `TC-FR-006-01` | **VERIFIED** |
| **BR-001** | Business Rule | Zero Double-Booking Concurrency Invariant | `TC-BR-001-01` | **VERIFIED (REPAIRED)** |
| **SEC-001** | Security | Token authentication guard on appointments | `TC-SEC-001-01` | **VERIFIED** |
| **SEC-002** | Security | Cryptographic password hashing | `TC-SEC-002-01` | **VERIFIED** |

---

## 📁 Repository Structure

```
forgeswarm/
├── backend/
│   ├── app/
│   │   ├── api/            # REST API endpoints & SSE streaming
│   │   ├── agents/         # Capability registry & dynamic team formation
│   │   ├── orchestrator/   # State machine, event broadcaster & closed-loop engine
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── schemas/        # Pydantic serialization models
│   │   ├── execution/      # Workspace sandbox & hospital code generator
│   │   ├── testing/        # Pytest test automation runner
│   │   ├── security/       # AST security gate & vulnerability scanner
│   │   ├── deployment/     # Sandboxed staging process manager & health probes
│   │   ├── llm/            # LLM abstraction (Mock, Gemini, OpenAI)
│   │   ├── prompts/        # External prompt templates
│   │   └── core/           # Configuration & database sessions
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/     # PipelineTracker, AgentSwarm, SelfRepair, Traceability, Artifacts
│   │   ├── pages/          # LandingPage, CreateProjectPage, ProjectDashboard
│   │   └── services/       # Axios API client
│   └── package.json
├── generated_projects/     # Sandboxed outputs of engineered applications
├── scripts/                # Launchers & CLI demo runners
├── docs/                   # IMPLEMENTATION_PLAN.md & architectural specifications
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🏆 Key Achievements

- **Zero Fake UI**: All dashboard events, agent communications, test cases, and diffs come from real backend execution.
- **Real Application Generated**: A working hospital appointment platform with an interactive patient portal and REST API.
- **Genuine Closed-Loop Self-Repair**: Detects a race condition under concurrency, diagnoses the root cause, applies a surgical patch, and verifies regression pass rate.
- **Offline / Demo Resilience**: Operates in deterministic Demo Mode without requiring external API keys, while remaining fully compatible with live Gemini and OpenAI models.
