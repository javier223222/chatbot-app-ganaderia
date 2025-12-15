# src/services/agent_service.py
import os
from typing import Dict, Any
from sqlalchemy.orm import Session
from google import genai

from src.core.config import settings
from src.services.tools import cattle_tools, health_tools, heat_tools, reminder_tools


class AgentService:
    """Servicio del agente de IA para consultas en lenguaje natural"""
    
    def __init__(self, db: Session):
        self.db = db
        
       
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_name = "gemini-2.5-flash"
        
        # Definir herramientas disponibles
        self.tools = {
            # Herramientas de ganado
            "create_cattle": cattle_tools.create_cattle_tool,
            "get_all_cattle": cattle_tools.get_all_cattle_tool,
            "search_cattle_by_name": cattle_tools.search_cattle_by_name_tool,
            "get_cattle_by_lote": cattle_tools.get_cattle_by_lote_tool,
            "get_cattle_by_gender": cattle_tools.get_cattle_by_gender_tool,
            
            # Herramientas de salud
            "get_health_events_by_cattle": health_tools.get_health_events_by_cattle_tool,
            "get_upcoming_vaccines": health_tools.get_upcoming_vaccines_tool,
            "get_last_vaccine": health_tools.get_last_vaccine_tool,
            "get_all_upcoming_vaccines": health_tools.get_all_upcoming_vaccines_tool,
            
            # Herramientas de celo
            "get_heat_events_by_cattle": heat_tools.get_heat_events_by_cattle_tool,
            "get_pregnant_cattle": heat_tools.get_pregnant_cattle_tool,
            "get_pending_pregnancy_checks": heat_tools.get_pending_pregnancy_checks_tool,
            "get_last_heat": heat_tools.get_last_heat_tool,
            
            # Herramientas de recordatorios
            "create_reminder": reminder_tools.create_reminder_tool,
            "get_all_reminders": reminder_tools.get_all_reminders_tool,
            "get_upcoming_reminders": reminder_tools.get_upcoming_reminders_tool,
            "get_overdue_reminders": reminder_tools.get_overdue_reminders_tool,
            "get_reminders_by_cattle": reminder_tools.get_reminders_by_cattle_tool,
        }
    
    def _get_system_prompt(self) -> str:
        """Genera el prompt del sistema con descripción de herramientas"""
        return f"""Eres un experto en gestión ganadera. Tu trabajo es proporcionar información precisa sobre ganado, salud, celo y recordatorios, y ayudar a registrar nueva información.

Tienes acceso a las siguientes herramientas para consultar y modificar la base de datos:

HERRAMIENTAS DE CREACIÓN (ACCIONES):
- create_cattle(name, lote, gender, breed=None, weight=None, birth_date=None): Registra nuevo ganado. gender debe ser "male" o "female". birth_date formato "YYYY-MM-DD".
- create_reminder(title, date_str, type_str="other", description=None, cattle_lote=None): Crea un recordatorio. date_str formato "YYYY-MM-DD". type_str: "vaccine", "checkup", "treatment", "feeding", "breeding", "other".

HERRAMIENTAS DE GANADO:
- get_all_cattle(limit=50): Lista todo el ganado registrado
- search_cattle_by_name(name): Busca ganado por nombre
- get_cattle_by_lote(lote): Obtiene información de un ganado por su lote (ej: "LOTE-001")
- get_cattle_by_gender(gender): Filtra ganado por género ("male" o "female")

HERRAMIENTAS DE SALUD:
- get_health_events_by_cattle(lote): Historial de salud de un ganado
- get_upcoming_vaccines(days=30): Vacunas próximas en X días
- get_last_vaccine(lote, vaccine_name=None): Última vacuna de un ganado
- get_all_upcoming_vaccines(): TODAS las vacunas pendientes

HERRAMIENTAS DE CELO/REPRODUCCIÓN:
- get_heat_events_by_cattle(lote): Historial de celo de un ganado
- get_pregnant_cattle(): Lista de ganado con embarazo confirmado
- get_pending_pregnancy_checks(): Ganado que necesita chequeo de embarazo
- get_last_heat(lote): Último evento de celo de un ganado

HERRAMIENTAS DE RECORDATORIOS:
- get_all_reminders(): Todos los recordatorios pendientes
- get_upcoming_reminders(days=7): Recordatorios próximos en X días
- get_overdue_reminders(): Recordatorios vencidos
- get_reminders_by_cattle(lote): Recordatorios de un ganado específico

INSTRUCCIONES:
1. Cuando el usuario pregunte algo, primero analiza qué herramienta(s) necesitas usar
2. Si el usuario quiere CREAR algo (ganado, recordatorio), asegúrate de tener todos los datos obligatorios. Si faltan, PREGUNTA al usuario.
   - Para ganado: Nombre, Lote, Género.
   - Para recordatorio: Título, Fecha.
3. Usa las herramientas apropiadas para obtener la información o realizar la acción.
4. Interpreta la información y responde de forma directa y profesional.
5. Si el usuario menciona un número de lote (ej: "vaca 504", "lote 001"), usa "LOTE-" + número.
6. NO uses emojis ni iconos.
7. NO uses frases de relleno como "Claro", "Aquí tienes la información", "Como modelo de lenguaje".
8. Sé conciso.

Recuerda: Siempre consulta la base de datos antes de responder. NO inventes información.
"""
    
    def _extract_tool_call(self, text: str) -> tuple[str, dict]:
        """Extrae la llamada a herramienta del texto generado"""
        # Buscar patrones como: TOOL: nombre_tool(param1=value1, param2=value2)
        import re
        pattern = r'TOOL:\s*(\w+)\((.*?)\)'
        match = re.search(pattern, text)
        
        if not match:
            return None, {}
        
        tool_name = match.group(1)
        params_str = match.group(2)
        
        # Parsear parámetros
        params = {}
        if params_str.strip():
            for param in params_str.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    # Convertir tipos
                    if value.isdigit():
                        value = int(value)
                    params[key] = value
        
        return tool_name, params
    
    async def chat(self, user_message: str) -> Dict[str, Any]:
        """Procesa un mensaje del usuario y genera una respuesta"""
        try:
            # Crear prompt completo
            full_prompt = f"""{self._get_system_prompt()}

PREGUNTA DEL USUARIO: {user_message}

INSTRUCCIONES PARA RESPONDER:
1. Primero, identifica qué herramienta(s) necesitas usar
2. Si necesitas usar una herramienta, responde EXACTAMENTE en este formato:
   TOOL: nombre_herramienta(parametro1=valor1, parametro2=valor2)
   
3. Si necesitas información antes de usar una herramienta, pregúntale al usuario

Ejemplos:
- "¿Cuándo le toca vacuna a la vaca 504?" → TOOL: get_last_vaccine(lote="LOTE-504")
- "¿Qué ganado está preñado?" → TOOL: get_pregnant_cattle()
- "Muéstrame las vacunas de esta semana" → TOOL: get_upcoming_vaccines(days=7)

Ahora responde:"""

            # Primera llamada al modelo con la nueva API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            response_text = response.text
            
            # Verificar si el modelo quiere usar una herramienta
            tool_name, params = self._extract_tool_call(response_text)
            
            if tool_name and tool_name in self.tools:
                # Ejecutar la herramienta
                tool_function = self.tools[tool_name]
                tool_result = tool_function(self.db, **params)
                
                # Segunda llamada: dar el resultado de la herramienta al modelo
                follow_up_prompt = f"""La herramienta {tool_name} devolvió:

{tool_result}

Ahora, basándote en esta información, responde de forma directa y profesional a la pregunta original del usuario: "{user_message}"

No menciones las herramientas técnicas.
NO uses emojis ni iconos.
NO uses frases introductorias innecesarias.
Solo da la respuesta final."""

                final_response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=follow_up_prompt
                )
                final_text = final_response.text
                
                return {
                    "response": final_text,
                    "tool_used": tool_name,
                    "tool_params": params,
                    "tool_result": tool_result
                }
            else:
                # Respuesta directa sin usar herramientas
                return {
                    "response": response_text,
                    "tool_used": None
                }
                
        except Exception as e:
            return {
                "response": f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}",
                "error": str(e)
            }
