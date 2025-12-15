# src/services/tools/heat_tools.py
from datetime import date
from sqlalchemy.orm import Session

from src.repositories import HeatEventRepository, CattleRepository


def get_heat_events_by_cattle_tool(db: Session, lote: str) -> str:
    """Obtiene el historial de eventos de celo de un ganado"""
    cattle_repo = CattleRepository(db)
    cattle = cattle_repo.get_by_lote(lote)
    
    if not cattle:
        return f"No se encontró ganado con el lote '{lote}'."
    
    heat_repo = HeatEventRepository(db)
    events = heat_repo.get_by_cattle_id(cattle.id, limit=20)
    
    if not events:
        return f"El ganado {cattle.name} (Lote: {lote}) no tiene eventos de celo registrados."
    
    result = f"Historial de celo de {cattle.name} (Lote: {lote}):\n\n"
    for event in events:
        result += f"📅 {event.heat_date}\n"
        result += f"   Permite monta: {'Sí' if event.allows_mounting else 'No'}\n"
        if event.was_inseminated:
            result += f"   ✅ Inseminada: {event.insemination_date}\n"
            if event.pregnancy_confirmed is not None:
                status = "✅ Confirmado" if event.pregnancy_confirmed else "❌ No confirmado"
                result += f"   Embarazo: {status}\n"
        result += "\n"
    
    return result


def get_pregnant_cattle_tool(db: Session) -> str:
    """Obtiene la lista de ganado con embarazo confirmado"""
    heat_repo = HeatEventRepository(db)
    cattle_repo = CattleRepository(db)
    
    events = heat_repo.get_confirmed_pregnancies(limit=50)
    
    if not events:
        return "No hay ganado con embarazo confirmado."
    
    result = "Ganado con embarazo confirmado:\n\n"
    for event in events:
        cattle = cattle_repo.get_by_id(event.cattle_id)
        result += f"🐮 {cattle.name} (Lote: {cattle.lote})\n"
        result += f"   Fecha de celo: {event.heat_date}\n"
        result += f"   Fecha de inseminación: {event.insemination_date}\n"
        
        if event.insemination_date:
            days_pregnant = (date.today() - event.insemination_date).days
            result += f"   Días de gestación: ~{days_pregnant} días\n"
        
        result += "\n"
    
    return result


def get_pending_pregnancy_checks_tool(db: Session) -> str:
    """Obtiene ganado inseminado que necesita confirmación de embarazo"""
    heat_repo = HeatEventRepository(db)
    cattle_repo = CattleRepository(db)
    
    events = heat_repo.get_pending_pregnancy_check(days_after_insemination=45, limit=50)
    
    if not events:
        return "No hay ganado pendiente de confirmación de embarazo."
    
    result = "Ganado que necesita confirmación de embarazo:\n\n"
    for event in events:
        cattle = cattle_repo.get_by_id(event.cattle_id)
        days_since = (date.today() - event.insemination_date).days
        
        result += f"🐮 {cattle.name} (Lote: {cattle.lote})\n"
        result += f"   Inseminada: {event.insemination_date} (hace {days_since} días)\n"
        result += f"   ⚠️ Requiere chequeo de embarazo\n"
        result += "\n"
    
    return result


def get_last_heat_tool(db: Session, lote: str) -> str:
    """Obtiene el último evento de celo de un ganado"""
    cattle_repo = CattleRepository(db)
    cattle = cattle_repo.get_by_lote(lote)
    
    if not cattle:
        return f"No se encontró ganado con el lote '{lote}'."
    
    heat_repo = HeatEventRepository(db)
    last_heat = heat_repo.get_last_heat(cattle.id)
    
    if not last_heat:
        return f"El ganado {cattle.name} (Lote: {lote}) no tiene eventos de celo registrados."
    
    result = f"Último celo de {cattle.name} (Lote: {lote}):\n"
    result += f"- Fecha: {last_heat.heat_date}\n"
    result += f"- Permite monta: {'Sí' if last_heat.allows_mounting else 'No'}\n"
    
    if last_heat.was_inseminated:
        result += f"- Inseminada: {last_heat.insemination_date}\n"
        if last_heat.pregnancy_confirmed is not None:
            result += f"- Embarazo confirmado: {'Sí' if last_heat.pregnancy_confirmed else 'No'}\n"
    
    if last_heat.comportamiento:
        result += f"- Comportamiento: {last_heat.comportamiento}\n"
    
    return result
