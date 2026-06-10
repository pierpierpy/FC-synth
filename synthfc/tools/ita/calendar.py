"""Strumenti mock per calendario e pianificazione."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible, safe_int

STRUMENTI_CALENDARIO = [
    {
        "type": "function",
        "function": {
            "name": "ottieni_eventi_calendario",
            "description": "Ottieni gli eventi del calendario per un intervallo di date specifico",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_inizio": {"type": "string", "description": "Data di inizio (AAAA-MM-GG)"},
                    "data_fine": {"type": "string", "description": "Data di fine (AAAA-MM-GG)"},
                    "id_calendario": {"type": "string", "default": "principale"}
                },
                "required": ["data_inizio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_evento_calendario",
            "description": "Crea un nuovo evento o appuntamento nel calendario",
            "parameters": {
                "type": "object",
                "properties": {
                    "titolo": {"type": "string", "description": "Titolo dell'evento"},
                    "ora_inizio": {"type": "string", "description": "Data e ora di inizio (formato ISO)"},
                    "ora_fine": {"type": "string", "description": "Data e ora di fine (formato ISO)"},
                    "luogo": {"type": "string"},
                    "descrizione": {"type": "string"},
                    "partecipanti": {"type": "array", "items": {"type": "string"}, "description": "Lista di indirizzi email"},
                    "minuti_promemoria": {"type": "integer", "default": 30}
                },
                "required": ["titolo", "ora_inizio", "ora_fine"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "elimina_evento_calendario",
            "description": "Elimina un evento del calendario tramite ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_evento": {"type": "string", "description": "Identificativo dell'evento"}
                },
                "required": ["id_evento"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "aggiorna_evento_calendario",
            "description": "Aggiorna un evento esistente nel calendario",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_evento": {"type": "string"},
                    "titolo": {"type": "string"},
                    "ora_inizio": {"type": "string"},
                    "ora_fine": {"type": "string"},
                    "luogo": {"type": "string"},
                    "descrizione": {"type": "string"}
                },
                "required": ["id_evento"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trova_slot_liberi",
            "description": "Trova fasce orarie disponibili per la pianificazione",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "Data da verificare (AAAA-MM-GG)"},
                    "durata_minuti": {"type": "integer", "description": "Durata richiesta in minuti"},
                    "solo_orario_lavorativo": {"type": "boolean", "default": True}
                },
                "required": ["data", "durata_minuti"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "imposta_promemoria",
            "description": "Imposta un promemoria per un orario specifico",
            "parameters": {
                "type": "object",
                "properties": {
                    "messaggio": {"type": "string", "description": "Testo del promemoria"},
                    "data_ora": {"type": "string", "description": "Quando ricordare (formato ISO)"},
                    "ripeti": {"type": "string", "enum": ["nessuno", "giornaliero", "settimanale", "mensile"], "default": "nessuno"}
                },
                "required": ["messaggio", "data_ora"]
            }
        }
    },
]
