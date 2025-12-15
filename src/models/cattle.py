# src/infrastructure/models/cattle.py
from sqlalchemy import Column, String, DateTime, Date, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.infrastructure.database import Base


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class Cattle(Base):
    __tablename__ = "cattle"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Datos básicos
    name = Column(String(100), nullable=False)
    lote = Column(String(50), unique=True, nullable=False, index=True)
    breed = Column(String(100))
    gender = Column(SQLEnum(GenderEnum), nullable=False)
    birth_date = Column(Date)
    weight = Column(Float)
    fecha_ultimo_parto = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones (solo internas a core-service)
    health_events = relationship("HealthEvent", back_populates="cattle", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="cattle")
    heat_events = relationship("HeatEventModel", back_populates="cattle", cascade="all, delete-orphan")

