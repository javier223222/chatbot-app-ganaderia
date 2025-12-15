"""
Script para inicializar la base de datos creando todas las tablas
"""
from src.infrastructure.database import engine, Base
from src.models import Cattle, HealthEvent, HeatEventModel, Reminder


def init_db():
    """Crea todas las tablas en la base de datos"""
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente!")
    print("\nTablas creadas:")
    print("- cattle")
    print("- health_events")
    print("- heat_events")
    print("- reminders")


if __name__ == "__main__":
    init_db()
