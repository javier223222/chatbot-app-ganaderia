# src/services/tools/cattle_tools.py
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from src.repositories import CattleRepository
from src.schemas.cattle import CattleResponse, CattleCreate, GenderEnum


def create_cattle_tool(db: Session, name: str, lote: str, gender: str, breed: str = None, weight: float = None, birth_date: str = None) -> str:
    """Registra un nuevo ganado en la base de datos"""
    try:
        # Validar género
        try:
            gender_enum = GenderEnum(gender.lower())
        except ValueError:
            return f"Error: El género debe ser 'male' o 'female'. Recibido: {gender}"

        # Convertir fecha si existe
        birth_date_obj = None
        if birth_date:
            try:
                birth_date_obj = date.fromisoformat(birth_date)
            except ValueError:
                return f"Error: La fecha de nacimiento debe tener formato YYYY-MM-DD. Recibido: {birth_date}"

        cattle_data = CattleCreate(
            name=name,
            lote=lote,
            gender=gender_enum,
            breed=breed,
            weight=weight,
            birth_date=birth_date_obj
        )
        
        repo = CattleRepository(db)
        
        # Verificar si el lote ya existe
        if repo.get_by_lote(lote):
            return f"Error: Ya existe un ganado con el lote '{lote}'."
            
        new_cattle = repo.create(cattle_data)
        
        return f"✅ Ganado registrado exitosamente:\n- Nombre: {new_cattle.name}\n- Lote: {new_cattle.lote}\n- ID: {new_cattle.id}"
    except Exception as e:
        return f"Error al crear ganado: {str(e)}"


def get_all_cattle_tool(db: Session, limit: int = 50) -> str:
    """Obtiene información de todo el ganado registrado"""
    repo = CattleRepository(db)
    cattle_list = repo.get_all(limit=limit)
    
    if not cattle_list:
        return "No hay ganado registrado en la base de datos."
    
    result = f"Total de ganado: {repo.count()}\n\n"
    for cattle in cattle_list:
        result += f"- {cattle.name} (Lote: {cattle.lote})\n"
        result += f"  Raza: {cattle.breed or 'No especificada'}\n"
        result += f"  Género: {cattle.gender.value}\n"
        result += f"  Peso: {cattle.weight or 'No registrado'} kg\n"
        if cattle.birth_date:
            age = (date.today() - cattle.birth_date).days // 365
            result += f"  Edad: {age} años\n"
        result += "\n"
    
    return result


def search_cattle_by_name_tool(db: Session, name: str) -> str:
    """Busca ganado por nombre"""
    repo = CattleRepository(db)
    cattle_list = repo.search_by_name(name, limit=10)
    
    if not cattle_list:
        return f"No se encontró ningún ganado con el nombre '{name}'."
    
    result = f"Ganado encontrado con nombre similar a '{name}':\n\n"
    for cattle in cattle_list:
        result += f"- {cattle.name} (Lote: {cattle.lote})\n"
        result += f"  Raza: {cattle.breed}\n"
        result += f"  Género: {cattle.gender.value}\n"
        result += f"  Peso: {cattle.weight} kg\n"
        result += "\n"
    
    return result


def get_cattle_by_lote_tool(db: Session, lote: str) -> str:
    """Obtiene información de un ganado específico por su lote"""
    repo = CattleRepository(db)
    cattle = repo.get_by_lote(lote)
    
    if not cattle:
        return f"No se encontró ganado con el lote '{lote}'."
    
    result = f"Información del ganado {cattle.name}:\n"
    result += f"- Lote: {cattle.lote}\n"
    result += f"- Raza: {cattle.breed or 'No especificada'}\n"
    result += f"- Género: {cattle.gender.value}\n"
    result += f"- Peso: {cattle.weight or 'No registrado'} kg\n"
    
    if cattle.birth_date:
        age = (date.today() - cattle.birth_date).days // 365
        result += f"- Edad: {age} años (Fecha de nacimiento: {cattle.birth_date})\n"
    
    if cattle.fecha_ultimo_parto:
        result += f"- Último parto: {cattle.fecha_ultimo_parto}\n"
    
    return result


def get_cattle_by_gender_tool(db: Session, gender: str) -> str:
    """Obtiene ganado filtrado por género (male o female)"""
    repo = CattleRepository(db)
    cattle_list = repo.get_by_gender(gender, limit=50)
    
    if not cattle_list:
        return f"No se encontró ganado de género '{gender}'."
    
    result = f"Ganado de género {gender}:\n\n"
    for cattle in cattle_list:
        result += f"- {cattle.name} (Lote: {cattle.lote}, Raza: {cattle.breed})\n"
    
    return result
