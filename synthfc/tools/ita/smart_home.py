"""Strumenti mock per casa intelligente e dispositivi IoT."""

import random
from datetime import datetime, timedelta

STRUMENTI_CASA_SMART = [
    {
        "type": "function",
        "function": {
            "name": "controlla_luci",
            "description": "Controlla le luci smart (accendi/spegni, luminosità, colore)",
            "parameters": {
                "type": "object",
                "properties": {
                    "stanza": {"type": "string", "description": "Nome della stanza o 'tutte'"},
                    "azione": {"type": "string", "enum": ["accendi", "spegni", "alterna", "abbassa", "aumenta"]},
                    "luminosita": {"type": "integer", "description": "Livello di luminosità 0-100"},
                    "colore": {"type": "string", "description": "Nome del colore o codice esadecimale"}
                },
                "required": ["stanza", "azione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "imposta_termostato",
            "description": "Controlla la temperatura del termostato smart",
            "parameters": {
                "type": "object",
                "properties": {
                    "temperatura": {"type": "number", "description": "Temperatura target in Celsius"},
                    "modalita": {"type": "string", "enum": ["riscaldamento", "raffreddamento", "auto", "spento"]},
                    "zona": {"type": "string", "description": "Nome della zona (opzionale)"}
                },
                "required": ["temperatura"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_stato_casa",
            "description": "Ottieni lo stato generale della casa smart e dei dispositivi",
            "parameters": {
                "type": "object",
                "properties": {
                    "includi_energia": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "controlla_serratura",
            "description": "Blocca o sblocca le serrature smart",
            "parameters": {
                "type": "object",
                "properties": {
                    "porta": {"type": "string", "description": "Identificativo della porta (principale, secondaria, garage)"},
                    "azione": {"type": "string", "enum": ["blocca", "sblocca"]}
                },
                "required": ["porta", "azione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_video_telecamera",
            "description": "Ottieni lo stato o un'istantanea dalla telecamera di sicurezza",
            "parameters": {
                "type": "object",
                "properties": {
                    "telecamera": {"type": "string", "description": "Nome o posizione della telecamera"},
                    "azione": {"type": "string", "enum": ["stato", "istantanea", "registrazione"], "default": "stato"}
                },
                "required": ["telecamera"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "controlla_tapparelle",
            "description": "Controlla tapparelle o tende smart",
            "parameters": {
                "type": "object",
                "properties": {
                    "stanza": {"type": "string"},
                    "posizione": {"type": "integer", "description": "Posizione 0 (chiuso) a 100 (aperto)"},
                    "azione": {"type": "string", "enum": ["apri", "chiudi", "imposta_posizione"]}
                },
                "required": ["stanza"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riproduci_musica",
            "description": "Controlla gli speaker smart e riproduci musica",
            "parameters": {
                "type": "object",
                "properties": {
                    "azione": {"type": "string", "enum": ["riproduci", "pausa", "stop", "successivo", "precedente", "volume"]},
                    "query": {"type": "string", "description": "Nome del brano, artista o playlist"},
                    "speaker": {"type": "string", "description": "Nome dello speaker o della stanza"},
                    "volume": {"type": "integer", "description": "Livello del volume 0-100"}
                },
                "required": ["azione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "imposta_allarme",
            "description": "Attiva o disattiva l'allarme di sicurezza della casa",
            "parameters": {
                "type": "object",
                "properties": {
                    "azione": {"type": "string", "enum": ["attiva_assente", "attiva_presente", "disattiva"]},
                    "codice": {"type": "string", "description": "Codice di sicurezza"}
                },
                "required": ["azione"]
            }
        }
    },
]
