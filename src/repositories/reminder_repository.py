# src/repositories/reminder_repository.py
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.reminder import Reminder
from src.schemas.reminder import ReminderCreate, ReminderUpdate, ReminderStatusEnum, ReminderTypeEnum


class ReminderRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, reminder_data: ReminderCreate) -> Reminder:
        """Crea un nuevo recordatorio"""
        db_reminder = Reminder(**reminder_data.model_dump())
        self.db.add(db_reminder)
        self.db.commit()
        self.db.refresh(db_reminder)
        return db_reminder
    
    def get_by_id(self, reminder_id: UUID) -> Optional[Reminder]:
        """Obtiene un recordatorio por su ID"""
        return self.db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene todos los recordatorios con paginación"""
        return self.db.query(Reminder).order_by(Reminder.reminder_date).offset(skip).limit(limit).all()
    
    def get_by_cattle_id(self, cattle_id: UUID, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene todos los recordatorios de un ganado específico"""
        return self.db.query(Reminder).filter(
            Reminder.cattle_id == cattle_id
        ).order_by(Reminder.reminder_date).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: ReminderStatusEnum, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene recordatorios por estado"""
        return self.db.query(Reminder).filter(
            Reminder.status == status.value
        ).order_by(Reminder.reminder_date).offset(skip).limit(limit).all()
    
    def get_pending(self, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene recordatorios pendientes"""
        return self.get_by_status(ReminderStatusEnum.pending, skip, limit)
    
    def get_by_type(self, reminder_type: ReminderTypeEnum, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene recordatorios por tipo"""
        return self.db.query(Reminder).filter(
            Reminder.reminder_type == reminder_type.value
        ).order_by(Reminder.reminder_date).offset(skip).limit(limit).all()
    
    def get_upcoming(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene recordatorios próximos en los siguientes X días"""
        end_date = date.today() + timedelta(days=days)
        return self.db.query(Reminder).filter(
            and_(
                Reminder.status == "pending",
                Reminder.reminder_date >= date.today(),
                Reminder.reminder_date <= end_date
            )
        ).order_by(Reminder.reminder_date).offset(skip).limit(limit).all()
    
    def get_overdue(self, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene recordatorios vencidos (pendientes con fecha pasada)"""
        return self.db.query(Reminder).filter(
            and_(
                Reminder.status == "pending",
                Reminder.reminder_date < date.today()
            )
        ).order_by(Reminder.reminder_date).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtiene recordatorios en un rango de fechas"""
        return self.db.query(Reminder).filter(
            and_(
                Reminder.reminder_date >= start_date,
                Reminder.reminder_date <= end_date
            )
        ).order_by(Reminder.reminder_date).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Cuenta el total de recordatorios"""
        return self.db.query(func.count(Reminder.id)).scalar()
    
    def count_pending(self) -> int:
        """Cuenta los recordatorios pendientes"""
        return self.db.query(func.count(Reminder.id)).filter(
            Reminder.status == "pending"
        ).scalar()
    
    def count_overdue(self) -> int:
        """Cuenta los recordatorios vencidos"""
        return self.db.query(func.count(Reminder.id)).filter(
            and_(
                Reminder.status == "pending",
                Reminder.reminder_date < date.today()
            )
        ).scalar()
    
    def update(self, reminder_id: UUID, reminder_data: ReminderUpdate) -> Optional[Reminder]:
        """Actualiza un recordatorio"""
        db_reminder = self.get_by_id(reminder_id)
        if not db_reminder:
            return None
        
        update_data = reminder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_reminder, field, value)
        
        self.db.commit()
        self.db.refresh(db_reminder)
        return db_reminder
    
    def mark_completed(self, reminder_id: UUID) -> Optional[Reminder]:
        """Marca un recordatorio como completado"""
        from datetime import datetime
        db_reminder = self.get_by_id(reminder_id)
        if not db_reminder:
            return None
        
        db_reminder.status = "completed"
        db_reminder.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_reminder)
        return db_reminder
    
    def mark_cancelled(self, reminder_id: UUID) -> Optional[Reminder]:
        """Marca un recordatorio como cancelado"""
        db_reminder = self.get_by_id(reminder_id)
        if not db_reminder:
            return None
        
        db_reminder.status = "cancelled"
        
        self.db.commit()
        self.db.refresh(db_reminder)
        return db_reminder
    
    def delete(self, reminder_id: UUID) -> bool:
        """Elimina un recordatorio"""
        db_reminder = self.get_by_id(reminder_id)
        if not db_reminder:
            return False
        
        self.db.delete(db_reminder)
        self.db.commit()
        return True


from datetime import timedelta
