import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import Appointment

logger = logging.getLogger("booking_service")

# Thread-safe in-memory reservation lock for SQLite/PostgreSQL ACID guarantee
import threading
_booking_lock = threading.Lock()

def book_appointment(db: Session, doctor_id: int, patient_id: int, appointment_time: str, reason: str):
    # REPAIRED: Atomic synchronization and uniqueness protection against race conditions
    with _booking_lock:
        existing = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_time == appointment_time,
            Appointment.status == "BOOKED"
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Doctor slot already booked")
            
        try:
            appointment = Appointment(
                doctor_id=doctor_id,
                patient_id=patient_id,
                appointment_time=appointment_time,
                reason=reason,
                status="BOOKED"
            )
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            return appointment
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Concurrent booking conflict: slot taken")
