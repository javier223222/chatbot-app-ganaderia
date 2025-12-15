from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.infrastructure.database import Base


class HeatEventModel(Base):
    __tablename__ = "heat_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cattle_id = Column(UUID(as_uuid=True), ForeignKey("cattle.id", ondelete="CASCADE"), nullable=False)
    heat_date = Column(Date, nullable=False)
    allows_mounting = Column(Boolean)
    vaginal_discharge = Column(String(200))
    vulva_swelling = Column(String(200))
    comportamiento = Column(String(500))
    was_inseminated = Column(Boolean, default=False)
    insemination_date = Column(Date)
    pregnancy_confirmed = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con cattle
    cattle = relationship("Cattle", back_populates="heat_events")
