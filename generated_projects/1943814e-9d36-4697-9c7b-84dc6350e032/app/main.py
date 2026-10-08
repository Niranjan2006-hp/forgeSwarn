import hashlib
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import User, Doctor, DoctorAllocation
from app.services.allocation_service import execute_allocation

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hospital Appointment Management System",
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

# Seed initial doctors if empty
def seed_catalog():
    db = next(get_db())
    if db.query(Doctor).count() == 0:
        items = [
            Doctor(name="Dr. Priya Sharma", specialty="Cardiology", room="Suite 301"),
            Doctor(name="Dr. Marcus Vance", specialty="Neurology", room="Suite 405"),
            Doctor(name="Dr. Elena Rostova", specialty="Pediatrics", room="Suite 102"),
            Doctor(name="Dr. James Wilson", specialty="Orthopedics", room="Suite 204"),
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
    doctor_id: int
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
    return {"status": "HEALTHY", "system": "Hospital Appointment Management System", "domain": "Healthcare", "version": "1.0.0"}

@app.post("/api/auth/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Account with this email already exists")
    user = User(name=req.name, email=req.email, password_hash=hash_pw(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": user.email, "user": {"id": user.id, "name": user.name, "email": user.email}}

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email, User.password_hash == hash_pw(req.password)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": user.email, "user": {"id": user.id, "name": user.name, "email": user.email}}

@app.get("/api/doctors")
def list_doctors(db: Session = Depends(get_db)):
    items = db.query(Doctor).all()
    return [
        {"id": i.id, "name": i.name, "specialty": getattr(i, "specialty"), "room": getattr(i, "room")}
        for i in items
    ]

# Backward compatibility alias
@app.get("/api/doctors")
def list_doctors_alias(db: Session = Depends(get_db)):
    return list_doctors(db)

@app.get("/api/doctors/{doctor_id}/slots")
def get_doctor_slots(doctor_id: int, date: str = "2026-10-15", db: Session = Depends(get_db)):
    item = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    all_slots = [
        f"{date} Slot 1 (09:00 AM)", f"{date} Slot 2 (10:00 AM)", f"{date} Slot 3 (11:00 AM)",
        f"{date} Slot 4 (01:00 PM)", f"{date} Slot 5 (02:00 PM)", f"{date} Slot 6 (03:00 PM)"
    ]
    
    allocated = db.query(DoctorAllocation.slot_time).filter(
        DoctorAllocation.doctor_id == doctor_id,
        DoctorAllocation.status == "ACTIVE"
    ).all()
    allocated_times = {a[0] for a in allocated}
    
    return [
        {"slot": slot, "available": slot not in allocated_times}
        for slot in all_slots
    ]

@app.post("/api/allocations", status_code=201)
def create_allocation(req: AllocationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Doctor).filter(Doctor.id == req.doctor_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Doctor not found")
    rec = execute_allocation(db, req.doctor_id, user.id, req.slot_time, req.notes)
    return {
        "id": rec.id,
        "doctor_id": rec.doctor_id,
        "item_name": item.name,
        "slot_time": rec.slot_time,
        "notes": rec.notes,
        "status": rec.status
    }

# Backward-compat alias for appointments endpoint
@app.post("/api/appointments", status_code=201)
def create_appointment_alias(req: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target_id = req.get("doctor_id") or req.get("doctor_id") or 1
    slot = req.get("slot_time") or req.get("appointment_time") or "2026-10-15 Slot 1 (09:00 AM)"
    notes = req.get("notes") or req.get("reason") or "Standard request"
    alloc_req = AllocationRequest(doctor_id=target_id, slot_time=slot, notes=notes)
    return create_allocation(alloc_req, user, db)

@app.get("/api/allocations")
def list_allocations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(DoctorAllocation).filter(DoctorAllocation.user_id == user.id).all()
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "doctor_id": r.doctor_id,
            "item_name": r.doctor.name if r.doctor else "Item",
            "slot_time": r.slot_time,
            "notes": r.notes,
            "status": r.status
        })
    return result

@app.get("/api/appointments")
def list_appointments_alias(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_allocations(user, db)

@app.delete("/api/allocations/{allocation_id}")
def cancel_allocation(allocation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(DoctorAllocation).filter(
        DoctorAllocation.id == allocation_id,
        DoctorAllocation.user_id == user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Allocation not found or not owned by user")
    record.status = "CANCELLED"
    db.commit()
    return {"message": "Allocation successfully released", "status": "CANCELLED"}

@app.delete("/api/appointments/{appointment_id}")
def cancel_appointment_alias(appointment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cancel_allocation(appointment_id, user, db)

@app.get("/", response_class=HTMLResponse)
def index_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Hospital Appointment Management System — Generated by ForgeSwarm</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: #0B1120; color: #F8FAFC; font-family: system-ui, sans-serif; }
  </style>
</head>
<body class="p-6 max-w-5xl mx-auto">
  <header class="border-b border-slate-700 pb-4 mb-6 flex justify-between items-center">
    <div>
      <div class="flex items-center space-x-2">
        <span class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></span>
        <h1 class="text-2xl font-bold text-white tracking-tight">Hospital Appointment Management System</h1>
      </div>
      <p class="text-sm text-slate-400 mt-1">Domain: <span class="text-cyan-400 font-semibold">Healthcare</span> | Engineered by <span class="text-cyan-300 font-semibold">ForgeSwarm</span></p>
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
      <h2 class="text-lg font-semibold text-cyan-400 mb-3">Available Doctors Catalog</h2>
      <div id="item-list" class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div class="text-xs text-slate-500">Loading catalog...</div>
      </div>

      <div id="slot-container" class="mt-4 pt-4 border-t border-slate-800 hidden">
        <h3 class="text-sm font-semibold text-slate-200 mb-2">Select Allocation Slot for <span id="selected-item-name" class="text-cyan-300"></span></h3>
        <div id="slot-buttons" class="grid grid-cols-2 sm:grid-cols-3 gap-2"></div>
        <div class="mt-4 flex space-x-2">
          <input id="notes-input" type="text" placeholder="Notes / Purpose" class="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-xs text-white" value="Standard book">
          <button onclick="bookSelectedSlot()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded transition">Confirm Book</button>
        </div>
        <div id="booking-alert" class="mt-3 text-xs p-2 rounded hidden"></div>
      </div>
    </div>
  </div>

  <!-- User Allocations History -->
  <div class="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg font-semibold text-cyan-400">My Active Booked Records (FR-006 Traceability)</h2>
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

    async function handleRegister() {
      const name = document.getElementById('name-input').value;
      const email = document.getElementById('email-input').value;
      const password = document.getElementById('pass-input').value;
      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({name, email, password})
        });
        const data = await res.json();
        if (res.ok) {
          currentToken = data.token;
          onAuthSuccess(data.user.name);
          showAlert('auth-alert', 'Registered successfully!', 'emerald');
        } else {
          showAlert('auth-alert', data.detail || 'Registration failed', 'rose');
        }
      } catch (err) {
        showAlert('auth-alert', 'Network error', 'rose');
      }
    }

    async function handleLogin() {
      const email = document.getElementById('email-input').value;
      const password = document.getElementById('pass-input').value;
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({email, password})
        });
        const data = await res.json();
        if (res.ok) {
          currentToken = data.token;
          onAuthSuccess(data.user.name);
          showAlert('auth-alert', 'Signed in successfully!', 'emerald');
        } else {
          showAlert('auth-alert', data.detail || 'Login failed', 'rose');
        }
      } catch (err) {
        showAlert('auth-alert', 'Network error', 'rose');
      }
    }

    function onAuthSuccess(userName) {
      document.getElementById('auth-form').classList.add('hidden');
      document.getElementById('user-info').classList.remove('hidden');
      document.getElementById('logged-user').innerText = userName;
      document.getElementById('auth-status').innerText = 'Authenticated (' + userName + ')';
      fetchAllocations();
    }

    function handleLogout() {
      currentToken = null;
      document.getElementById('auth-form').classList.remove('hidden');
      document.getElementById('user-info').classList.add('hidden');
      document.getElementById('auth-status').innerText = 'Not authenticated';
      document.getElementById('allocations-list').innerHTML = '<div class="text-xs text-slate-500 py-2">Signed out.</div>';
    }

    function showAlert(elemId, msg, color) {
      const el = document.getElementById(elemId);
      el.className = `mt-3 text-xs p-2 rounded bg-${color}-900/50 text-${color}-200 border border-${color}-700 block`;
      el.innerText = msg;
    }

    async function fetchItems() {
      const res = await fetch('/api/doctors');
      const items = await res.json();
      const container = document.getElementById('item-list');
      container.innerHTML = items.map(i => `
        <div onclick="selectItem(${i.id}, '${i.name}')" class="p-3 bg-slate-800/80 hover:bg-slate-700/80 cursor-pointer rounded-lg border border-slate-700 transition">
          <div class="font-medium text-white text-sm">${i.name}</div>
          <div class="text-xs text-cyan-400 mt-0.5">${i.specialty}</div>
          <div class="text-xs text-slate-400 mt-1">${i.room}</div>
        </div>
      `).join('');
    }

    async function selectItem(id, name) {
      selectedItemId = id;
      document.getElementById('selected-item-name').innerText = name;
      document.getElementById('slot-container').classList.remove('hidden');
      
      const res = await fetch(`/api/doctors/${id}/slots`);
      const slots = await res.json();
      const container = document.getElementById('slot-buttons');
      container.innerHTML = slots.map(s => `
        <button onclick="chooseSlot('${s.slot}')" class="text-xs p-2 rounded border text-center transition ${
          s.available ? 'bg-slate-800 hover:bg-cyan-900 border-slate-700 text-slate-200' : 'bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed opacity-50'
        }" ${!s.available ? 'disabled' : ''}>
          ${s.slot}
        </button>
      `).join('');
    }

    function chooseSlot(slot) {
      selectedSlot = slot;
      showAlert('booking-alert', 'Selected: ' + slot, 'cyan');
    }

    async function bookSelectedSlot() {
      if (!currentToken) {
        alert('Please register or sign in first!');
        return;
      }
      if (!selectedItemId || !selectedSlot) {
        alert('Please select an item and available slot');
        return;
      }
      const notes = document.getElementById('notes-input').value;
      try {
        const res = await fetch('/api/allocations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + currentToken
          },
          body: JSON.stringify({
            doctor_id: selectedItemId,
            slot_time: selectedSlot,
            notes: notes
          })
        });
        const data = await res.json();
        if (res.ok) {
          showAlert('booking-alert', 'Confirmed allocation #' + data.id + ' for ' + data.slot_time, 'emerald');
          fetchAllocations();
          selectItem(selectedItemId, document.getElementById('selected-item-name').innerText);
        } else {
          showAlert('booking-alert', 'Conflict Error: ' + (data.detail || 'Slot Conflict'), 'rose');
        }
      } catch (err) {
        showAlert('booking-alert', 'Network error during reservation', 'rose');
      }
    }

    async function fetchAllocations() {
      if (!currentToken) return;
      const res = await fetch('/api/allocations', {
        headers: {'Authorization': 'Bearer ' + currentToken}
      });
      const data = await res.json();
      const container = document.getElementById('allocations-list');
      if (data.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-500 py-2">No active records.</div>';
        return;
      }
      container.innerHTML = data.map(a => `
        <div class="py-2.5 flex justify-between items-center">
          <div>
            <span class="font-medium text-white">${a.item_name}</span>
            <span class="text-xs text-slate-400 ml-2">${a.slot_time}</span>
            <span class="text-xs px-2 py-0.5 rounded ml-2 ${a.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'}">${a.status}</span>
          </div>
          ${a.status === 'ACTIVE' ? `<button onclick="cancelAlloc(${a.id})" class="text-xs bg-rose-900/50 hover:bg-rose-800 border border-rose-700 text-rose-200 px-2.5 py-1 rounded">Cancel</button>` : ''}
        </div>
      `).join('');
    }

    async function cancelAlloc(id) {
      const res = await fetch(`/api/allocations/${id}`, {
        method: 'DELETE',
        headers: {'Authorization': 'Bearer ' + currentToken}
      });
      if (res.ok) {
        fetchAllocations();
        if (selectedItemId) {
          selectItem(selectedItemId, document.getElementById('selected-item-name').innerText);
        }
      }
    }

    fetchItems();
  </script>
</body>
</html>"""
