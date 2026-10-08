import logging
from typing import List, Dict, Any
from app.execution.workspace import ProjectWorkspace
from app.execution.domain_analyzer import analyze_user_prompt, DomainSpec

logger = logging.getLogger("forgeswarm.dynamic_generator")

class DynamicCodeGenerator:
    @classmethod
    def generate_project(cls, workspace: ProjectWorkspace, user_requirement: str, has_bug: bool = True) -> List[str]:
        """
        Dynamically generates a full-stack application (FastAPI + SQLAlchemy + UI + Pytest Suite)
        tailored directly to the user's software requirement and domain.
        """
        workspace.initialize()
        spec: DomainSpec = analyze_user_prompt(user_requirement)

        item_cls = spec.item_singular.capitalize()
        alloc_cls = f"{item_cls}Allocation"
        
        # 1. requirements.txt
        workspace.write_file("requirements.txt", """fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.35
pydantic>=2.9.0
pytest>=8.3.0
httpx>=0.27.0
""")

        # 2. Dockerfile
        workspace.write_file("Dockerfile", """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8005
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
""")

        # 3. app/database.py
        workspace.write_file("app/database.py", f"""from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app_{spec.item_singular}.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={{"check_same_thread": False}}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

        # 4. app/models.py
        if not has_bug:
            table_args_str = f"__table_args__ = (UniqueConstraint('{spec.item_singular}_id', 'slot_time', name='uix_{spec.item_singular}_slot'),)"
            constraint_import = "from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint"
        else:
            table_args_str = "__table_args__ = ()"
            constraint_import = "from sqlalchemy import Column, Integer, String, DateTime, ForeignKey"

        workspace.write_file("app/models.py", f"""{constraint_import}
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    allocations = relationship("{alloc_cls}", back_populates="user")

class {item_cls}(Base):
    __tablename__ = "{spec.item_plural}"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    {spec.item_attr1_name} = Column(String(100), nullable=False)
    {spec.item_attr2_name} = Column(String(100), nullable=False)
    allocations = relationship("{alloc_cls}", back_populates="{spec.item_singular}")

class {alloc_cls}(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True, index=True)
    {spec.item_singular}_id = Column(Integer, ForeignKey("{spec.item_plural}.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    slot_time = Column(String(50), nullable=False)
    notes = Column(String(255), default="Standard allocation")
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    {spec.item_singular} = relationship("{item_cls}", back_populates="allocations")
    user = relationship("User", back_populates="allocations")
    {table_args_str}
""")

        # 5. app/services/allocation_service.py
        if has_bug:
            service_code = f"""import time
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import {alloc_cls}

logger = logging.getLogger("allocation_service")

def execute_allocation(db: Session, {spec.item_singular}_id: int, user_id: int, slot_time: str, notes: str):
    # VULNERABILITY (BR-001 VIOLATION): TOCTOU Race Condition
    # Check availability without atomic row lock or DB unique constraint
    existing = db.query({alloc_cls}).filter(
        {alloc_cls}.{spec.item_singular}_id == {spec.item_singular}_id,
        {alloc_cls}.slot_time == slot_time,
        {alloc_cls}.status == "ACTIVE"
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="{item_cls} slot already allocated")
        
    # Simulated IO latency allows interleaved concurrent execution
    time.sleep(0.04)
    
    record = {alloc_cls}(
        {spec.item_singular}_id={spec.item_singular}_id,
        user_id=user_id,
        slot_time=slot_time,
        notes=notes,
        status="ACTIVE"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
"""
        else:
            service_code = f"""import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import {alloc_cls}

logger = logging.getLogger("allocation_service")

# Thread-safe in-memory reservation lock for ACID concurrency invariant
import threading
_allocation_lock = threading.Lock()

def execute_allocation(db: Session, {spec.item_singular}_id: int, user_id: int, slot_time: str, notes: str):
    # REPAIRED: Atomic synchronization and uniqueness protection against race conditions
    with _allocation_lock:
        existing = db.query({alloc_cls}).filter(
            {alloc_cls}.{spec.item_singular}_id == {spec.item_singular}_id,
            {alloc_cls}.slot_time == slot_time,
            {alloc_cls}.status == "ACTIVE"
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="{item_cls} slot already allocated")
            
        try:
            record = {alloc_cls}(
                {spec.item_singular}_id={spec.item_singular}_id,
                user_id=user_id,
                slot_time=slot_time,
                notes=notes,
                status="ACTIVE"
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Concurrent allocation conflict: slot taken")
"""
        workspace.write_file("app/services/allocation_service.py", service_code)

        # 6. Seed Items Code Generation
        seed_lines = []
        for s in spec.seed_items:
            seed_lines.append(f'            {item_cls}(name="{s["name"]}", {spec.item_attr1_name}="{s["attr1"]}", {spec.item_attr2_name}="{s["attr2"]}"),')
        seeds_str = "\n".join(seed_lines)

        # 7. app/main.py
        workspace.write_file("app/main.py", f"""import hashlib
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import User, {item_cls}, {alloc_cls}
from app.services.allocation_service import execute_allocation

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{spec.project_name}",
    version="1.0.0",
    description="Engineered by ForgeSwarm Autonomous Engineering Swarm"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed initial {spec.item_plural} if empty
def seed_catalog():
    db = next(get_db())
    if db.query({item_cls}).count() == 0:
        items = [
{seeds_str}
        ]
        db.add_all(items)
        db.commit()
    db.close()

seed_catalog()

# Schemas
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AllocationRequest(BaseModel):
    {spec.item_singular}_id: int
    slot_time: str
    notes: Optional[str] = "Standard allocation request"

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication token required (SEC-001)")
    token = authorization.split(" ")[1]
    user = db.query(User).filter(User.email == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user

@app.get("/health")
def health():
    return {{"status": "HEALTHY", "system": "{spec.project_name}", "domain": "{spec.domain}", "version": "1.0.0"}}

@app.post("/api/auth/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Account with this email already exists")
    user = User(name=req.name, email=req.email, password_hash=hash_pw(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {{"token": user.email, "user": {{"id": user.id, "name": user.name, "email": user.email}}}}

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email, User.password_hash == hash_pw(req.password)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {{"token": user.email, "user": {{"id": user.id, "name": user.name, "email": user.email}}}}

@app.get("/api/{spec.item_plural}")
def list_{spec.item_plural}(db: Session = Depends(get_db)):
    items = db.query({item_cls}).all()
    return [
        {{"id": i.id, "name": i.name, "{spec.item_attr1_name}": getattr(i, "{spec.item_attr1_name}"), "{spec.item_attr2_name}": getattr(i, "{spec.item_attr2_name}")}}
        for i in items
    ]

# Backward compatibility alias
@app.get("/api/doctors")
def list_doctors_alias(db: Session = Depends(get_db)):
    return list_{spec.item_plural}(db)

@app.get("/api/{spec.item_plural}/{{{spec.item_singular}_id}}/slots")
def get_{spec.item_singular}_slots({spec.item_singular}_id: int, date: str = "2026-10-15", db: Session = Depends(get_db)):
    item = db.query({item_cls}).filter({item_cls}.id == {spec.item_singular}_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{item_cls} not found")
        
    all_slots = [
        f"{{date}} Slot 1 (09:00 AM)", f"{{date}} Slot 2 (10:00 AM)", f"{{date}} Slot 3 (11:00 AM)",
        f"{{date}} Slot 4 (01:00 PM)", f"{{date}} Slot 5 (02:00 PM)", f"{{date}} Slot 6 (03:00 PM)"
    ]
    
    allocated = db.query({alloc_cls}.slot_time).filter(
        {alloc_cls}.{spec.item_singular}_id == {spec.item_singular}_id,
        {alloc_cls}.status == "ACTIVE"
    ).all()
    allocated_times = {{a[0] for a in allocated}}
    
    return [
        {{"slot": slot, "available": slot not in allocated_times}}
        for slot in all_slots
    ]

@app.post("/api/allocations", status_code=201)
def create_allocation(req: AllocationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query({item_cls}).filter({item_cls}.id == req.{spec.item_singular}_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{item_cls} not found")
    rec = execute_allocation(db, req.{spec.item_singular}_id, user.id, req.slot_time, req.notes)
    return {{
        "id": rec.id,
        "{spec.item_singular}_id": rec.{spec.item_singular}_id,
        "item_name": item.name,
        "slot_time": rec.slot_time,
        "notes": rec.notes,
        "status": rec.status
    }}

# Backward-compat alias for appointments endpoint
@app.post("/api/appointments", status_code=201)
def create_appointment_alias(req: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target_id = req.get("{spec.item_singular}_id") or req.get("doctor_id") or 1
    slot = req.get("slot_time") or req.get("appointment_time") or "2026-10-15 Slot 1 (09:00 AM)"
    notes = req.get("notes") or req.get("reason") or "Standard request"
    alloc_req = AllocationRequest({spec.item_singular}_id=target_id, slot_time=slot, notes=notes)
    return create_allocation(alloc_req, user, db)

@app.get("/api/allocations")
def list_allocations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query({alloc_cls}).filter({alloc_cls}.user_id == user.id).all()
    result = []
    for r in records:
        result.append({{
            "id": r.id,
            "{spec.item_singular}_id": r.{spec.item_singular}_id,
            "item_name": r.{spec.item_singular}.name if r.{spec.item_singular} else "Item",
            "slot_time": r.slot_time,
            "notes": r.notes,
            "status": r.status
        }})
    return result

@app.get("/api/appointments")
def list_appointments_alias(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_allocations(user, db)

@app.delete("/api/allocations/{{allocation_id}}")
def cancel_allocation(allocation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query({alloc_cls}).filter(
        {alloc_cls}.id == allocation_id,
        {alloc_cls}.user_id == user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Allocation not found or not owned by user")
    record.status = "CANCELLED"
    db.commit()
    return {{"message": "Allocation successfully released", "status": "CANCELLED"}}

@app.delete("/api/appointments/{{appointment_id}}")
def cancel_appointment_alias(appointment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cancel_allocation(appointment_id, user, db)

@app.get("/", response_class=HTMLResponse)
def index_page():
    return \"\"\"<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{spec.project_name} — Generated by ForgeSwarm</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ background: #0B1120; color: #F8FAFC; font-family: system-ui, sans-serif; }}
  </style>
</head>
<body class="p-6 max-w-5xl mx-auto">
  <header class="border-b border-slate-700 pb-4 mb-6 flex justify-between items-center">
    <div>
      <div class="flex items-center space-x-2">
        <span class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></span>
        <h1 class="text-2xl font-bold text-white tracking-tight">{spec.project_name}</h1>
      </div>
      <p class="text-sm text-slate-400 mt-1">Domain: <span class="text-cyan-400 font-semibold">{spec.domain}</span> | Engineered by <span class="text-cyan-300 font-semibold">ForgeSwarm</span></p>
    </div>
    <div id="auth-status" class="text-right text-xs text-slate-400">Not authenticated</div>
  </header>

  <div id="app-container" class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Auth Card -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-cyan-400 mb-3" id="auth-title">User Authentication</h2>
      <div id="auth-form" class="space-y-2">
        <input id="name-input" type="text" placeholder="Full Name" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white" value="Jordan Hayes">
        <input id="email-input" type="email" placeholder="Email Address" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white" value="jordan@example.com">
        <input id="pass-input" type="password" placeholder="Password" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white" value="Secret123!">
        <div class="flex space-x-2 pt-1">
          <button onclick="handleRegister()" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold py-2 px-3 rounded transition">Register</button>
          <button onclick="handleLogin()" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white text-xs font-semibold py-2 px-3 rounded transition">Sign In</button>
        </div>
      </div>
      <div id="user-info" class="hidden">
        <p class="text-sm text-slate-300">Signed in as: <strong id="logged-user" class="text-emerald-400">Jordan</strong></p>
        <button onclick="handleLogout()" class="mt-3 text-xs bg-rose-900/60 hover:bg-rose-800 text-rose-200 px-3 py-1.5 rounded">Sign Out</button>
      </div>
      <div id="auth-alert" class="mt-3 text-xs p-2 rounded hidden"></div>
    </div>

    <!-- Catalog & Slot Selection -->
    <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-cyan-400 mb-3">Available {spec.item_plural.capitalize()} Catalog</h2>
      <div id="item-list" class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div class="text-xs text-slate-500">Loading catalog...</div>
      </div>

      <div id="slot-container" class="mt-4 pt-4 border-t border-slate-800 hidden">
        <h3 class="text-sm font-semibold text-slate-200 mb-2">Select Allocation Slot for <span id="selected-item-name" class="text-cyan-300"></span></h3>
        <div id="slot-buttons" class="grid grid-cols-2 sm:grid-cols-3 gap-2"></div>
        <div class="mt-4 flex space-x-2">
          <input id="notes-input" type="text" placeholder="Notes / Purpose" class="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-xs text-white" value="Standard {spec.action_name}">
          <button onclick="bookSelectedSlot()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded transition">Confirm {spec.action_name.capitalize()}</button>
        </div>
        <div id="booking-alert" class="mt-3 text-xs p-2 rounded hidden"></div>
      </div>
    </div>
  </div>

  <!-- User Allocations History -->
  <div class="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg font-semibold text-cyan-400">My Active {spec.action_past.capitalize()} Records (FR-006 Traceability)</h2>
      <button onclick="fetchAllocations()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded">Refresh</button>
    </div>
    <div id="allocations-list" class="divide-y divide-slate-800 text-sm">
      <div class="text-xs text-slate-500 py-2">No active records or not signed in.</div>
    </div>
  </div>

  <script>
    let currentToken = null;
    let selectedItemId = null;
    let selectedSlot = null;

    async function handleRegister() {{
      const name = document.getElementById('name-input').value;
      const email = document.getElementById('email-input').value;
      const password = document.getElementById('pass-input').value;
      try {{
        const res = await fetch('/api/auth/register', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{name, email, password}})
        }});
        const data = await res.json();
        if (res.ok) {{
          currentToken = data.token;
          onAuthSuccess(data.user.name);
          showAlert('auth-alert', 'Registered successfully!', 'emerald');
        }} else {{
          showAlert('auth-alert', data.detail || 'Registration failed', 'rose');
        }}
      }} catch (err) {{
        showAlert('auth-alert', 'Network error', 'rose');
      }}
    }}

    async function handleLogin() {{
      const email = document.getElementById('email-input').value;
      const password = document.getElementById('pass-input').value;
      try {{
        const res = await fetch('/api/auth/login', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{email, password}})
        }});
        const data = await res.json();
        if (res.ok) {{
          currentToken = data.token;
          onAuthSuccess(data.user.name);
          showAlert('auth-alert', 'Signed in successfully!', 'emerald');
        }} else {{
          showAlert('auth-alert', data.detail || 'Login failed', 'rose');
        }}
      }} catch (err) {{
        showAlert('auth-alert', 'Network error', 'rose');
      }}
    }}

    function onAuthSuccess(userName) {{
      document.getElementById('auth-form').classList.add('hidden');
      document.getElementById('user-info').classList.remove('hidden');
      document.getElementById('logged-user').innerText = userName;
      document.getElementById('auth-status').innerText = 'Authenticated (' + userName + ')';
      fetchAllocations();
    }}

    function handleLogout() {{
      currentToken = null;
      document.getElementById('auth-form').classList.remove('hidden');
      document.getElementById('user-info').classList.add('hidden');
      document.getElementById('auth-status').innerText = 'Not authenticated';
      document.getElementById('allocations-list').innerHTML = '<div class="text-xs text-slate-500 py-2">Signed out.</div>';
    }}

    function showAlert(elemId, msg, color) {{
      const el = document.getElementById(elemId);
      el.className = `mt-3 text-xs p-2 rounded bg-${{color}}-900/50 text-${{color}}-200 border border-${{color}}-700 block`;
      el.innerText = msg;
    }}

    async function fetchItems() {{
      const res = await fetch('/api/{spec.item_plural}');
      const items = await res.json();
      const container = document.getElementById('item-list');
      container.innerHTML = items.map(i => `
        <div onclick="selectItem(${{i.id}}, '${{i.name}}')" class="p-3 bg-slate-800/80 hover:bg-slate-700/80 cursor-pointer rounded-lg border border-slate-700 transition">
          <div class="font-medium text-white text-sm">${{i.name}}</div>
          <div class="text-xs text-cyan-400 mt-0.5">${{i.{spec.item_attr1_name}}}</div>
          <div class="text-xs text-slate-400 mt-1">${{i.{spec.item_attr2_name}}}</div>
        </div>
      `).join('');
    }}

    async function selectItem(id, name) {{
      selectedItemId = id;
      document.getElementById('selected-item-name').innerText = name;
      document.getElementById('slot-container').classList.remove('hidden');
      
      const res = await fetch(`/api/{spec.item_plural}/${{id}}/slots`);
      const slots = await res.json();
      const container = document.getElementById('slot-buttons');
      container.innerHTML = slots.map(s => `
        <button onclick="chooseSlot('${{s.slot}}')" class="text-xs p-2 rounded border text-center transition ${{
          s.available ? 'bg-slate-800 hover:bg-cyan-900 border-slate-700 text-slate-200' : 'bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed opacity-50'
        }}" ${{!s.available ? 'disabled' : ''}}>
          ${{s.slot}}
        </button>
      `).join('');
    }}

    function chooseSlot(slot) {{
      selectedSlot = slot;
      showAlert('booking-alert', 'Selected: ' + slot, 'cyan');
    }}

    async function bookSelectedSlot() {{
      if (!currentToken) {{
        alert('Please register or sign in first!');
        return;
      }}
      if (!selectedItemId || !selectedSlot) {{
        alert('Please select an item and available slot');
        return;
      }}
      const notes = document.getElementById('notes-input').value;
      try {{
        const res = await fetch('/api/allocations', {{
          method: 'POST',
          headers: {{
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + currentToken
          }},
          body: JSON.stringify({{
            {spec.item_singular}_id: selectedItemId,
            slot_time: selectedSlot,
            notes: notes
          }})
        }});
        const data = await res.json();
        if (res.ok) {{
          showAlert('booking-alert', 'Confirmed allocation #' + data.id + ' for ' + data.slot_time, 'emerald');
          fetchAllocations();
          selectItem(selectedItemId, document.getElementById('selected-item-name').innerText);
        }} else {{
          showAlert('booking-alert', 'Conflict Error: ' + (data.detail || 'Slot Conflict'), 'rose');
        }}
      }} catch (err) {{
        showAlert('booking-alert', 'Network error during reservation', 'rose');
      }}
    }}

    async function fetchAllocations() {{
      if (!currentToken) return;
      const res = await fetch('/api/allocations', {{
        headers: {{'Authorization': 'Bearer ' + currentToken}}
      }});
      const data = await res.json();
      const container = document.getElementById('allocations-list');
      if (data.length === 0) {{
        container.innerHTML = '<div class="text-xs text-slate-500 py-2">No active records.</div>';
        return;
      }}
      container.innerHTML = data.map(a => `
        <div class="py-2.5 flex justify-between items-center">
          <div>
            <span class="font-medium text-white">${{a.item_name}}</span>
            <span class="text-xs text-slate-400 ml-2">${{a.slot_time}}</span>
            <span class="text-xs px-2 py-0.5 rounded ml-2 ${{a.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'}}">${{a.status}}</span>
          </div>
          ${{a.status === 'ACTIVE' ? `<button onclick="cancelAlloc(${{a.id}})" class="text-xs bg-rose-900/50 hover:bg-rose-800 border border-rose-700 text-rose-200 px-2.5 py-1 rounded">{spec.action_reverse.capitalize()}</button>` : ''}}
        </div>
      `).join('');
    }}

    async function cancelAlloc(id) {{
      const res = await fetch(`/api/allocations/${{id}}`, {{
        method: 'DELETE',
        headers: {{'Authorization': 'Bearer ' + currentToken}}
      }});
      if (res.ok) {{
        fetchAllocations();
        if (selectedItemId) {{
          selectItem(selectedItemId, document.getElementById('selected-item-name').innerText);
        }}
      }}
    }}

    fetchItems();
  </script>
</body>
</html>\"\"\"
""")

        # 8. tests/test_suite.py (17 Requirement-Based Tests mapped to user domain)
        workspace.write_file("tests/test_suite.py", f"""import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

# --- FR-001: User Registration & Auth ---
def test_fr_001_user_registration_success():
    resp = client.post("/api/auth/register", json={{
        "name": "Alex Vance",
        "email": "alex.vance@swarm-test.org",
        "password": "SecurePassword123!"
    }})
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "alex.vance@swarm-test.org"

def test_fr_001_duplicate_registration_rejection():
    resp = client.post("/api/auth/register", json={{
        "name": "Duplicate User",
        "email": "alex.vance@swarm-test.org",
        "password": "AnotherPassword!"
    }})
    assert resp.status_code == 400

def test_fr_001_login_valid_credentials():
    resp = client.post("/api/auth/login", json={{
        "email": "alex.vance@swarm-test.org",
        "password": "SecurePassword123!"
    }})
    assert resp.status_code == 200
    assert "token" in resp.json()

def test_fr_001_login_invalid_password():
    resp = client.post("/api/auth/login", json={{
        "email": "alex.vance@swarm-test.org",
        "password": "WrongPassword!"
    }})
    assert resp.status_code == 401

# --- FR-002: Catalog Listing ---
def test_fr_002_list_items():
    resp = client.get("/api/{spec.item_plural}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 4

# --- FR-003: Slot Availability Inspection ---
def test_fr_003_available_slots_retrieval():
    resp = client.get("/api/{spec.item_plural}/1/slots")
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) > 0
    assert any(s["available"] is True for s in slots)

# --- SEC-001: Unauthenticated Allocation Blocked ---
def test_sec_001_unauthenticated_allocation_blocked():
    resp = client.post("/api/allocations", json={{
        "{spec.item_singular}_id": 1,
        "slot_time": "2026-10-15 Slot 1 (09:00 AM)",
        "notes": "Test"
    }})
    assert resp.status_code == 401

# --- FR-004: Authenticated Allocation Success ---
def test_fr_004_authenticated_allocation_success():
    resp = client.post("/api/allocations", 
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}},
        json={{
            "{spec.item_singular}_id": 1,
            "slot_time": "2026-10-15 Slot 1 (09:00 AM)",
            "notes": "Priority Reservation"
        }}
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "ACTIVE"

def test_fr_003_slot_status_updated_after_allocation():
    resp = client.get("/api/{spec.item_plural}/1/slots")
    slots = resp.json()
    booked = next(s for s in slots if s["slot"] == "2026-10-15 Slot 1 (09:00 AM)")
    assert booked["available"] is False

# --- FR-005: Release / Cancellation Workflow ---
def test_fr_005_cancellation_workflow():
    alloc_resp = client.post("/api/allocations", 
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}},
        json={{
            "{spec.item_singular}_id": 2,
            "slot_time": "2026-10-15 Slot 4 (01:00 PM)",
            "notes": "Temporary"
        }}
    )
    alloc_id = alloc_resp.json()["id"]
    
    cancel_resp = client.delete(f"/api/allocations/{{alloc_id}}",
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}}
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

def test_fr_005_slot_reopened_after_cancellation():
    resp = client.get("/api/{spec.item_plural}/2/slots")
    slots = resp.json()
    reopened = next(s for s in slots if s["slot"] == "2026-10-15 Slot 4 (01:00 PM)")
    assert reopened["available"] is True

# --- FR-006: User Allocation History ---
def test_fr_006_user_allocation_history():
    resp = client.get("/api/allocations",
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}}
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

# --- SEC-002: Password Hashing Verification ---
def test_sec_002_password_not_stored_plaintext():
    from app.models import User
    from app.database import SessionLocal
    db = SessionLocal()
    user = db.query(User).filter(User.email == "alex.vance@swarm-test.org").first()
    assert user.password_hash != "SecurePassword123!"
    assert len(user.password_hash) == 64
    db.close()

# --- Boundary & Reliability Tests ---
def test_fr_004_nonexistent_item_rejection():
    resp = client.post("/api/allocations", 
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}},
        json={{
            "{spec.item_singular}_id": 99999,
            "slot_time": "2026-10-15 Slot 1 (09:00 AM)"
        }}
    )
    assert resp.status_code == 404

def test_fr_005_cancel_unauthorized_allocation_fails():
    resp = client.delete("/api/allocations/99999",
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}}
    )
    assert resp.status_code == 404

def test_health_check_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

# --- BR-001: CONCURRENCY INVARIANT PROBE ---
def test_br_001_concurrency_invariant_prevention():
    \"\"\"
    CRITICAL ACCEPTANCE TEST ({spec.concurrency_invariant_title}):
    Given two users attempt to allocate the exact same {spec.item_singular} and slot simultaneously:
    EXPECTED: Exactly ONE succeeds (HTTP 201), the second MUST FAIL safely (HTTP 409 Conflict).
    \"\"\"
    client.post("/api/auth/register", json={{"name": "User Alpha", "email": "alpha.concurrency@test.com", "password": "pass"}})
    client.post("/api/auth/register", json={{"name": "User Beta", "email": "beta.concurrency@test.com", "password": "pass"}})

    target_slot = "2026-10-15 Slot 2 (10:00 AM)"
    target_item_id = 1

    results = []

    def make_allocation(email):
        local_client = TestClient(app)
        res = local_client.post("/api/allocations",
            headers={{"Authorization": f"Bearer {{email}}"}},
            json={{
                "{spec.item_singular}_id": target_item_id,
                "slot_time": target_slot,
                "notes": f"Concurrent allocation probe from {{email}}"
            }}
        )
        return res.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(make_allocation, "alpha.concurrency@test.com")
        f2 = executor.submit(make_allocation, "beta.concurrency@test.com")
        results = [f1.result(), f2.result()]

    successes = results.count(201)
    conflicts = results.count(409)

    # In the defective version, BOTH requests will return 201 (successes == 2), which fails this assertion!
    # In the repaired version, exactly one is 201 and the other is 409.
    assert successes == 1, f"BR-001 VIOLATION: Expected 1 booking success, got {{successes}}. Status codes: {{results}}"
    assert conflicts == 1, f"Expected 1 conflict rejection (409), got {{conflicts}}."
""")

        return workspace.list_files()
