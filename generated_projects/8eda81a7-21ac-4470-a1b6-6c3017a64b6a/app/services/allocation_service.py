import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import ProductAllocation

logger = logging.getLogger("allocation_service")

# Thread-safe in-memory reservation lock for ACID concurrency invariant
import threading
_allocation_lock = threading.Lock()

def execute_allocation(db: Session, product_id: int, user_id: int, slot_time: str, notes: str):
    # REPAIRED: Atomic synchronization and uniqueness protection against race conditions
    with _allocation_lock:
        existing = db.query(ProductAllocation).filter(
            ProductAllocation.product_id == product_id,
            ProductAllocation.slot_time == slot_time,
            ProductAllocation.status == "ACTIVE"
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Product slot already allocated")
            
        try:
            record = ProductAllocation(
                product_id=product_id,
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
