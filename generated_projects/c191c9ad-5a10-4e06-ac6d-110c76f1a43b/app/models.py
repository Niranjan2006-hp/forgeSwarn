from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="MEMBER")
    is_active = Column(String(10), default="TRUE")
    created_at = Column(DateTime, default=datetime.utcnow)
    allocations = relationship("CourseAllocation", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    instructor = Column(String(100), nullable=False)
    schedule = Column(String(100), nullable=False)
    status = Column(String(50), default="AVAILABLE")
    created_at = Column(DateTime, default=datetime.utcnow)
    allocations = relationship("CourseAllocation", back_populates="course")

class CourseAllocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    slot_time = Column(String(50), nullable=False)
    notes = Column(String(255), default="Standard allocation")
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="allocations")
    user = relationship("User", back_populates="allocations")
    __table_args__ = (UniqueConstraint('course_id', 'slot_time', name='uix_course_slot'),)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    entity_name = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
