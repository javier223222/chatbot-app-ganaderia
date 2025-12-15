# src/repositories/heat_event_repository.py
from typing import List, Optional
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.heat_event import HeatEventModel
from src.schemas.heat_event import HeatEventCreate, HeatEventUpdate


class HeatEventRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, event_data: HeatEventCreate) -> HeatEventModel:
        """Crea un nuevo evento de celo"""
        db_event = HeatEventModel(**event_data.model_dump())
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def get_by_id(self, event_id: UUID) -> Optional[HeatEventModel]:
        """Obtiene un evento de celo por su ID"""
        return self.db.query(HeatEventModel).filter(HeatEventModel.id == event_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[HeatEventModel]:
        """Obtiene todos los eventos de celo con paginación"""
        return self.db.query(HeatEventModel).offset(skip).limit(limit).all()
    
    def get_by_cattle_id(self, cattle_id: UUID, skip: int = 0, limit: int = 100) -> List[HeatEventModel]:
        """Obtiene todos los eventos de celo de un ganado específico"""
        return self.db.query(HeatEventModel).filter(
            HeatEventModel.cattle_id == cattle_id
        ).order_by(HeatEventModel.heat_date.desc()).offset(skip).limit(limit).all()
    
    def get_last_heat(self, cattle_id: UUID) -> Optional[HeatEventModel]:
        """Obtiene el último evento de celo de un ganado"""
        return self.db.query(HeatEventModel).filter(
            HeatEventModel.cattle_id == cattle_id
        ).order_by(HeatEventModel.heat_date.desc()).first()
    
    def get_inseminated(self, skip: int = 0, limit: int = 100) -> List[HeatEventModel]:
        """Obtiene eventos de celo donde hubo inseminación"""
        return self.db.query(HeatEventModel).filter(
            HeatEventModel.was_inseminated == True
        ).order_by(HeatEventModel.insemination_date.desc()).offset(skip).limit(limit).all()
    
    def get_confirmed_pregnancies(self, skip: int = 0, limit: int = 100) -> List[HeatEventModel]:
        """Obtiene eventos con embarazo confirmado"""
        return self.db.query(HeatEventModel).filter(
            HeatEventModel.pregnancy_confirmed == True
        ).offset(skip).limit(limit).all()
    
    def get_pending_pregnancy_check(self, days_after_insemination: int = 45, skip: int = 0, limit: int = 100) -> List[HeatEventModel]:
        """Obtiene inseminaciones que necesitan confirmación de embarazo"""
        check_date = date.today() - timedelta(days=days_after_insemination)
        return self.db.query(HeatEventModel).filter(
            and_(
                HeatEventModel.was_inseminated == True,
                HeatEventModel.pregnancy_confirmed.is_(None),
                HeatEventModel.insemination_date <= check_date
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[HeatEventModel]:
        """Obtiene eventos de celo en un rango de fechas"""
        return self.db.query(HeatEventModel).filter(
            and_(
                HeatEventModel.heat_date >= start_date,
                HeatEventModel.heat_date <= end_date
            )
        ).order_by(HeatEventModel.heat_date.desc()).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Cuenta el total de eventos de celo"""
        return self.db.query(func.count(HeatEventModel.id)).scalar()
    
    def count_by_cattle_id(self, cattle_id: UUID) -> int:
        """Cuenta los eventos de celo de un ganado específico"""
        return self.db.query(func.count(HeatEventModel.id)).filter(
            HeatEventModel.cattle_id == cattle_id
        ).scalar()
    
    def update(self, event_id: UUID, event_data: HeatEventUpdate) -> Optional[HeatEventModel]:
        """Actualiza un evento de celo"""
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
        """Elimina un evento de celo"""
        db_event = self.get_by_id(event_id)
        if not db_event:
            return False
        
        self.db.delete(db_event)
        self.db.commit()
        return True
