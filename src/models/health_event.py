# src/infrastructure/models/health_event.py
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.infrastructure.database import Base


class EventTypeEnum(str, enum.Enum):
    vaccine = "vaccine"
    treatment = "treatment"
    checkup = "checkup"
    surgery = "surgery"
    injury = "injury"
    illness = "illness"
    other = "other"


class AdministrationRouteEnum(str, enum.Enum):
    oral = "oral"
    intramuscular = "intramuscular"
    subcutaneous = "subcutaneous"
    intravenous = "intravenous"
    topical = "topical"
    other = "other"


class HealthEvent(Base):
    __tablename__ = "health_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cattle_id = Column(UUID(as_uuid=True), ForeignKey("cattle.id", ondelete="CASCADE"), nullable=False)
    
    event_type = Column(SQLEnum(EventTypeEnum), nullable=False)
    disease_name = Column(String(100))
    medicine_name = Column(String(100))
    application_date = Column(Date, nullable=False)
    administration_route = Column(SQLEnum(AdministrationRouteEnum))
    next_dose_date = Column(Date)
    treatment_end_date = Column(Date)
    dosage = Column(String(50))
    veterinarian_name = Column(String(100))
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    cattle = relationship("Cattle", back_populates="health_events")
    reminders = relationship("Reminder", back_populates="health_event")
