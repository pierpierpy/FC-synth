"""Strumenti mock per ricerca e recupero informazioni."""

import random
from datetime import datetime, timedelta

STRUMENTI_RICERCA = [
    {
        "type": "function",
        "function": {
            "name": "ricerca_web",
            "description": "Cerca informazioni sul web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query di ricerca"},
                    "numero_risultati": {"type": "integer", "default": 5},
                    "lingua": {"type": "string", "default": "it"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_wikipedia",
            "description": "Cerca e recupera informazioni da Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Argomento da cercare"},
                    "lingua": {"type": "string", "enum": ["it", "en", "de", "fr", "es"], "default": "it"},
                    "solo_riepilogo": {"type": "boolean", "default": True}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_notizie",
            "description": "Cerca articoli di notizie recenti",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "categoria": {"type": "string", "enum": ["generale", "tecnologia", "economia", "sport", "spettacolo", "scienza"]},
                    "intervallo_tempo": {"type": "string", "enum": ["24h", "7g", "30g"], "default": "7g"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_immagini",
            "description": "Cerca immagini sul web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "dimensione": {"type": "string", "enum": ["piccola", "media", "grande"], "default": "media"},
                    "tipo": {"type": "string", "enum": ["foto", "clipart", "illustrazione", "qualsiasi"], "default": "qualsiasi"},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_definizione",
            "description": "Cerca la definizione di una parola o termine",
            "parameters": {
                "type": "object",
                "properties": {
                    "parola": {"type": "string"},
                    "lingua": {"type": "string", "default": "it"},
                    "includi_esempi": {"type": "boolean", "default": True}
                },
                "required": ["parola"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_luoghi_locali",
            "description": "Cerca attività commerciali, ristoranti o punti di interesse nelle vicinanze",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Cosa cercare"},
                    "localita": {"type": "string", "description": "Città o indirizzo"},
                    "raggio_km": {"type": "number", "default": 5},
                    "categoria": {"type": "string", "enum": ["ristorante", "hotel", "negozio", "farmacia", "benzina", "qualsiasi"]}
                },
                "required": ["query", "localita"]
            }
        }
    },
]
