"""Strumenti mock per gestione documenti e file."""

import random
from datetime import datetime, timedelta

STRUMENTI_DOCUMENTI = [
    {
        "type": "function",
        "function": {
            "name": "cerca_documenti",
            "description": "Cerca tra i documenti nel cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query di ricerca"},
                    "tipo_file": {"type": "string", "enum": ["tutti", "pdf", "docx", "xlsx", "pptx", "txt", "immagine"]},
                    "cartella": {"type": "string", "description": "Percorso della cartella in cui cercare"},
                    "modificato_dopo": {"type": "string", "description": "Filtra per data di modifica"},
                    "proprietario": {"type": "string", "description": "Filtra per email del proprietario"},
                    "condivisi_con_me": {"type": "boolean", "default": False}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_documento",
            "description": "Crea un nuovo documento nel cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome del documento"},
                    "tipo": {"type": "string", "enum": ["documento", "foglio_calcolo", "presentazione", "modulo"]},
                    "cartella": {"type": "string"},
                    "template": {"type": "string", "description": "Template da utilizzare"},
                    "contenuto": {"type": "string", "description": "Contenuto iniziale"}
                },
                "required": ["nome", "tipo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "condividi_documento",
            "description": "Condividi un documento con utenti o gruppi specifici",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_documento": {"type": "string"},
                    "condividi_con": {"type": "array", "items": {"type": "string"}, "description": "Indirizzi email"},
                    "permesso": {"type": "string", "enum": ["visualizza", "commenta", "modifica"]},
                    "notifica": {"type": "boolean", "default": True},
                    "messaggio": {"type": "string", "description": "Messaggio opzionale da includere"}
                },
                "required": ["id_documento", "condividi_con", "permesso"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_info_documento",
            "description": "Ottieni informazioni dettagliate su un documento",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_documento": {"type": "string"},
                    "includi_cronologia": {"type": "boolean", "default": False},
                    "includi_permessi": {"type": "boolean", "default": False}
                },
                "required": ["id_documento"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "converti_documento",
            "description": "Converti un documento in un formato diverso",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_documento": {"type": "string"},
                    "formato_destinazione": {"type": "string", "enum": ["pdf", "docx", "html", "txt", "epub"]},
                    "opzioni": {
                        "type": "object",
                        "properties": {
                            "includi_commenti": {"type": "boolean"},
                            "includi_immagini": {"type": "boolean"},
                            "intervallo_pagine": {"type": "string"}
                        }
                    }
                },
                "required": ["id_documento", "formato_destinazione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "carica_file",
            "description": "Carica un file nel cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "percorso_file": {"type": "string", "description": "Percorso locale del file"},
                    "cartella_destinazione": {"type": "string"},
                    "rinomina_in": {"type": "string"},
                    "converti_in_nativo": {"type": "boolean", "default": False}
                },
                "required": ["percorso_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_cartella",
            "description": "Crea una nuova cartella nel cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "cartella_padre": {"type": "string"},
                    "colore": {"type": "string", "enum": ["blu", "rosso", "verde", "giallo", "viola", "grigio"]}
                },
                "required": ["nome"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_quota_storage",
            "description": "Ottieni informazioni sull'utilizzo e quota dello storage cloud",
            "parameters": {
                "type": "object",
                "properties": {
                    "includi_dettaglio": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
]
