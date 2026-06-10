"""Strumenti mock per media e intrattenimento."""

import random
from datetime import datetime, timedelta

STRUMENTI_MEDIA = [
    {
        "type": "function",
        "function": {
            "name": "cerca_film",
            "description": "Cerca film per titolo, genere o attore",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "genere": {"type": "string", "enum": ["azione", "commedia", "drammatico", "horror", "fantascienza", "romantico", "thriller"]},
                    "anno": {"type": "integer"},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_dettagli_film",
            "description": "Ottieni informazioni dettagliate su un film",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_film": {"type": "string"},
                    "titolo": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_disponibilita_streaming",
            "description": "Verifica su quali piattaforme streaming è disponibile un film/serie",
            "parameters": {
                "type": "object",
                "properties": {
                    "titolo": {"type": "string"},
                    "paese": {"type": "string", "default": "IT"}
                },
                "required": ["titolo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_palinsesto_tv",
            "description": "Ottieni il palinsesto televisivo",
            "parameters": {
                "type": "object",
                "properties": {
                    "canale": {"type": "string"},
                    "data": {"type": "string", "description": "Data (AAAA-MM-GG)"},
                    "solo_prima_serata": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_episodi_podcast",
            "description": "Ottieni gli episodi di un podcast",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_podcast": {"type": "string"},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": ["nome_podcast"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_risultati_sport",
            "description": "Ottieni risultati sportivi in tempo reale o recenti",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "enum": ["calcio", "basket", "tennis", "f1", "moto_gp"]},
                    "campionato": {"type": "string"},
                    "squadra": {"type": "string"}
                },
                "required": ["sport"]
            }
        }
    },
]
