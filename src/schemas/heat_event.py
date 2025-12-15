# src/schemas/heat_event.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class HeatEventBase(BaseModel):
    heat_date: date
    allows_mounting: Optional[bool] = None
    vaginal_discharge: Optional[str] = Field(None, max_length=200)
    vulva_swelling: Optional[str] = Field(None, max_length=200)
    comportamiento: Optional[str] = Field(None, max_length=500)
    was_inseminated: bool = False
    insemination_date: Optional[date] = None
    pregnancy_confirmed: Optional[bool] = None


class HeatEventCreate(HeatEventBase):
    cattle_id: UUID


class HeatEventUpdate(BaseModel):
    heat_date: Optional[date] = None
    allows_mounting: Optional[bool] = None
    vaginal_discharge: Optional[str] = Field(None, max_length=200)
    vulva_swelling: Optional[str] = Field(None, max_length=200)
    comportamiento: Optional[str] = Field(None, max_length=500)
    was_inseminated: Optional[bool] = None
    insemination_date: Optional[date] = None
    pregnancy_confirmed: Optional[bool] = None


class HeatEventResponse(HeatEventBase):
    id: UUID
    cattle_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HeatEventListResponse(BaseModel):
    total: int
    events: list[HeatEventResponse]
