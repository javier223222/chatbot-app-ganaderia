# src/schemas/reminder.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum
from uuid import UUID


class ReminderTypeEnum(str, Enum):
    vaccine = "vaccine"
    checkup = "checkup"
    treatment = "treatment"
    feeding = "feeding"
    breeding = "breeding"
    other = "other"


class ReminderStatusEnum(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


class ReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    reminder_date: date
    reminder_type: ReminderTypeEnum
    cattle_id: Optional[UUID] = None
    health_event_id: Optional[UUID] = None


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    reminder_date: Optional[date] = None
    reminder_type: Optional[ReminderTypeEnum] = None
    cattle_id: Optional[UUID] = None
    health_event_id: Optional[UUID] = None
    status: Optional[ReminderStatusEnum] = None


class ReminderResponse(ReminderBase):
    id: UUID
    status: ReminderStatusEnum
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReminderListResponse(BaseModel):
    total: int
    reminders: list[ReminderResponse]
