"""Strumenti mock per e-commerce e acquisti online."""

import random
from datetime import datetime, timedelta

STRUMENTI_ECOMMERCE = [
    {
        "type": "function",
        "function": {
            "name": "cerca_prodotti",
            "description": "Cerca prodotti nei negozi online",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query di ricerca prodotto"},
                    "categoria": {"type": "string"},
                    "prezzo_minimo": {"type": "number"},
                    "prezzo_massimo": {"type": "number"},
                    "ordina_per": {"type": "string", "enum": ["rilevanza", "prezzo_crescente", "prezzo_decrescente", "valutazione", "novita"]},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_dettagli_prodotto",
            "description": "Ottieni informazioni dettagliate su un prodotto specifico",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_prodotto": {"type": "string"}
                },
                "required": ["id_prodotto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "aggiungi_al_carrello",
            "description": "Aggiungi un prodotto al carrello",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_prodotto": {"type": "string"},
                    "quantita": {"type": "integer", "default": 1}
                },
                "required": ["id_prodotto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_carrello",
            "description": "Visualizza il contenuto attuale del carrello",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "traccia_ordine",
            "description": "Traccia lo stato di un ordine",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_ordine": {"type": "string"}
                },
                "required": ["id_ordine"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_storico_ordini",
            "description": "Recupera gli ordini passati",
            "parameters": {
                "type": "object",
                "properties": {
                    "limite": {"type": "integer", "default": 10},
                    "stato": {"type": "string", "enum": ["tutti", "in_attesa", "spedito", "consegnato", "annullato"]}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "applica_coupon",
            "description": "Applica un coupon sconto al carrello",
            "parameters": {
                "type": "object",
                "properties": {
                    "codice_coupon": {"type": "string"}
                },
                "required": ["codice_coupon"]
            }
        }
    },
]
