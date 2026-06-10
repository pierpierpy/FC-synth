"""Strumenti mock relativi al meteo."""

import random
from datetime import datetime, timedelta

STRUMENTI_METEO = [
    {
        "type": "function",
        "function": {
            "name": "ottieni_meteo_attuale",
            "description": "Ottieni le condizioni meteo attuali per una località specifica",
            "parameters": {
                "type": "object",
                "properties": {
                    "localita": {"type": "string", "description": "Nome della città o coordinate"},
                    "unita": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
                },
                "required": ["localita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_previsioni_meteo",
            "description": "Ottieni le previsioni meteo per i prossimi giorni",
            "parameters": {
                "type": "object",
                "properties": {
                    "localita": {"type": "string", "description": "Nome della città"},
                    "giorni": {"type": "integer", "description": "Numero di giorni di previsione (1-14)", "default": 7}
                },
                "required": ["localita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_allerte_meteo",
            "description": "Ottieni le allerte meteo attive per una regione",
            "parameters": {
                "type": "object",
                "properties": {
                    "regione": {"type": "string", "description": "Nome della regione o città"},
                    "gravita": {"type": "string", "enum": ["tutte", "lieve", "moderata", "grave"], "default": "tutte"}
                },
                "required": ["regione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_qualita_aria",
            "description": "Ottieni l'indice di qualità dell'aria e i livelli di inquinanti",
            "parameters": {
                "type": "object",
                "properties": {
                    "localita": {"type": "string", "description": "Città o indirizzo"},
                    "includi_previsioni": {"type": "boolean", "default": False}
                },
                "required": ["localita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_indice_uv",
            "description": "Ottieni l'indice UV e raccomandazioni per l'esposizione solare",
            "parameters": {
                "type": "object",
                "properties": {
                    "localita": {"type": "string"},
                    "data": {"type": "string", "description": "Data nel formato AAAA-MM-GG"}
                },
                "required": ["localita"]
            }
        }
    },
]
