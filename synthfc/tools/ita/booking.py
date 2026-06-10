"""Strumenti mock per prenotazioni e riservazioni (ristoranti, eventi, servizi)."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible, safe_int

STRUMENTI_PRENOTAZIONI = [
    {
        "type": "function",
        "function": {
            "name": "prenota_ristorante",
            "description": "Effettua una prenotazione al ristorante",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_ristorante": {"type": "string"},
                    "data": {"type": "string", "description": "Data nel formato AAAA-MM-GG"},
                    "ora": {"type": "string", "description": "Ora nel formato HH:MM"},
                    "numero_persone": {"type": "integer"},
                    "richieste_speciali": {"type": "string"},
                    "tavolo_esterno": {"type": "boolean", "default": False}
                },
                "required": ["nome_ristorante", "data", "ora", "numero_persone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_ristoranti",
            "description": "Cerca ristoranti in base a criteri specifici",
            "parameters": {
                "type": "object",
                "properties": {
                    "localita": {"type": "string"},
                    "cucina": {"type": "string", "enum": ["italiana", "giapponese", "cinese", "messicana", "americana", "indiana", "francese", "fusion", "pizzeria", "pesce"]},
                    "fascia_prezzo": {"type": "string", "enum": ["€", "€€", "€€€", "€€€€"]},
                    "valutazione_minima": {"type": "number", "minimum": 1, "maximum": 5},
                    "aperto_ora": {"type": "boolean"},
                    "caratteristiche": {"type": "array", "items": {"type": "string", "enum": ["esterno", "wifi", "parcheggio", "vegetariano", "vegano", "senza_glutine", "consegna"]}}
                },
                "required": ["localita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prenota_biglietti_evento",
            "description": "Prenota biglietti per concerti, spettacoli, eventi sportivi",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_evento": {"type": "string"},
                    "data": {"type": "string"},
                    "sede": {"type": "string"},
                    "tipo_biglietto": {"type": "string", "enum": ["standard", "vip", "premium", "gold", "platinum"]},
                    "quantita": {"type": "integer"},
                    "preferenza_posto": {"type": "string", "enum": ["qualsiasi", "davanti", "centro", "dietro", "corridoio"]}
                },
                "required": ["nome_evento", "quantita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_eventi",
            "description": "Cerca eventi in programma",
            "parameters": {
                "type": "object",
                "properties": {
                    "localita": {"type": "string"},
                    "categoria": {"type": "string", "enum": ["concerti", "teatro", "sport", "comicita", "festival", "mostre", "conferenze"]},
                    "data_da": {"type": "string"},
                    "data_a": {"type": "string"},
                    "artista_squadra": {"type": "string"},
                    "prezzo_massimo": {"type": "number"}
                },
                "required": ["localita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prenota_appuntamento",
            "description": "Prenota un appuntamento (medico, dentista, parrucchiere, ecc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_servizio": {"type": "string", "enum": ["medico", "dentista", "parrucchiere", "spa", "meccanico", "veterinario", "avvocato", "commercialista"]},
                    "nome_professionista": {"type": "string"},
                    "data": {"type": "string"},
                    "orario_preferito": {"type": "string", "enum": ["mattina", "pomeriggio", "sera", "qualsiasi"]},
                    "dettagli_servizio": {"type": "string"},
                    "prima_visita": {"type": "boolean", "default": False}
                },
                "required": ["tipo_servizio", "data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verifica_disponibilita",
            "description": "Verifica la disponibilità per un servizio o locale",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_servizio": {"type": "string"},
                    "data": {"type": "string"},
                    "durata_minuti": {"type": "integer"},
                    "numero_persone": {"type": "integer", "default": 1}
                },
                "required": ["id_servizio", "data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "annulla_prenotazione",
            "description": "Annulla una prenotazione esistente",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_prenotazione": {"type": "string"},
                    "motivo": {"type": "string"},
                    "richiedi_rimborso": {"type": "boolean", "default": True}
                },
                "required": ["id_prenotazione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modifica_prenotazione",
            "description": "Modifica una prenotazione esistente",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_prenotazione": {"type": "string"},
                    "nuova_data": {"type": "string"},
                    "nuovo_orario": {"type": "string"},
                    "nuovo_numero_persone": {"type": "integer"},
                    "note_aggiuntive": {"type": "string"}
                },
                "required": ["id_prenotazione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_storico_prenotazioni",
            "description": "Ottieni lo storico delle prenotazioni dell'utente",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {"type": "string", "enum": ["ristoranti", "eventi", "appuntamenti", "tutti"]},
                    "stato": {"type": "string", "enum": ["future", "passate", "annullate", "tutte"]},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
]
