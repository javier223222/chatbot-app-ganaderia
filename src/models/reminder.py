from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.infrastructure.database import Base


class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cattle_id = Column(UUID(as_uuid=True), ForeignKey("cattle.id", ondelete="SET NULL"))
    health_event_id = Column(UUID(as_uuid=True), ForeignKey("health_events.id", ondelete="SET NULL"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    reminder_date = Column(Date, nullable=False)
    reminder_type = Column(String(50), nullable=False)  # vaccine, checkup, treatment, feeding, breeding, other
    status = Column(String(20), default="pending", nullable=False)  # pending, completed, cancelled
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships (solo con tablas de este servicio)
    cattle = relationship("Cattle", back_populates="reminders")
    health_event = relationship("HealthEvent", back_populates="reminders")
