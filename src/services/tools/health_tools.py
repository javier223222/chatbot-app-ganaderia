# src/services/tools/health_tools.py
from typing import Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from src.repositories import HealthEventRepository, CattleRepository


def get_health_events_by_cattle_tool(db: Session, lote: str) -> str:
    """Obtiene el historial de eventos de salud de un ganado por su lote"""
    cattle_repo = CattleRepository(db)
    cattle = cattle_repo.get_by_lote(lote)
    
    if not cattle:
        return f"No se encontró ganado con el lote '{lote}'."
    
    health_repo = HealthEventRepository(db)
    events = health_repo.get_by_cattle_id(cattle.id, limit=20)
    
    if not events:
        return f"El ganado {cattle.name} (Lote: {lote}) no tiene eventos de salud registrados."
    
    result = f"Historial de salud de {cattle.name} (Lote: {lote}):\n\n"
    for event in events:
        result += f"📅 {event.application_date} - {event.event_type.value.upper()}\n"
        if event.disease_name:
            result += f"   Enfermedad: {event.disease_name}\n"
        if event.medicine_name:
            result += f"   Medicamento: {event.medicine_name}\n"
        if event.dosage:
            result += f"   Dosis: {event.dosage}\n"
        if event.next_dose_date:
            result += f"   Próxima dosis: {event.next_dose_date}\n"
        if event.veterinarian_name:
            result += f"   Veterinario: {event.veterinarian_name}\n"
        if event.notes:
            result += f"   Notas: {event.notes}\n"
        result += "\n"
    
    return result


def get_upcoming_vaccines_tool(db: Session, days: int = 30) -> str:
    """Obtiene las vacunas próximas a aplicar en los próximos X días"""
    health_repo = HealthEventRepository(db)
    cattle_repo = CattleRepository(db)
    
    current_date = date.today()
    events = health_repo.get_upcoming_doses(current_date, limit=50)
    
    # Filtrar solo las que están dentro del rango de días
    upcoming = [e for e in events if e.next_dose_date <= current_date + timedelta(days=days)]
    
    if not upcoming:
        return f"No hay vacunas programadas para los próximos {days} días."
    
    result = f"Vacunas y tratamientos programados para los próximos {days} días:\n\n"
    for event in upcoming:
        cattle = cattle_repo.get_by_id(event.cattle_id)
        days_remaining = (event.next_dose_date - current_date).days
        
        result += f"📌 {cattle.name} (Lote: {cattle.lote})\n"
        result += f"   Fecha: {event.next_dose_date} ({days_remaining} días)\n"
        result += f"   Tipo: {event.event_type.value}\n"
        if event.medicine_name:
            result += f"   Medicamento: {event.medicine_name}\n"
        if event.dosage:
            result += f"   Dosis: {event.dosage}\n"
        result += "\n"
    
    return result


def get_last_vaccine_tool(db: Session, lote: str, vaccine_name: Optional[str] = None) -> str:
    """Obtiene la última vacuna aplicada a un ganado específico"""
    cattle_repo = CattleRepository(db)
    cattle = cattle_repo.get_by_lote(lote)
    
    if not cattle:
        return f"No se encontró ganado con el lote '{lote}'."
    
    health_repo = HealthEventRepository(db)
    events = health_repo.get_by_cattle_id(cattle.id, limit=50)
    
    # Filtrar solo vacunas
    from src.models.health_event import EventTypeEnum
    vaccines = [e for e in events if e.event_type == EventTypeEnum.vaccine]
    
    if vaccine_name:
        vaccines = [v for v in vaccines if vaccine_name.lower() in (v.medicine_name or '').lower()]
    
    if not vaccines:
        msg = f"vacuna {vaccine_name}" if vaccine_name else "vacunas"
        return f"El ganado {cattle.name} (Lote: {lote}) no tiene {msg} registradas."
    
    last_vaccine = vaccines[0]  # Ya están ordenadas por fecha descendente
    
    result = f"Última vacuna de {cattle.name} (Lote: {lote}):\n"
    result += f"- Fecha de aplicación: {last_vaccine.application_date}\n"
    result += f"- Vacuna: {last_vaccine.medicine_name or 'No especificada'}\n"
    if last_vaccine.disease_name:
        result += f"- Para: {last_vaccine.disease_name}\n"
    if last_vaccine.next_dose_date:
        result += f"- Próxima dosis: {last_vaccine.next_dose_date}\n"
    if last_vaccine.veterinarian_name:
        result += f"- Veterinario: {last_vaccine.veterinarian_name}\n"
    
    return result


def get_all_upcoming_vaccines_tool(db: Session) -> str:
    """Obtiene TODAS las próximas vacunas/dosis pendientes de todo el ganado"""
    health_repo = HealthEventRepository(db)
    cattle_repo = CattleRepository(db)
    
    current_date = date.today()
    events = health_repo.get_upcoming_doses(current_date, limit=100)
    
    if not events:
        return "No hay vacunas o dosis pendientes programadas."
    
    result = f"Todas las vacunas y dosis pendientes:\n\n"
    for event in events:
        cattle = cattle_repo.get_by_id(event.cattle_id)
        days_remaining = (event.next_dose_date - current_date).days
        
        result += f"📌 {cattle.name} (Lote: {cattle.lote})\n"
        result += f"   Fecha programada: {event.next_dose_date} (en {days_remaining} días)\n"
        result += f"   Tipo: {event.event_type.value}\n"
        if event.medicine_name:
            result += f"   Medicamento: {event.medicine_name}\n"
        if event.dosage:
            result += f"   Dosis: {event.dosage}\n"
        result += "\n"
    
    return result
