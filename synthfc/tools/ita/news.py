"""Strumenti mock per notizie e feed RSS."""

import random
from datetime import datetime, timedelta

STRUMENTI_NOTIZIE = [
    {
        "type": "function",
        "function": {
            "name": "ottieni_titoli_notizie",
            "description": "Ottieni gli ultimi titoli delle notizie per categoria o fonte",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {"type": "string", "enum": ["generale", "tecnologia", "economia", "sport", "spettacolo", "scienza", "salute", "politica"]},
                    "paese": {"type": "string", "description": "Codice paese (it, us, uk, ecc.)"},
                    "fonte": {"type": "string", "description": "Nome della fonte di notizie"},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_notizie",
            "description": "Cerca articoli di notizie per parole chiave",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "data_da": {"type": "string", "description": "Data inizio AAAA-MM-GG"},
                    "data_a": {"type": "string", "description": "Data fine AAAA-MM-GG"},
                    "lingua": {"type": "string", "default": "it"},
                    "ordina_per": {"type": "string", "enum": ["rilevanza", "data", "popolarita"]}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_feed_rss",
            "description": "Ottieni e analizza un feed RSS da un URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url_feed": {"type": "string"},
                    "limite": {"type": "integer", "default": 20},
                    "includi_contenuto": {"type": "boolean", "default": False}
                },
                "required": ["url_feed"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "iscriviti_alert_notizie",
            "description": "Iscriviti agli alert per argomenti specifici",
            "parameters": {
                "type": "object",
                "properties": {
                    "parole_chiave": {"type": "array", "items": {"type": "string"}},
                    "frequenza": {"type": "string", "enum": ["istantaneo", "giornaliero", "settimanale"]},
                    "metodo_consegna": {"type": "string", "enum": ["email", "push", "sms"]},
                    "fonti": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["parole_chiave"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_riepilogo_articolo",
            "description": "Ottieni un riepilogo generato dall'IA di un articolo di notizie",
            "parameters": {
                "type": "object",
                "properties": {
                    "url_articolo": {"type": "string"},
                    "lunghezza_riepilogo": {"type": "string", "enum": ["breve", "medio", "lungo"]},
                    "includi_punti_chiave": {"type": "boolean", "default": True},
                    "traduci_in": {"type": "string", "description": "Lingua target per la traduzione"}
                },
                "required": ["url_articolo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_notizie_trending",
            "description": "Ottieni le notizie di tendenza del momento",
            "parameters": {
                "type": "object",
                "properties": {
                    "regione": {"type": "string", "default": "IT"},
                    "arco_temporale": {"type": "string", "enum": ["1h", "6h", "24h", "7g"]},
                    "categoria": {"type": "string"}
                },
                "required": []
            }
        }
    },
]
