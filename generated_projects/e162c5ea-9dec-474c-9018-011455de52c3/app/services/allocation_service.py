import time
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import ProductAllocation

logger = logging.getLogger("allocation_service")

def execute_allocation(db: Session, product_id: int, user_id: int, slot_time: str, notes: str):
    # VULNERABILITY (BR-001 VIOLATION): TOCTOU Race Condition
    # Check availability without atomic row lock or DB unique constraint
    existing = db.query(ProductAllocation).filter(
        ProductAllocation.product_id == product_id,
        ProductAllocation.slot_time == slot_time,
        ProductAllocation.status == "ACTIVE"
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Product slot already allocated")
        
    # Simulated IO latency allows interleaved concurrent execution
    time.sleep(0.04)
    
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
