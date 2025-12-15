# src/services/tools/reminder_tools.py
from datetime import date
from sqlalchemy.orm import Session

from src.repositories import ReminderRepository, CattleRepository
from src.schemas.reminder import ReminderCreate, ReminderTypeEnum


def create_reminder_tool(db: Session, title: str, date_str: str, type_str: str = "other", description: str = None, cattle_lote: str = None) -> str:
    """Crea un nuevo recordatorio"""
    try:
        # Validar fecha
        try:
            reminder_date = date.fromisoformat(date_str)
        except ValueError:
            return f"Error: La fecha debe tener formato YYYY-MM-DD. Recibido: {date_str}"
            
        # Validar tipo
        try:
            reminder_type = ReminderTypeEnum(type_str.lower())
        except ValueError:
            valid_types = [t.value for t in ReminderTypeEnum]
            return f"Error: Tipo inválido '{type_str}'. Tipos válidos: {', '.join(valid_types)}"
            
        cattle_id = None
        if cattle_lote:
            cattle_repo = CattleRepository(db)
            cattle = cattle_repo.get_by_lote(cattle_lote)
            if not cattle:
                return f"Error: No se encontró ganado con el lote '{cattle_lote}'"
            cattle_id = cattle.id
            
        reminder_data = ReminderCreate(
            title=title,
            description=description,
            reminder_date=reminder_date,
            reminder_type=reminder_type,
            cattle_id=cattle_id
        )
        
        repo = ReminderRepository(db)
        new_reminder = repo.create(reminder_data)
        
        return f"✅ Recordatorio creado: '{new_reminder.title}' para el {new_reminder.reminder_date}"
        
    except Exception as e:
        return f"Error al crear recordatorio: {str(e)}"


def get_all_reminders_tool(db: Session) -> str:
    """Obtiene todos los recordatorios pendientes"""
    repo = ReminderRepository(db)
    reminders = repo.get_pending(limit=50)
    
    if not reminders:
        return "No hay recordatorios pendientes."
    
    result = "Recordatorios pendientes:\n\n"
    for reminder in reminders:
        days_until = (reminder.reminder_date - date.today()).days
        status_text = "⚠️ VENCIDO" if days_until < 0 else f"en {days_until} días"
        
        result += f"📋 {reminder.title}\n"
        result += f"   Fecha: {reminder.reminder_date} ({status_text})\n"
        result += f"   Tipo: {reminder.reminder_type}\n"
        if reminder.description:
            result += f"   Descripción: {reminder.description}\n"
        result += "\n"
    
    return result


def get_upcoming_reminders_tool(db: Session, days: int = 7) -> str:
    """Obtiene recordatorios para los próximos X días"""
    repo = ReminderRepository(db)
    reminders = repo.get_upcoming(days=days, limit=50)
    
    if not reminders:
        return f"No hay recordatorios para los próximos {days} días."
    
    result = f"Recordatorios para los próximos {days} días:\n\n"
    for reminder in reminders:
        days_until = (reminder.reminder_date - date.today()).days
        
        result += f"📋 {reminder.title}\n"
        result += f"   Fecha: {reminder.reminder_date} (en {days_until} días)\n"
        result += f"   Tipo: {reminder.reminder_type}\n"
        if reminder.description:
            result += f"   Descripción: {reminder.description}\n"
        result += "\n"
    
    return result


def get_overdue_reminders_tool(db: Session) -> str:
    """Obtiene recordatorios vencidos"""
    repo = ReminderRepository(db)
    reminders = repo.get_overdue(limit=50)
    
    if not reminders:
        return "No hay recordatorios vencidos. ¡Todo al día!"
    
    result = "⚠️ Recordatorios VENCIDOS:\n\n"
    for reminder in reminders:
        days_overdue = (date.today() - reminder.reminder_date).days
        
        result += f"❗ {reminder.title}\n"
        result += f"   Fecha: {reminder.reminder_date} (hace {days_overdue} días)\n"
        result += f"   Tipo: {reminder.reminder_type}\n"
        if reminder.description:
            result += f"   Descripción: {reminder.description}\n"
        result += "\n"
    
    return result


def get_reminders_by_cattle_tool(db: Session, lote: str) -> str:
    """Obtiene recordatorios de un ganado específico"""
    cattle_repo = CattleRepository(db)
    cattle = cattle_repo.get_by_lote(lote)
    
    if not cattle:
        return f"No se encontró ganado con el lote '{lote}'."
    
    reminder_repo = ReminderRepository(db)
    reminders = reminder_repo.get_by_cattle_id(cattle.id, limit=20)
    
    if not reminders:
        return f"No hay recordatorios para {cattle.name} (Lote: {lote})."
    
    result = f"Recordatorios de {cattle.name} (Lote: {lote}):\n\n"
    for reminder in reminders:
        result += f"📋 {reminder.title}\n"
        result += f"   Fecha: {reminder.reminder_date}\n"
        result += f"   Estado: {reminder.status}\n"
        result += f"   Tipo: {reminder.reminder_type}\n"
        if reminder.description:
            result += f"   Descripción: {reminder.description}\n"
        result += "\n"
    
    return result
