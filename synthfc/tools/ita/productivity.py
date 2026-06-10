"""Strumenti mock per produttività e gestione attività."""

import random
from datetime import datetime, timedelta

STRUMENTI_PRODUTTIVITA = [
    {
        "type": "function",
        "function": {
            "name": "crea_attivita",
            "description": "Crea una nuova attività o elemento da fare",
            "parameters": {
                "type": "object",
                "properties": {
                    "titolo": {"type": "string"},
                    "descrizione": {"type": "string"},
                    "data_scadenza": {"type": "string", "description": "Data di scadenza (AAAA-MM-GG)"},
                    "priorita": {"type": "string", "enum": ["bassa", "media", "alta", "urgente"]},
                    "progetto": {"type": "string"},
                    "etichette": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["titolo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_attivita",
            "description": "Recupera le attività filtrate per vari criteri",
            "parameters": {
                "type": "object",
                "properties": {
                    "stato": {"type": "string", "enum": ["in_sospeso", "in_corso", "completata", "tutte"], "default": "in_sospeso"},
                    "progetto": {"type": "string"},
                    "scadenza_prima_di": {"type": "string"},
                    "priorita": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "completa_attivita",
            "description": "Segna un'attività come completata",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_attivita": {"type": "string"}
                },
                "required": ["id_attivita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_nota",
            "description": "Crea una nuova nota o documento",
            "parameters": {
                "type": "object",
                "properties": {
                    "titolo": {"type": "string"},
                    "contenuto": {"type": "string"},
                    "cartella": {"type": "string"},
                    "etichette": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["titolo", "contenuto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_note",
            "description": "Cerca tra le note salvate",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "cartella": {"type": "string"},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "imposta_timer",
            "description": "Imposta un timer con conto alla rovescia",
            "parameters": {
                "type": "object",
                "properties": {
                    "durata_minuti": {"type": "integer"},
                    "etichetta": {"type": "string"},
                    "suono_allarme": {"type": "boolean", "default": True}
                },
                "required": ["durata_minuti"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "avvia_cronometro",
            "description": "Avvia un cronometro per il tracciamento del tempo",
            "parameters": {
                "type": "object",
                "properties": {
                    "etichetta": {"type": "string", "description": "Cosa stai cronometrando"},
                    "progetto": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "traduci_testo",
            "description": "Traduci testo tra lingue diverse",
            "parameters": {
                "type": "object",
                "properties": {
                    "testo": {"type": "string"},
                    "lingua_origine": {"type": "string", "description": "Codice lingua di origine (rilevamento automatico se non specificato)"},
                    "lingua_destinazione": {"type": "string", "description": "Codice lingua di destinazione"}
                },
                "required": ["testo", "lingua_destinazione"]
            }
        }
    },
]
