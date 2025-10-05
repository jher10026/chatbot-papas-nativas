from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
from datetime import datetime
import json
import requests

# TU API KEY DE GOOGLE GEMINI
import os
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDJIpMnLezov_CzsTCxFGK8xCQF_oWpRE0')
# REEMPLAZA CON TU KEY
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyDJIpMnLezov_CzsTCxFGK8xCQF_oWpRE0"

# Configurar logging
logging.basicConfig(
    filename='chatbot_analytics.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Base de conocimiento
CONOCIMIENTO_PAPAS = """
Eres un asistente experto sobre papas nativas del Perú. Responde de forma natural y amigable.

VARIEDADES:
1. Papa Amarilla: Cremosa, ideal para causa/puré. Regiones: Junín, Huánuco. Precio: S/4-5.50/kg
2. Papa Huayro: Firme, ideal para pachamanca/guisos. Regiones: Cusco, Apurímac. Precio: S/3.50-4.50/kg
3. Papa Negra/Morada: Rica en antioxidantes. Ideal para ensaladas/chips. Precio: S/4-5/kg
4. Papa Peruanita: Similar a amarilla, versátil. Precio: S/4/kg
5. Papa Huamantanga: Piel rosada. Precio: S/4.50-6/kg
6. Papa Canchan: Comercial, uso general. Precio: S/2.50-3.50/kg

DATOS CLAVE:
- Perú: 3,800+ variedades (76% mundial)
- Domesticada hace 8,000 años (Lago Titicaca)
- Regiones: Puno (19%), Cusco (12%), Huancavelica (11%), Junín (10%), Apurímac (8%)
- Cultivo: 3,000-4,200 msnm. Siembra sep-dic, cosecha abr-jun
- Nutrición: Vitamina C (20-30mg/100g), Potasio (400-500mg), antioxidantes

USOS CULINARIOS:
- Papa amarilla: Causa, huancaína, puré, ocopa
- Papa huayro: Pachamanca, carapulcra, guisos
- Papa morada: Ensaladas, chips gourmet

CONSERVACIÓN:
- Lugar fresco (7-10°C), oscuro, seco
- NO refrigerar
- Duración: 2-3 meses

HISTORIA:
- 8,000 años de cultivo
- Los incas crearon el chuño (papa deshidratada)
- Llegó a Europa en 1570
- 4° cultivo más importante del mundo

Responde de forma conversacional, usa emojis ocasionalmente 🥔, sé conciso pero informativo.
"""


def llamar_gemini(pregunta):
    """Función para llamar a Gemini API"""
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{CONOCIMIENTO_PAPAS}\n\nPregunta del usuario: {pregunta}\n\nRespuesta (natural y conversacional):"
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 1024,
                "topP": 0.9
            }
        }
        
        response = requests.post(
            GEMINI_URL,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=15
        )
        
        # Debug: imprimir respuesta completa
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar estructura de respuesta
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                
                if 'content' in candidate and 'parts' in candidate['content']:
                    texto = candidate['content']['parts'][0]['text']
                    return texto.strip()
                else:
                    logging.error(f"Estructura inesperada: {data}")
                    return None
            else:
                logging.error(f"No hay candidatos en la respuesta: {data}")
                return None
        else:
            logging.error(f"Error API Gemini: {response.status_code} - {response.text}")
            return None
            
    except KeyError as e:
        logging.error(f"Error de estructura en respuesta: {e}")
        print(f"Error KeyError: {e}")
        return None
    except Exception as e:
        logging.error(f"Error llamando a Gemini: {e}")
        print(f"Error general: {e}")
        return None


class ActionRespuestaIA(Action):
    """Acción principal con IA de Gemini"""
    
    def name(self) -> Text:
        return "action_respuesta_ia"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mensaje_usuario = tracker.latest_message.get('text', '')
        
        # Llamar a Gemini
        respuesta = llamar_gemini(mensaje_usuario)
        
        if respuesta:
            dispatcher.utter_message(text=respuesta)
            self._log_interaccion(tracker.sender_id, mensaje_usuario, True)
        else:
            dispatcher.utter_message(
                text="Disculpa, tuve un problema procesando tu pregunta. ¿Podrías reformularla de otra manera? 🤔"
            )
            self._log_interaccion(tracker.sender_id, mensaje_usuario, False)
        
        return []
    
    def _log_interaccion(self, user_id: str, pregunta: str, exitoso: bool):
        log_data = {
            "evento": "respuesta_ia",
            "usuario": user_id,
            "pregunta": pregunta,
            "exitoso": exitoso,
            "timestamp": datetime.now().isoformat()
        }
        logging.info(json.dumps(log_data))


class ActionConsultarVariedad(Action):
    """Consultar variedad específica con IA"""
    
    def name(self) -> Text:
        return "action_consultar_variedad"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mensaje_usuario = tracker.latest_message.get('text', '')
        
        # Mejorar el prompt para variedades específicas
        pregunta_mejorada = f"Dame información detallada y organizada sobre esta variedad de papa: {mensaje_usuario}. Incluye características, usos, regiones, precio y datos curiosos."
        
        respuesta = llamar_gemini(pregunta_mejorada)
        
        if respuesta:
            dispatcher.utter_message(text=respuesta)
        else:
            dispatcher.utter_message(text="No pude obtener información sobre esa variedad ahora. ¿Intentamos de nuevo? 🥔")
        
        return []


class ActionBuscarReceta(Action):
    """Buscar recetas con IA"""
    
    def name(self) -> Text:
        return "action_buscar_receta"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mensaje_usuario = tracker.latest_message.get('text', '')
        
        pregunta_mejorada = f"Receta peruana con papas nativas: {mensaje_usuario}. Incluye papa ideal, ingredientes, preparación, tiempo y dificultad."
        
        respuesta = llamar_gemini(pregunta_mejorada)
        
        if respuesta:
            dispatcher.utter_message(text=respuesta)
        else:
            dispatcher.utter_message(text="No encontré la receta. ¿Quieres saber sobre otra preparación? 👨‍🍳")
        
        return []


class ActionRegistrarConversacion(Action):
    """Registrar conversación en analytics"""
    
    def name(self) -> Text:
        return "action_registrar_conversacion"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_id = tracker.sender_id
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        confidence = tracker.latest_message.get('intent', {}).get('confidence', 0)
        
        log_data = {
            "evento": "interaccion",
            "usuario": user_id,
            "intent": intent,
            "confianza": confidence,
            "timestamp": datetime.now().isoformat()
        }
        logging.info(json.dumps(log_data))
        
        return []