# src/repositories/health_event_repository.py
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.health_event import HealthEvent, EventTypeEnum
from src.schemas.health_event import HealthEventCreate, HealthEventUpdate


class HealthEventRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, event_data: HealthEventCreate) -> HealthEvent:
        """Crea un nuevo evento de salud"""
        db_event = HealthEvent(**event_data.model_dump())
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def get_by_id(self, event_id: UUID) -> Optional[HealthEvent]:
        """Obtiene un evento de salud por su ID"""
        return self.db.query(HealthEvent).filter(HealthEvent.id == event_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[HealthEvent]:
        """Obtiene todos los eventos de salud con paginación"""
        return self.db.query(HealthEvent).offset(skip).limit(limit).all()
    
    def get_by_cattle_id(self, cattle_id: UUID, skip: int = 0, limit: int = 100) -> List[HealthEvent]:
        """Obtiene todos los eventos de salud de un ganado específico"""
        return self.db.query(HealthEvent).filter(
            HealthEvent.cattle_id == cattle_id
        ).order_by(HealthEvent.application_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_event_type(self, event_type: EventTypeEnum, skip: int = 0, limit: int = 100) -> List[HealthEvent]:
        """Obtiene eventos de salud por tipo"""
        return self.db.query(HealthEvent).filter(
            HealthEvent.event_type == event_type
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[HealthEvent]:
        """Obtiene eventos de salud en un rango de fechas"""
        return self.db.query(HealthEvent).filter(
            and_(
                HealthEvent.application_date >= start_date,
                HealthEvent.application_date <= end_date
            )
        ).order_by(HealthEvent.application_date.desc()).offset(skip).limit(limit).all()
    
    def get_upcoming_doses(self, current_date: date, skip: int = 0, limit: int = 100) -> List[HealthEvent]:
        """Obtiene eventos con próximas dosis pendientes"""
        return self.db.query(HealthEvent).filter(
            and_(
                HealthEvent.next_dose_date.isnot(None),
                HealthEvent.next_dose_date >= current_date
            )
        ).order_by(HealthEvent.next_dose_date).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Cuenta el total de eventos de salud"""
        return self.db.query(func.count(HealthEvent.id)).scalar()
    
    def count_by_cattle_id(self, cattle_id: UUID) -> int:
        """Cuenta los eventos de salud de un ganado específico"""
        return self.db.query(func.count(HealthEvent.id)).filter(
            HealthEvent.cattle_id == cattle_id
        ).scalar()
    
    def update(self, event_id: UUID, event_data: HealthEventUpdate) -> Optional[HealthEvent]:
        """Actualiza un evento de salud"""
        db_event = self.get_by_id(event_id)
        if not db_event:
            return None
        
        update_data = event_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_event, field, value)
        
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def delete(self, event_id: UUID) -> bool:
        """Elimina un evento de salud"""
        db_event = self.get_by_id(event_id)
        if not db_event:
            return False
        
        self.db.delete(db_event)
        self.db.commit()
        return True
