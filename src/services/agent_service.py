# src/services/agent_service.py
import os
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from src.core.config import settings
from src.services.tools import cattle_tools, health_tools, heat_tools, reminder_tools


class LivestockTools:
    """Clase contenedora para las herramientas, vinculando la sesión de DB"""
    def __init__(self, db: Session):
        self.db = db

    def create_cattle(self, name: str, lote: str, gender: str, breed: str = None, weight: float = None, birth_date: str = None):
        """Registra nuevo ganado. gender debe ser 'male' o 'female'. birth_date formato 'YYYY-MM-DD'."""
        return cattle_tools.create_cattle_tool(self.db, name, lote, gender, breed, weight, birth_date)

    def get_all_cattle(self, limit: int = 50):
        """Lista todo el ganado registrado"""
        return cattle_tools.get_all_cattle_tool(self.db, limit)

    def search_cattle_by_name(self, name: str):
        """Busca ganado por nombre"""
        return cattle_tools.search_cattle_by_name_tool(self.db, name)

    def get_cattle_by_lote(self, lote: str):
        """Obtiene información de un ganado por su lote (ej: 'LOTE-001')"""
        return cattle_tools.get_cattle_by_lote_tool(self.db, lote)

    def get_cattle_by_gender(self, gender: str):
        """Filtra ganado por género ('male' o 'female')"""
        return cattle_tools.get_cattle_by_gender_tool(self.db, gender)

    def get_health_events_by_cattle(self, lote: str):
        """Historial de salud de un ganado"""
        return health_tools.get_health_events_by_cattle_tool(self.db, lote)

    def get_upcoming_vaccines(self, days: int = 30):
        """Vacunas próximas en X días"""
        return health_tools.get_upcoming_vaccines_tool(self.db, days)

    def get_last_vaccine(self, lote: str, vaccine_name: str = None):
        """Última vacuna de un ganado"""
        return health_tools.get_last_vaccine_tool(self.db, lote, vaccine_name)

    def get_all_upcoming_vaccines(self):
        """TODAS las vacunas pendientes"""
        return health_tools.get_all_upcoming_vaccines_tool(self.db)

    def get_heat_events_by_cattle(self, lote: str):
        """Historial de celo de un ganado"""
        return heat_tools.get_heat_events_by_cattle_tool(self.db, lote)

    def get_pregnant_cattle(self):
        """Lista de ganado con embarazo confirmado"""
        return heat_tools.get_pregnant_cattle_tool(self.db)

    def get_pending_pregnancy_checks(self):
        """Ganado que necesita chequeo de embarazo"""
        return heat_tools.get_pending_pregnancy_checks_tool(self.db)

    def get_last_heat(self, lote: str):
        """Último evento de celo de un ganado"""
        return heat_tools.get_last_heat_tool(self.db, lote)

    def create_reminder(self, title: str, date_str: str, type_str: str = "other", description: str = None, cattle_lote: str = None):
        """Crea un recordatorio. date_str formato 'YYYY-MM-DD'. type_str: 'vaccine', 'checkup', 'treatment', 'feeding', 'breeding', 'other'."""
        return reminder_tools.create_reminder_tool(self.db, title, date_str, type_str, description, cattle_lote)

    def get_all_reminders(self):
        """Todos los recordatorios pendientes"""
        return reminder_tools.get_all_reminders_tool(self.db)

    def get_upcoming_reminders(self, days: int = 7):
        """Recordatorios próximos en X días"""
        return reminder_tools.get_upcoming_reminders_tool(self.db, days)

    def get_overdue_reminders(self):
        """Recordatorios vencidos"""
        return reminder_tools.get_overdue_reminders_tool(self.db)

    def get_reminders_by_cattle(self, lote: str):
        """Recordatorios de un ganado específico"""
        return reminder_tools.get_reminders_by_cattle_tool(self.db, lote)


class AgentService:
    """Servicio del agente de IA usando Function Calling nativo"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_name = "gemini-2.5-flash"
    
    def _get_system_prompt(self) -> str:
        return """Eres un experto en gestión ganadera. Tu trabajo es proporcionar información precisa sobre ganado, salud, celo y recordatorios, y ayudar a registrar nueva información.
        
Usa las herramientas disponibles para responder a las preguntas del usuario.
Si el usuario menciona un número de lote (ej: "vaca 504"), asume que es "LOTE-504".
NO uses emojis. Sé directo y profesional.
"""

    async def chat(self, user_message: str) -> Dict[str, Any]:
        try:
            # 1. Preparar herramientas
            tools_instance = LivestockTools(self.db)
            tool_map = {
                "create_cattle": tools_instance.create_cattle,
                "get_all_cattle": tools_instance.get_all_cattle,
                "search_cattle_by_name": tools_instance.search_cattle_by_name,
                "get_cattle_by_lote": tools_instance.get_cattle_by_lote,
                "get_cattle_by_gender": tools_instance.get_cattle_by_gender,
                "get_health_events_by_cattle": tools_instance.get_health_events_by_cattle,
                "get_upcoming_vaccines": tools_instance.get_upcoming_vaccines,
                "get_last_vaccine": tools_instance.get_last_vaccine,
                "get_all_upcoming_vaccines": tools_instance.get_all_upcoming_vaccines,
                "get_heat_events_by_cattle": tools_instance.get_heat_events_by_cattle,
                "get_pregnant_cattle": tools_instance.get_pregnant_cattle,
                "get_pending_pregnancy_checks": tools_instance.get_pending_pregnancy_checks,
                "get_last_heat": tools_instance.get_last_heat,
                "create_reminder": tools_instance.create_reminder,
                "get_all_reminders": tools_instance.get_all_reminders,
                "get_upcoming_reminders": tools_instance.get_upcoming_reminders,
                "get_overdue_reminders": tools_instance.get_overdue_reminders,
                "get_reminders_by_cattle": tools_instance.get_reminders_by_cattle,
            }
            
            tool_list = list(tool_map.values())

            # 2. Configuración
            config = types.GenerateContentConfig(
                tools=tool_list,
                system_instruction=self._get_system_prompt(),
                temperature=0.2
            )

            # 3. Primera llamada (Usuario -> Modelo)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=config
            )

            # 4. Verificar si hay llamadas a función
            tool_used_name = None
            tool_result_str = None
            tool_params = None
            
            # Debug: Imprimir respuesta cruda para diagnóstico
            print(f"DEBUG: Response candidates: {len(response.candidates)}")
            if response.candidates:
                print(f"DEBUG: Candidate 0 parts: {len(response.candidates[0].content.parts)}")
                for i, part in enumerate(response.candidates[0].content.parts):
                    print(f"DEBUG: Part {i} has function_call: {part.function_call is not None}")
                    if part.function_call:
                        print(f"DEBUG: Function call name: {part.function_call.name}")

            # Verificar function_calls en la respuesta (SDK v0.2+)
            # A veces response.function_calls puede estar vacío pero candidates[0].content.parts[0].function_call existe
            function_call = None
            
            if response.function_calls:
                function_call = response.function_calls[0]
            elif response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_call = part.function_call
                        break
            
            if function_call:
                tool_name = function_call.name
                tool_args = function_call.args
                
                print(f"DEBUG: Executing tool {tool_name} with args {tool_args}")
                
                tool_used_name = tool_name
                tool_params = tool_args

                if tool_name in tool_map:
                    try:
                        result = tool_map[tool_name](**tool_args)
                        tool_result_str = str(result)
                    except Exception as e:
                        tool_result_str = f"Error al ejecutar herramienta: {str(e)}"
                    
                    # 5. Segunda llamada (Resultado -> Modelo)
                    from google.genai.types import Content, Part
                    
                    user_content = Content(role="user", parts=[Part.from_text(user_message)])
                    model_content = response.candidates[0].content
                    
                    # Construir respuesta de herramienta correctamente
                    function_content = Content(role="tool", parts=[Part.from_function_response(
                        name=tool_name,
                        response={"result": tool_result_str}
                    )])
                    
                    final_response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[user_content, model_content, function_content],
                        config=config
                    )
                    
                    return {
                        "response": final_response.text,
                        "tool_used": tool_used_name,
                        "tool_params": tool_params,
                        "tool_result": tool_result_str
                    }
            
            return {
                "response": response.text,
                "tool_used": None
            }

        except Exception as e:
            return {
                "response": f"Error en el agente: {str(e)}",
                "error": str(e)
            }
