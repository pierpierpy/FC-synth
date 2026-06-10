"""Strumenti mock per gestione e monitoraggio dei social media."""

import random
from datetime import datetime, timedelta

STRUMENTI_SOCIAL = [
    {
        "type": "function",
        "function": {
            "name": "pubblica_sui_social",
            "description": "Crea e pubblica un post sulle piattaforme social",
            "parameters": {
                "type": "object",
                "properties": {
                    "piattaforme": {"type": "array", "items": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin", "tiktok"]}},
                    "contenuto": {"type": "string", "description": "Testo del post"},
                    "url_media": {"type": "array", "items": {"type": "string"}, "description": "URL dei media da allegare"},
                    "orario_programmato": {"type": "string", "description": "Data e ora ISO per programmare il post"},
                    "hashtag": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["piattaforme", "contenuto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_analytics_social",
            "description": "Ottieni dati analytics per gli account social",
            "parameters": {
                "type": "object",
                "properties": {
                    "piattaforma": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin", "tiktok", "tutte"]},
                    "metrica": {"type": "string", "enum": ["engagement", "copertura", "follower", "click", "impressioni"]},
                    "periodo": {"type": "string", "enum": ["24h", "7g", "30g", "90g"]},
                    "confronta_precedente": {"type": "boolean", "default": False}
                },
                "required": ["piattaforma"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_menzioni",
            "description": "Ottieni menzioni e tag del tuo account o brand",
            "parameters": {
                "type": "object",
                "properties": {
                    "piattaforma": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin", "tutte"]},
                    "sentiment": {"type": "string", "enum": ["positivo", "negativo", "neutro", "tutti"]},
                    "limite": {"type": "integer", "default": 20},
                    "includi_risposte": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "programma_post",
            "description": "Programma un post sui social per pubblicazione futura",
            "parameters": {
                "type": "object",
                "properties": {
                    "piattaforma": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin"]},
                    "contenuto": {"type": "string"},
                    "orario_programmato": {"type": "string", "description": "Data e ora ISO"},
                    "url_media": {"type": "array", "items": {"type": "string"}},
                    "primo_commento": {"type": "string", "description": "Pubblica automaticamente il primo commento (Instagram)"}
                },
                "required": ["piattaforma", "contenuto", "orario_programmato"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_argomenti_trending",
            "description": "Ottieni gli argomenti e hashtag di tendenza del momento",
            "parameters": {
                "type": "object",
                "properties": {
                    "piattaforma": {"type": "string", "enum": ["twitter", "tiktok", "instagram"]},
                    "localita": {"type": "string", "description": "Paese o città"},
                    "categoria": {"type": "string", "enum": ["tutti", "tech", "intrattenimento", "sport", "notizie", "business"]}
                },
                "required": ["piattaforma"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rispondi_a_commento",
            "description": "Rispondi a un commento o messaggio sui social",
            "parameters": {
                "type": "object",
                "properties": {
                    "piattaforma": {"type": "string"},
                    "id_commento": {"type": "string"},
                    "testo_risposta": {"type": "string"},
                    "includi_menzione": {"type": "boolean", "default": True}
                },
                "required": ["piattaforma", "id_commento", "testo_risposta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_analisi_competitor",
            "description": "Analizza le performance social dei competitor",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle_competitor": {"type": "array", "items": {"type": "string"}},
                    "piattaforma": {"type": "string", "enum": ["twitter", "instagram", "linkedin"]},
                    "metriche": {"type": "array", "items": {"type": "string", "enum": ["follower", "tasso_engagement", "frequenza_post", "contenuti_top"]}}
                },
                "required": ["handle_competitor", "piattaforma"]
            }
        }
    },
]
