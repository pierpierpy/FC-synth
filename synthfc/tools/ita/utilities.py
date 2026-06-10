"""Strumenti mock di utilità e varie."""

import random
from datetime import datetime, timedelta
import math

STRUMENTI_UTILITA = [
    {
        "type": "function",
        "function": {
            "name": "calcola",
            "description": "Esegui calcoli matematici",
            "parameters": {
                "type": "object",
                "properties": {
                    "espressione": {"type": "string", "description": "Espressione matematica da valutare"},
                    "precisione": {"type": "integer", "default": 2}
                },
                "required": ["espressione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "converti_unita",
            "description": "Converti tra diverse unità di misura",
            "parameters": {
                "type": "object",
                "properties": {
                    "valore": {"type": "number"},
                    "unita_origine": {"type": "string"},
                    "unita_destinazione": {"type": "string"}
                },
                "required": ["valore", "unita_origine", "unita_destinazione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_ora_corrente",
            "description": "Ottieni data e ora correnti per un fuso orario",
            "parameters": {
                "type": "object",
                "properties": {
                    "fuso_orario": {"type": "string", "description": "Nome del fuso orario o offset"},
                    "formato": {"type": "string", "enum": ["completo", "data", "ora"], "default": "completo"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "genera_password",
            "description": "Genera una password casuale sicura",
            "parameters": {
                "type": "object",
                "properties": {
                    "lunghezza": {"type": "integer", "default": 16},
                    "includi_simboli": {"type": "boolean", "default": True},
                    "includi_numeri": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "genera_qr_code",
            "description": "Genera un codice QR per testo o URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "contenuto": {"type": "string", "description": "Testo o URL da codificare"},
                    "dimensione": {"type": "string", "enum": ["piccolo", "medio", "grande"], "default": "medio"}
                },
                "required": ["contenuto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "accorcia_url",
            "description": "Crea un URL abbreviato",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL lungo da abbreviare"},
                    "alias_personalizzato": {"type": "string", "description": "Alias breve personalizzato (opzionale)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_curiosita",
            "description": "Ottieni una curiosità o fatto interessante casuale",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {"type": "string", "enum": ["scienza", "storia", "natura", "tecnologia", "qualsiasi"]}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_citazione",
            "description": "Ottieni una citazione ispirazionale o famosa",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {"type": "string", "enum": ["motivazionale", "saggezza", "divertente", "famosa", "qualsiasi"]}
                },
                "required": []
            }
        }
    },
]
