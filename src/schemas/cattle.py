# src/schemas/cattle.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum
from uuid import UUID


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


class CattleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lote: str = Field(..., min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    gender: GenderEnum
    birth_date: Optional[date] = None
    weight: Optional[float] = Field(None, ge=0)
    fecha_ultimo_parto: Optional[date] = None


class CattleCreate(CattleBase):
    pass


class CattleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    lote: Optional[str] = Field(None, min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    gender: Optional[GenderEnum] = None
    birth_date: Optional[date] = None
    weight: Optional[float] = Field(None, ge=0)
    fecha_ultimo_parto: Optional[date] = None


class CattleResponse(CattleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CattleListResponse(BaseModel):
    total: int
    cattle: list[CattleResponse]
