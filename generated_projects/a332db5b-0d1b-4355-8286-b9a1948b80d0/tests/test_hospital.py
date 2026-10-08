import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

# --- FR-001: Patient Registration and Auth Tests ---
def test_fr_001_patient_registration_success():
    resp = client.post("/api/auth/register", json={
        "name": "Sarah Connor",
        "email": "sarah.connor@hospital-test.org",
        "password": "SecurePassword123!"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "sarah.connor@hospital-test.org"

def test_fr_001_duplicate_registration_rejection():
    # Attempting to register existing email should return 400
    resp = client.post("/api/auth/register", json={
        "name": "Sarah Duplicate",
        "email": "sarah.connor@hospital-test.org",
        "password": "AnotherPassword!"
    })
    assert resp.status_code == 400

def test_fr_001_login_valid_credentials():
    resp = client.post("/api/auth/login", json={
        "email": "sarah.connor@hospital-test.org",
        "password": "SecurePassword123!"
    })
    assert resp.status_code == 200
    assert "token" in resp.json()

def test_fr_001_login_invalid_password():
    resp = client.post("/api/auth/login", json={
        "email": "sarah.connor@hospital-test.org",
        "password": "WrongPassword!"
    })
    assert resp.status_code == 401

# --- FR-002: Doctor Directory Browsing ---
def test_fr_002_list_doctors():
    resp = client.get("/api/doctors")
    assert resp.status_code == 200
    doctors = resp.json()
    assert len(doctors) >= 4
    names = [d["name"] for d in doctors]
    assert "Dr. Priya Sharma" in names

# --- FR-003: Slot Availability ---
def test_fr_003_available_slots_retrieval():
    resp = client.get("/api/doctors/1/slots")
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) > 0
    assert any(s["available"] is True for s in slots)

# --- FR-004: Appointment Booking & SEC-001 Authentication Check ---
def test_sec_001_unauthenticated_booking_blocked():
    resp = client.post("/api/appointments", json={
        "doctor_id": 1,
        "appointment_time": "2026-10-15 09:00 AM",
        "reason": "Checkup"
    })
    assert resp.status_code == 401

def test_fr_004_authenticated_booking_success():
    resp = client.post("/api/appointments", 
        headers={"Authorization": "Bearer sarah.connor@hospital-test.org"},
        json={
            "doctor_id": 1,
            "appointment_time": "2026-10-15 09:00 AM",
            "reason": "Chest Pain"
        }
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "BOOKED"

def test_fr_003_slot_status_updated_after_booking():
    resp = client.get("/api/doctors/1/slots")
    slots = resp.json()
    booked_slot = next(s for s in slots if s["slot"] == "2026-10-15 09:00 AM")
    assert booked_slot["available"] is False

# --- FR-005: Appointment Cancellation ---
def test_fr_005_cancellation_workflow():
    # Create booking then cancel
    book_resp = client.post("/api/appointments", 
        headers={"Authorization": "Bearer sarah.connor@hospital-test.org"},
        json={
            "doctor_id": 2,
            "appointment_time": "2026-10-15 02:00 PM",
            "reason": "Migraine"
        }
    )
    app_id = book_resp.json()["id"]
    
    cancel_resp = client.delete(f"/api/appointments/{app_id}",
        headers={"Authorization": "Bearer sarah.connor@hospital-test.org"}
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

def test_fr_005_slot_reopened_after_cancellation():
    resp = client.get("/api/doctors/2/slots")
    slots = resp.json()
    reopened = next(s for s in slots if s["slot"] == "2026-10-15 02:00 PM")
    assert reopened["available"] is True

# --- FR-006: Patient History ---
def test_fr_006_patient_appointment_history():
    resp = client.get("/api/appointments",
        headers={"Authorization": "Bearer sarah.connor@hospital-test.org"}
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

# --- Security Checks ---
def test_sec_002_password_not_stored_plaintext():
    from app.models import User
    from app.database import SessionLocal
    db = SessionLocal()
    user = db.query(User).filter(User.email == "sarah.connor@hospital-test.org").first()
    assert user.password_hash != "SecurePassword123!"
    assert len(user.password_hash) == 64  # sha256
    db.close()

# --- Additional Boundary Tests ---
def test_fr_004_nonexistent_doctor_rejection():
    resp = client.post("/api/appointments", 
        headers={"Authorization": "Bearer sarah.connor@hospital-test.org"},
        json={
            "doctor_id": 99999,
            "appointment_time": "2026-10-15 09:00 AM"
        }
    )
    assert resp.status_code == 404

def test_fr_005_cancel_unauthorized_appointment_fails():
    resp = client.delete("/api/appointments/99999",
        headers={"Authorization": "Bearer sarah.connor@hospital-test.org"}
    )
    assert resp.status_code == 404

def test_health_check_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

# --- BR-001: ZERO DOUBLE-BOOKING CONCURRENCY INVARIANT ---
def test_br_001_concurrency_double_booking_prevention():
    """
    CRITICAL ACCEPTANCE TEST:
    Given two patients attempt to book the EXACT SAME doctor and time slot simultaneously:
    EXPECTED: Exactly ONE succeeds (HTTP 201), the other MUST FAIL (HTTP 409 Conflict).
    """
    # Register two distinct patients
    client.post("/api/auth/register", json={"name": "Patient Alpha", "email": "alpha@test.com", "password": "pass"})
    client.post("/api/auth/register", json={"name": "Patient Beta", "email": "beta@test.com", "password": "pass"})

    target_slot = "2026-10-15 10:00 AM"
    target_doctor = 1  # Dr. Sharma

    results = []

    def make_booking(user_email):
        local_client = TestClient(app)
        res = local_client.post("/api/appointments",
            headers={"Authorization": f"Bearer {user_email}"},
            json={
                "doctor_id": target_doctor,
                "appointment_time": target_slot,
                "reason": f"Concurrent test from {user_email}"
            }
        )
        return res.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(make_booking, "alpha@test.com")
        f2 = executor.submit(make_booking, "beta@test.com")
        results = [f1.result(), f2.result()]

    successes = results.count(201)
    conflicts = results.count(409)

    # In the defective version, BOTH requests will return 201 (successes == 2), which fails this assertion!
    # In the repaired version, exactly one is 201 and the other is 409.
    assert successes == 1, f"BR-001 VIOLATION: Expected 1 booking success, got {successes}. Status codes: {results}"
    assert conflicts == 1, f"Expected 1 conflict rejection (409), got {conflicts}."
