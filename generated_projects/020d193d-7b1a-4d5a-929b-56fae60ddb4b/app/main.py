import hashlib
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import User, Doctor, Appointment
from app.services.booking_service import book_appointment

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

# Seed sample doctors if empty
def seed_doctors():
    db = next(get_db())
    if db.query(Doctor).count() == 0:
        docs = [
            Doctor(name="Dr. Priya Sharma", specialty="Cardiology", room="Suite 301"),
            Doctor(name="Dr. Marcus Vance", specialty="Neurology", room="Suite 405"),
            Doctor(name="Dr. Elena Rostova", specialty="Pediatrics", room="Suite 102"),
            Doctor(name="Dr. James Wilson", specialty="Orthopedics", room="Suite 204")
        ]
        db.add_all(docs)
        db.commit()
    db.close()

seed_doctors()

# Schemas
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class BookRequest(BaseModel):
    doctor_id: int
    appointment_time: str
    reason: Optional[str] = "General Consultation"

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
    return {"status": "HEALTHY", "system": "Hospital Appointment Platform", "version": "1.0.0"}

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
def get_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    return [{"id": d.id, "name": d.name, "specialty": d.specialty, "room": d.room} for d in doctors]

@app.get("/api/doctors/{doctor_id}/slots")
def get_doctor_slots(doctor_id: int, date: str = "2026-10-15", db: Session = Depends(get_db)):
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    all_slots = [
        f"{date} 09:00 AM", f"{date} 09:30 AM", f"{date} 10:00 AM",
        f"{date} 10:30 AM", f"{date} 11:00 AM", f"{date} 11:30 AM",
        f"{date} 02:00 PM", f"{date} 02:30 PM", f"{date} 03:00 PM"
    ]
    
    booked = db.query(Appointment.appointment_time).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == "BOOKED"
    ).all()
    booked_times = {b[0] for b in booked}
    
    return [
        {"slot": slot, "available": slot not in booked_times}
        for slot in all_slots
    ]

@app.post("/api/appointments", status_code=201)
def create_appointment(req: BookRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Doctor).filter(Doctor.id == req.doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    app_record = book_appointment(db, req.doctor_id, user.id, req.appointment_time, req.reason)
    return {
        "id": app_record.id,
        "doctor_id": app_record.doctor_id,
        "doctor_name": doc.name,
        "appointment_time": app_record.appointment_time,
        "reason": app_record.reason,
        "status": app_record.status
    }

@app.get("/api/appointments")
def list_appointments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(Appointment).filter(Appointment.patient_id == user.id).all()
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "doctor_id": r.doctor_id,
            "doctor_name": r.doctor.name if r.doctor else "Unknown",
            "appointment_time": r.appointment_time,
            "reason": r.reason,
            "status": r.status
        })
    return result

@app.delete("/api/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Appointment not found or not owned by user")
    record.status = "CANCELLED"
    db.commit()
    return {"message": "Appointment cancelled successfully", "status": "CANCELLED"}

@app.get("/", response_class=HTMLResponse)
def index_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Hospital Appointment Platform — Generated by ForgeSwarm</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: #0B1120; color: #F8FAFC; font-family: system-ui, sans-serif; }
  </style>
</head>
<body class="p-6 max-w-5xl mx-auto">
  <header class="border-b border-slate-700 pb-4 mb-6 flex justify-between items-center">
    <div>
      <div class="flex items-center space-x-2">
        <span class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
        <h1 class="text-2xl font-bold text-white tracking-tight">Hospital Appointment Portal</h1>
      </div>
      <p class="text-sm text-slate-400 mt-1">Autonomous Application Engineered by <span class="text-cyan-400 font-semibold">ForgeSwarm</span></p>
    </div>
    <div id="auth-status" class="text-right text-xs text-slate-400">Not authenticated</div>
  </header>

  <div id="app-container" class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Auth & Profile Card -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-cyan-400 mb-3" id="auth-title">Patient Authentication</h2>
      <div id="auth-form" class="space-x-1">
        <input id="name-input" type="text" placeholder="Full Name" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white mb-2" value="Alex Morgan">
        <input id="email-input" type="email" placeholder="Email Address" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white mb-2" value="alex@example.com">
        <input id="pass-input" type="password" placeholder="Password" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white mb-3" value="Secret123!">
        <div class="flex space-x-2">
          <button onclick="handleRegister()" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold py-2 px-3 rounded transition">Register</button>
          <button onclick="handleLogin()" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white text-xs font-semibold py-2 px-3 rounded transition">Sign In</button>
        </div>
      </div>
      <div id="user-info" class="hidden">
        <p class="text-sm text-slate-300">Signed in as: <strong id="logged-user" class="text-emerald-400">Alex</strong></p>
        <button onclick="handleLogout()" class="mt-3 text-xs bg-rose-900/60 hover:bg-rose-800 text-rose-200 px-3 py-1.5 rounded">Sign Out</button>
      </div>
      <div id="auth-alert" class="mt-3 text-xs p-2 rounded hidden"></div>
    </div>

    <!-- Doctors & Slot Picker -->
    <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-cyan-400 mb-3">Available Doctors & Appointments</h2>
      <div id="doctor-list" class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div class="text-xs text-slate-500">Loading clinical staff...</div>
      </div>

      <div id="slot-container" class="mt-4 pt-4 border-t border-slate-800 hidden">
        <h3 class="text-sm font-semibold text-slate-200 mb-2">Select Slot for <span id="selected-doc-name" class="text-cyan-300"></span></h3>
        <div id="slot-buttons" class="grid grid-cols-3 gap-2"></div>
        <div class="mt-4 flex space-x-2">
          <input id="reason-input" type="text" placeholder="Reason (e.g. Annual Checkup)" class="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-xs text-white" value="Cardiology Consultation">
          <button onclick="bookSelectedSlot()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded transition">Confirm Booking</button>
        </div>
        <div id="booking-alert" class="mt-3 text-xs p-2 rounded hidden"></div>
      </div>
    </div>
  </div>

  <!-- Appointments History -->
  <div class="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg font-semibold text-cyan-400">My Scheduled Appointments (Traceability FR-006)</h2>
      <button onclick="fetchAppointments()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded">Refresh</button>
    </div>
    <div id="appointments-list" class="divide-y divide-slate-800 text-sm">
      <div class="text-xs text-slate-500 py-2">No appointments scheduled yet or not authenticated.</div>
    </div>
  </div>

  <script>
    let currentToken = null;
    let selectedDoctorId = null;
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
          showAlert('auth-alert', 'Account registered successfully!', 'emerald');
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
      fetchAppointments();
    }

    function handleLogout() {
      currentToken = null;
      document.getElementById('auth-form').classList.remove('hidden');
      document.getElementById('user-info').classList.add('hidden');
      document.getElementById('auth-status').innerText = 'Not authenticated';
      document.getElementById('appointments-list').innerHTML = '<div class="text-xs text-slate-500 py-2">Signed out.</div>';
    }

    function showAlert(elemId, msg, color) {
      const el = document.getElementById(elemId);
      el.className = `mt-3 text-xs p-2 rounded bg-${color}-900/50 text-${color}-200 border border-${color}-700 block`;
      el.innerText = msg;
    }

    async function fetchDoctors() {
      const res = await fetch('/api/doctors');
      const docs = await res.json();
      const container = document.getElementById('doctor-list');
      container.innerHTML = docs.map(d => `
        <div onclick="selectDoctor(${d.id}, '${d.name}')" class="p-3 bg-slate-800/80 hover:bg-slate-700/80 cursor-pointer rounded-lg border border-slate-700 transition">
          <div class="font-medium text-white text-sm">${d.name}</div>
          <div class="text-xs text-cyan-400">${d.specialty}</div>
          <div class="text-xs text-slate-400 mt-1">${d.room}</div>
        </div>
      `).join('');
    }

    async function selectDoctor(id, name) {
      selectedDoctorId = id;
      document.getElementById('selected-doc-name').innerText = name;
      document.getElementById('slot-container').classList.remove('hidden');
      
      const res = await fetch(`/api/doctors/${id}/slots`);
      const slots = await res.json();
      const container = document.getElementById('slot-buttons');
      container.innerHTML = slots.map(s => `
        <button onclick="chooseSlot('${s.slot}')" class="text-xs p-2 rounded border text-center transition ${
          s.available ? 'bg-slate-800 hover:bg-cyan-900 border-slate-700 text-slate-200' : 'bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed opacity-50'
        }" ${!s.available ? 'disabled' : ''}>
          ${s.slot.split(' ')[1]} ${s.slot.split(' ')[2]}
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
      if (!selectedDoctorId || !selectedSlot) {
        alert('Please pick a doctor and an available slot');
        return;
      }
      const reason = document.getElementById('reason-input').value;
      try {
        const res = await fetch('/api/appointments', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + currentToken
          },
          body: JSON.stringify({
            doctor_id: selectedDoctorId,
            appointment_time: selectedSlot,
            reason: reason
          })
        });
        const data = await res.json();
        if (res.ok) {
          showAlert('booking-alert', 'Confirmed booking #' + data.id + ' at ' + data.appointment_time, 'emerald');
          fetchAppointments();
          selectDoctor(selectedDoctorId, document.getElementById('selected-doc-name').innerText);
        } else {
          showAlert('booking-alert', 'Booking Error: ' + (data.detail || 'Slot Conflict'), 'rose');
        }
      } catch (err) {
        showAlert('booking-alert', 'Network error during reservation', 'rose');
      }
    }

    async function fetchAppointments() {
      if (!currentToken) return;
      const res = await fetch('/api/appointments', {
        headers: {'Authorization': 'Bearer ' + currentToken}
      });
      const data = await res.json();
      const container = document.getElementById('appointments-list');
      if (data.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-500 py-2">No appointments booked yet.</div>';
        return;
      }
      container.innerHTML = data.map(a => `
        <div class="py-2.5 flex justify-between items-center">
          <div>
            <span class="font-medium text-white">${a.doctor_name}</span>
            <span class="text-xs text-slate-400 ml-2">${a.appointment_time}</span>
            <span class="text-xs px-2 py-0.5 rounded ml-2 ${a.status === 'BOOKED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'}">${a.status}</span>
          </div>
          ${a.status === 'BOOKED' ? `<button onclick="cancelApp(${a.id})" class="text-xs bg-rose-900/50 hover:bg-rose-800 border border-rose-700 text-rose-200 px-2.5 py-1 rounded">Cancel</button>` : ''}
        </div>
      `).join('');
    }

    async function cancelApp(id) {
      const res = await fetch(`/api/appointments/${id}`, {
        method: 'DELETE',
        headers: {'Authorization': 'Bearer ' + currentToken}
      });
      if (res.ok) {
        fetchAppointments();
        if (selectedDoctorId) {
          selectDoctor(selectedDoctorId, document.getElementById('selected-doc-name').innerText);
        }
      }
    }

    fetchDoctors();
  </script>
</body>
</html>"""
