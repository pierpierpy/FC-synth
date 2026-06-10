"""Strumenti mock per comunicazione (email, messaggistica, chiamate)."""

import random
from datetime import datetime, timedelta

STRUMENTI_COMUNICAZIONE = [
    {
        "type": "function",
        "function": {
            "name": "invia_email",
            "description": "Invia un'email a uno o più destinatari",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "array", "items": {"type": "string"}, "description": "Lista di indirizzi email dei destinatari"},
                    "oggetto": {"type": "string"},
                    "corpo": {"type": "string"},
                    "cc": {"type": "array", "items": {"type": "string"}},
                    "allegati": {"type": "array", "items": {"type": "string"}, "description": "Percorsi dei file da allegare"}
                },
                "required": ["a", "oggetto", "corpo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_email",
            "description": "Recupera le email dalla posta in arrivo o da una cartella specifica",
            "parameters": {
                "type": "object",
                "properties": {
                    "cartella": {"type": "string", "enum": ["posta_in_arrivo", "inviati", "bozze", "spam", "cestino"], "default": "posta_in_arrivo"},
                    "solo_non_lette": {"type": "boolean", "default": False},
                    "limite": {"type": "integer", "default": 10},
                    "query_ricerca": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "invia_sms",
            "description": "Invia un messaggio SMS",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_telefono": {"type": "string", "description": "Numero di telefono del destinatario"},
                    "messaggio": {"type": "string", "description": "Testo del messaggio (max 160 caratteri)"}
                },
                "required": ["numero_telefono", "messaggio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "invia_messaggio_whatsapp",
            "description": "Invia un messaggio WhatsApp a un contatto",
            "parameters": {
                "type": "object",
                "properties": {
                    "contatto": {"type": "string", "description": "Nome del contatto o numero di telefono"},
                    "messaggio": {"type": "string"}
                },
                "required": ["contatto", "messaggio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "effettua_chiamata",
            "description": "Avvia una telefonata",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_telefono": {"type": "string"},
                    "nome_contatto": {"type": "string"}
                },
                "required": ["numero_telefono"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_contatti",
            "description": "Cerca e recupera contatti dalla rubrica",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Cerca per nome, email o telefono"},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pianifica_riunione",
            "description": "Pianifica una riunione video/audio e invia gli inviti",
            "parameters": {
                "type": "object",
                "properties": {
                    "titolo": {"type": "string"},
                    "partecipanti": {"type": "array", "items": {"type": "string"}},
                    "data_ora": {"type": "string", "description": "Ora di inizio della riunione (formato ISO)"},
                    "durata_minuti": {"type": "integer", "default": 60},
                    "piattaforma": {"type": "string", "enum": ["teams", "zoom", "meet", "webex"], "default": "teams"},
                    "ordine_del_giorno": {"type": "string"}
                },
                "required": ["titolo", "partecipanti", "data_ora"]
            }
        }
    },
]
