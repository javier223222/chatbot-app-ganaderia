# src/repositories/cattle_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.cattle import Cattle
from src.schemas.cattle import CattleCreate, CattleUpdate


class CattleRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, cattle_data: CattleCreate) -> Cattle:
        """Crea un nuevo registro de ganado"""
        db_cattle = Cattle(**cattle_data.model_dump())
        self.db.add(db_cattle)
        self.db.commit()
        self.db.refresh(db_cattle)
        return db_cattle
    
    def get_by_id(self, cattle_id: UUID) -> Optional[Cattle]:
        """Obtiene un ganado por su ID"""
        return self.db.query(Cattle).filter(Cattle.id == cattle_id).first()
    
    def get_by_lote(self, lote: str) -> Optional[Cattle]:
        """Obtiene un ganado por su lote"""
        return self.db.query(Cattle).filter(Cattle.lote == lote).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """Obtiene todos los registros de ganado con paginación"""
        return self.db.query(Cattle).offset(skip).limit(limit).all()
    
    def get_by_gender(self, gender: str, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """Obtiene ganado filtrado por género"""
        return self.db.query(Cattle).filter(Cattle.gender == gender).offset(skip).limit(limit).all()
    
    def get_by_breed(self, breed: str, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """Obtiene ganado filtrado por raza"""
        return self.db.query(Cattle).filter(Cattle.breed == breed).offset(skip).limit(limit).all()
    
    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Cattle]:
        """Busca ganado por nombre (búsqueda parcial)"""
        return self.db.query(Cattle).filter(
            Cattle.name.ilike(f"%{name}%")
        ).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Cuenta el total de registros de ganado"""
        return self.db.query(func.count(Cattle.id)).scalar()
    
    def update(self, cattle_id: UUID, cattle_data: CattleUpdate) -> Optional[Cattle]:
        """Actualiza un registro de ganado"""
        db_cattle = self.get_by_id(cattle_id)
        if not db_cattle:
            return None
        
        update_data = cattle_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cattle, field, value)
        
        self.db.commit()
        self.db.refresh(db_cattle)
        return db_cattle
    
    def delete(self, cattle_id: UUID) -> bool:
        """Elimina un registro de ganado"""
        db_cattle = self.get_by_id(cattle_id)
        if not db_cattle:
            return False
        
        self.db.delete(db_cattle)
        self.db.commit()
        return True
    
    def exists_lote(self, lote: str, exclude_id: Optional[UUID] = None) -> bool:
        """Verifica si un lote ya existe"""
        query = self.db.query(Cattle).filter(Cattle.lote == lote)
        if exclude_id:
            query = query.filter(Cattle.id != exclude_id)
        return query.first() is not None
