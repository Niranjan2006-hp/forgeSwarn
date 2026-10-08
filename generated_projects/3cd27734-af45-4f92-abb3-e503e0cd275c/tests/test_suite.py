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

# --- FR-001: User Registration & Auth ---
def test_fr_001_user_registration_success():
    resp = client.post("/api/auth/register", json={
        "name": "Alex Vance",
        "email": "alex.vance@swarm-test.org",
        "password": "SecurePassword123!"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "alex.vance@swarm-test.org"

def test_fr_001_duplicate_registration_rejection():
    resp = client.post("/api/auth/register", json={
        "name": "Duplicate User",
        "email": "alex.vance@swarm-test.org",
        "password": "AnotherPassword!"
    })
    assert resp.status_code == 400

def test_fr_001_login_valid_credentials():
    resp = client.post("/api/auth/login", json={
        "email": "alex.vance@swarm-test.org",
        "password": "SecurePassword123!"
    })
    assert resp.status_code == 200
    assert "token" in resp.json()

def test_fr_001_login_invalid_password():
    resp = client.post("/api/auth/login", json={
        "email": "alex.vance@swarm-test.org",
        "password": "WrongPassword!"
    })
    assert resp.status_code == 401

# --- FR-002: Catalog Listing ---
def test_fr_002_list_items():
    resp = client.get("/api/vehicles")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 4

# --- FR-003: Slot Availability Inspection ---
def test_fr_003_available_slots_retrieval():
    resp = client.get("/api/vehicles/1/slots")
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) > 0
    assert any(s["available"] is True for s in slots)

# --- SEC-001: Unauthenticated Allocation Blocked ---
def test_sec_001_unauthenticated_allocation_blocked():
    resp = client.post("/api/allocations", json={
        "vehicle_id": 1,
        "slot_time": "2026-10-15 Slot 1 (09:00 AM)",
        "notes": "Test"
    })
    assert resp.status_code == 401

# --- FR-004: Authenticated Allocation Success ---
def test_fr_004_authenticated_allocation_success():
    resp = client.post("/api/allocations", 
        headers={"Authorization": "Bearer alex.vance@swarm-test.org"},
        json={
            "vehicle_id": 1,
            "slot_time": "2026-10-15 Slot 1 (09:00 AM)",
            "notes": "Priority Reservation"
        }
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "ACTIVE"

def test_fr_003_slot_status_updated_after_allocation():
    resp = client.get("/api/vehicles/1/slots")
    slots = resp.json()
    booked = next(s for s in slots if s["slot"] == "2026-10-15 Slot 1 (09:00 AM)")
    assert booked["available"] is False

# --- FR-005: Release / Cancellation Workflow ---
def test_fr_005_cancellation_workflow():
    alloc_resp = client.post("/api/allocations", 
        headers={"Authorization": "Bearer alex.vance@swarm-test.org"},
        json={
            "vehicle_id": 2,
            "slot_time": "2026-10-15 Slot 4 (01:00 PM)",
            "notes": "Temporary"
        }
    )
    alloc_id = alloc_resp.json()["id"]
    
    cancel_resp = client.delete(f"/api/allocations/{alloc_id}",
        headers={"Authorization": "Bearer alex.vance@swarm-test.org"}
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

def test_fr_005_slot_reopened_after_cancellation():
    resp = client.get("/api/vehicles/2/slots")
    slots = resp.json()
    reopened = next(s for s in slots if s["slot"] == "2026-10-15 Slot 4 (01:00 PM)")
    assert reopened["available"] is True

# --- FR-006: User Allocation History ---
def test_fr_006_user_allocation_history():
    resp = client.get("/api/allocations",
        headers={"Authorization": "Bearer alex.vance@swarm-test.org"}
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
        headers={"Authorization": "Bearer alex.vance@swarm-test.org"},
        json={
            "vehicle_id": 99999,
            "slot_time": "2026-10-15 Slot 1 (09:00 AM)"
        }
    )
    assert resp.status_code == 404

def test_fr_005_cancel_unauthorized_allocation_fails():
    resp = client.delete("/api/allocations/99999",
        headers={"Authorization": "Bearer alex.vance@swarm-test.org"}
    )
    assert resp.status_code == 404

def test_health_check_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

# --- BR-001: CONCURRENCY INVARIANT PROBE ---
def test_br_001_concurrency_invariant_prevention():
    """
    CRITICAL ACCEPTANCE TEST (Exclusive Vehicle Lease Invariant):
    Given two users attempt to allocate the exact same vehicle and slot simultaneously:
    EXPECTED: Exactly ONE succeeds (HTTP 201), the second MUST FAIL safely (HTTP 409 Conflict).
    """
    client.post("/api/auth/register", json={"name": "User Alpha", "email": "alpha.concurrency@test.com", "password": "pass"})
    client.post("/api/auth/register", json={"name": "User Beta", "email": "beta.concurrency@test.com", "password": "pass"})

    target_slot = "2026-10-15 Slot 2 (10:00 AM)"
    target_item_id = 1

    results = []

    def make_allocation(email):
        local_client = TestClient(app)
        res = local_client.post("/api/allocations",
            headers={"Authorization": f"Bearer {email}"},
            json={
                "vehicle_id": target_item_id,
                "slot_time": target_slot,
                "notes": f"Concurrent allocation probe from {email}"
            }
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
    assert successes == 1, f"BR-001 VIOLATION: Expected 1 booking success, got {successes}. Status codes: {results}"
    assert conflicts == 1, f"Expected 1 conflict rejection (409), got {conflicts}."
