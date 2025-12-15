# src/schemas/health_event.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum
from uuid import UUID


class EventTypeEnum(str, Enum):
    vaccine = "vaccine"
    treatment = "treatment"
    checkup = "checkup"
    surgery = "surgery"
    injury = "injury"
    illness = "illness"
    other = "other"


class AdministrationRouteEnum(str, Enum):
    oral = "oral"
    intramuscular = "intramuscular"
    subcutaneous = "subcutaneous"
    intravenous = "intravenous"
    topical = "topical"
    other = "other"


class HealthEventBase(BaseModel):
    event_type: EventTypeEnum
    disease_name: Optional[str] = Field(None, max_length=100)
    medicine_name: Optional[str] = Field(None, max_length=100)
    application_date: date
    administration_route: Optional[AdministrationRouteEnum] = None
    next_dose_date: Optional[date] = None
    treatment_end_date: Optional[date] = None
    dosage: Optional[str] = Field(None, max_length=50)
    veterinarian_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class HealthEventCreate(HealthEventBase):
    cattle_id: UUID


class HealthEventUpdate(BaseModel):
    event_type: Optional[EventTypeEnum] = None
    disease_name: Optional[str] = Field(None, max_length=100)
    medicine_name: Optional[str] = Field(None, max_length=100)
    application_date: Optional[date] = None
    administration_route: Optional[AdministrationRouteEnum] = None
    next_dose_date: Optional[date] = None
    treatment_end_date: Optional[date] = None
    dosage: Optional[str] = Field(None, max_length=50)
    veterinarian_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class HealthEventResponse(HealthEventBase):
    id: UUID
    cattle_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HealthEventListResponse(BaseModel):
    total: int
    events: list[HealthEventResponse]
