"""
Script para poblar la base de datos con datos de ejemplo
"""
from datetime import date, datetime, timedelta
import uuid
from sqlalchemy.orm import Session

from src.infrastructure.database import SessionLocal
from src.models import Cattle, HealthEvent, HeatEventModel, Reminder
from src.models.cattle import GenderEnum
from src.models.health_event import EventTypeEnum, AdministrationRouteEnum


def create_sample_data():
    """Crea datos de ejemplo en la base de datos"""
    db: Session = SessionLocal()
    
    try:
        # Verificar si ya existen datos
        if db.query(Cattle).first():
            print("⚠️ La base de datos ya contiene datos. Saltando seed.")
            return

        print("🌱 Poblando base de datos con datos de ejemplo...")
        
        # ==================== CATTLE ====================
        print("\n🐮 Creando ganado...")
        
        cattle_1 = Cattle(
            id=uuid.uuid4(),
            name="Margarita",
            lote="LOTE-001",
            breed="Holstein",
            gender=GenderEnum.female,
            birth_date=date(2020, 3, 15),
            weight=450.5,
            fecha_ultimo_parto=date(2024, 6, 10)
        )
        
        cattle_2 = Cattle(
            id=uuid.uuid4(),
            name="Bella",
            lote="LOTE-002",
            breed="Jersey",
            gender=GenderEnum.female,
            birth_date=date(2021, 5, 20),
            weight=380.0,
            fecha_ultimo_parto=date(2024, 8, 15)
        )
        
        cattle_3 = Cattle(
            id=uuid.uuid4(),
            name="Toro Max",
            lote="LOTE-003",
            breed="Angus",
            gender=GenderEnum.male,
            birth_date=date(2019, 11, 5),
            weight=550.0
        )
        
        cattle_4 = Cattle(
            id=uuid.uuid4(),
            lote="LOTE-004",
            name="Luna",
            breed="Simmental",
            gender=GenderEnum.female,
            birth_date=date(2022, 1, 10),
            weight=320.0
        )
        
        db.add_all([cattle_1, cattle_2, cattle_3, cattle_4])
        db.flush()  # Para obtener los IDs
        
        print(f"✅ Creadas 4 cabezas de ganado")
        
        # ==================== HEALTH EVENTS ====================
        print("\n💉 Creando eventos de salud...")
        
        health_event_1 = HealthEvent(
            id=uuid.uuid4(),
            cattle_id=cattle_1.id,
            event_type=EventTypeEnum.vaccine,
            disease_name="Fiebre Aftosa",
            medicine_name="Aftovacuna",
            application_date=date(2024, 10, 1),
            administration_route=AdministrationRouteEnum.intramuscular,
            next_dose_date=date(2025, 4, 1),
            dosage="2ml",
            veterinarian_name="Dr. García",
            notes="Vacunación de rutina"
        )
        
        health_event_2 = HealthEvent(
            id=uuid.uuid4(),
            cattle_id=cattle_1.id,
            event_type=EventTypeEnum.checkup,
            application_date=date(2024, 11, 15),
            veterinarian_name="Dr. García",
            notes="Chequeo general. Animal en buen estado."
        )
        
        health_event_3 = HealthEvent(
            id=uuid.uuid4(),
            cattle_id=cattle_2.id,
            event_type=EventTypeEnum.treatment,
            disease_name="Mastitis",
            medicine_name="Antibiótico Cefalexina",
            application_date=date(2024, 12, 1),
            administration_route=AdministrationRouteEnum.intramuscular,
            treatment_end_date=date(2024, 12, 8),
            dosage="5ml diarios",
            veterinarian_name="Dra. Martínez",
            notes="Tratamiento por infección en ubre"
        )
        
        health_event_4 = HealthEvent(
            id=uuid.uuid4(),
            cattle_id=cattle_3.id,
            event_type=EventTypeEnum.vaccine,
            disease_name="Brucelosis",
            medicine_name="Vacuna RB51",
            application_date=date(2024, 9, 20),
            administration_route=AdministrationRouteEnum.subcutaneous,
            dosage="2ml",
            veterinarian_name="Dr. López"
        )
        
        db.add_all([health_event_1, health_event_2, health_event_3, health_event_4])
        db.flush()
        
        print(f"✅ Creados 4 eventos de salud")
        
        # ==================== HEAT EVENTS ====================
        print("\n🔥 Creando eventos de celo...")
        
        heat_event_1 = HeatEventModel(
            id=uuid.uuid4(),
            cattle_id=cattle_1.id,
            heat_date=date(2024, 11, 20),
            allows_mounting=True,
            vaginal_discharge="Mucoso transparente",
            vulva_swelling="Moderado",
            comportamiento="Inquieta, busca montar otras vacas",
            was_inseminated=True,
            insemination_date=date(2024, 11, 21),
            pregnancy_confirmed=True
        )
        
        heat_event_2 = HeatEventModel(
            id=uuid.uuid4(),
            cattle_id=cattle_2.id,
            heat_date=date(2024, 12, 5),
            allows_mounting=True,
            vaginal_discharge="Mucoso claro",
            vulva_swelling="Leve",
            comportamiento="Nerviosa, mugidos frecuentes",
            was_inseminated=False
        )
        
        heat_event_3 = HeatEventModel(
            id=uuid.uuid4(),
            cattle_id=cattle_4.id,
            heat_date=date(2024, 11, 10),
            allows_mounting=True,
            vaginal_discharge="Mucoso",
            vulva_swelling="Moderado",
            comportamiento="Inquieta",
            was_inseminated=True,
            insemination_date=date(2024, 11, 10),
            pregnancy_confirmed=False
        )
        
        db.add_all([heat_event_1, heat_event_2, heat_event_3])
        db.flush()
        
        print(f"✅ Creados 3 eventos de celo")
        
        # ==================== REMINDERS ====================
        print("\n⏰ Creando recordatorios...")
        
        reminder_1 = Reminder(
            id=uuid.uuid4(),
            cattle_id=cattle_1.id,
            health_event_id=health_event_1.id,
            title="Vacuna de refuerzo - Margarita",
            description="Aplicar segunda dosis de Aftovacuna",
            reminder_date=date(2025, 4, 1),
            reminder_type="vaccine",
            status="pending"
        )
        
        reminder_2 = Reminder(
            id=uuid.uuid4(),
            cattle_id=cattle_1.id,
            title="Chequeo de preñez - Margarita",
            description="Confirmar embarazo después de inseminación",
            reminder_date=date(2025, 1, 20),
            reminder_type="checkup",
            status="pending"
        )
        
        reminder_3 = Reminder(
            id=uuid.uuid4(),
            cattle_id=cattle_2.id,
            health_event_id=health_event_3.id,
            title="Seguimiento tratamiento - Bella",
            description="Revisar evolución de mastitis",
            reminder_date=date(2024, 12, 15),
            reminder_type="checkup",
            status="pending"
        )
        
        reminder_4 = Reminder(
            id=uuid.uuid4(),
            cattle_id=cattle_4.id,
            title="Verificar preñez - Luna",
            description="Chequeo post-inseminación",
            reminder_date=date(2025, 1, 10),
            reminder_type="checkup",
            status="pending"
        )
        
        reminder_5 = Reminder(
            id=uuid.uuid4(),
            title="Revisar inventario de medicamentos",
            description="Verificar stock de vacunas y antibióticos",
            reminder_date=date(2024, 12, 20),
            reminder_type="other",
            status="pending"
        )
        
        db.add_all([reminder_1, reminder_2, reminder_3, reminder_4, reminder_5])
        
        # Commit de todos los cambios
        db.commit()
        
        print("\n" + "="*50)
        print("✅ ¡Base de datos poblada exitosamente!")
        print("="*50)
        print(f"\n📊 Resumen:")
        print(f"   • {db.query(Cattle).count()} cabezas de ganado")
        print(f"   • {db.query(HealthEvent).count()} eventos de salud")
        print(f"   • {db.query(HeatEventModel).count()} eventos de celo")
        print(f"   • {db.query(Reminder).count()} recordatorios")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error al poblar la base de datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
