"""Strumenti mock per viaggi e trasporti."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible, safe_int

STRUMENTI_VIAGGI = [
    {
        "type": "function",
        "function": {
            "name": "cerca_voli",
            "description": "Cerca voli disponibili tra due città",
            "parameters": {
                "type": "object",
                "properties": {
                    "origine": {"type": "string", "description": "Codice aeroporto o città di partenza"},
                    "destinazione": {"type": "string", "description": "Codice aeroporto o città di arrivo"},
                    "data_partenza": {"type": "string", "description": "Data (AAAA-MM-GG)"},
                    "data_ritorno": {"type": "string", "description": "Data di ritorno per andata e ritorno"},
                    "passeggeri": {"type": "integer", "default": 1},
                    "classe": {"type": "string", "enum": ["economy", "business", "first"], "default": "economy"}
                },
                "required": ["origine", "destinazione", "data_partenza"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_hotel",
            "description": "Cerca hotel disponibili in una località",
            "parameters": {
                "type": "object",
                "properties": {
                    "localita": {"type": "string"},
                    "check_in": {"type": "string", "description": "Data di check-in (AAAA-MM-GG)"},
                    "check_out": {"type": "string", "description": "Data di check-out"},
                    "ospiti": {"type": "integer", "default": 2},
                    "camere": {"type": "integer", "default": 1},
                    "stelle_minime": {"type": "integer", "description": "Stelle minime dell'hotel (1-5)"}
                },
                "required": ["localita", "check_in", "check_out"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_treni",
            "description": "Cerca collegamenti ferroviari",
            "parameters": {
                "type": "object",
                "properties": {
                    "stazione_partenza": {"type": "string"},
                    "stazione_arrivo": {"type": "string"},
                    "data": {"type": "string"},
                    "ora": {"type": "string", "description": "Ora di partenza preferita (HH:MM)"},
                    "passeggeri": {"type": "integer", "default": 1}
                },
                "required": ["stazione_partenza", "stazione_arrivo", "data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prenota_taxi",
            "description": "Prenota un taxi o una corsa",
            "parameters": {
                "type": "object",
                "properties": {
                    "luogo_partenza": {"type": "string"},
                    "destinazione": {"type": "string"},
                    "orario_partenza": {"type": "string", "description": "Orario di partenza (formato ISO) o 'adesso'"},
                    "tipo_veicolo": {"type": "string", "enum": ["standard", "premium", "xl", "eco"], "default": "standard"}
                },
                "required": ["luogo_partenza", "destinazione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_indicazioni",
            "description": "Ottieni indicazioni e informazioni sul percorso tra due punti",
            "parameters": {
                "type": "object",
                "properties": {
                    "origine": {"type": "string"},
                    "destinazione": {"type": "string"},
                    "modalita": {"type": "string", "enum": ["auto", "piedi", "trasporto_pubblico", "bicicletta"], "default": "auto"},
                    "evita": {"type": "array", "items": {"type": "string"}, "description": "Evita pedaggi, autostrade, traghetti"}
                },
                "required": ["origine", "destinazione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_info_traffico",
            "description": "Ottieni le condizioni del traffico attuali per un percorso o zona",
            "parameters": {
                "type": "object",
                "properties": {
                    "percorso": {"type": "string", "description": "Nome del percorso o dell'autostrada"},
                    "zona": {"type": "string", "description": "Città o regione"}
                },
                "required": []
            }
        }
    },
]
