"""Strumenti mock per servizi governativi e pubblica amministrazione."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible

STRUMENTI_PA = [
    {
        "type": "function",
        "function": {
            "name": "verifica_stato_tasse",
            "description": "Verifica lo stato dei pagamenti fiscali e le scadenze",
            "parameters": {
                "type": "object",
                "properties": {
                    "codice_fiscale": {"type": "string", "description": "Codice fiscale"},
                    "anno_fiscale": {"type": "integer"},
                    "tipo_tassa": {"type": "string", "enum": ["IRPEF", "IVA", "IMU", "TARI", "tutte"]}
                },
                "required": ["codice_fiscale"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prenota_appuntamento_ufficio_pubblico",
            "description": "Prenota un appuntamento presso uffici pubblici (Comune, ASL, INPS, ecc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_ufficio": {"type": "string", "enum": ["comune", "anagrafe", "asl", "inps", "agenzia_entrate", "motorizzazione", "prefettura"]},
                    "servizio": {"type": "string", "description": "Servizio specifico richiesto"},
                    "citta": {"type": "string"},
                    "data_preferita": {"type": "string"},
                    "orario_preferito": {"type": "string", "enum": ["mattina", "pomeriggio", "qualsiasi"]}
                },
                "required": ["tipo_ufficio", "servizio", "citta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verifica_stato_documento",
            "description": "Verifica lo stato delle richieste di documenti (passaporto, CI, permessi)",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_documento": {"type": "string", "enum": ["passaporto", "carta_identita", "patente", "permesso_soggiorno", "certificato"]},
                    "id_richiesta": {"type": "string"},
                    "codice_fiscale": {"type": "string"}
                },
                "required": ["tipo_documento"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_info_trasporto_pubblico",
            "description": "Ottieni informazioni sul trasporto pubblico (abbonamenti, multe, orari)",
            "parameters": {
                "type": "object",
                "properties": {
                    "citta": {"type": "string"},
                    "tipo_info": {"type": "string", "enum": ["abbonamenti", "multe", "orari", "interruzioni", "tariffe"]},
                    "tipo_trasporto": {"type": "string", "enum": ["metro", "bus", "tram", "treno", "tutti"]}
                },
                "required": ["citta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "richiedi_certificato",
            "description": "Richiedi certificati ufficiali online",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_certificato": {"type": "string", "enum": ["nascita", "residenza", "stato_famiglia", "matrimonio", "esistenza_in_vita", "carichi_pendenti", "casellario_giudiziale"]},
                    "metodo_consegna": {"type": "string", "enum": ["digitale", "postale", "ritiro"]},
                    "urgenza": {"type": "string", "enum": ["standard", "urgente"]},
                    "copie": {"type": "integer", "default": 1}
                },
                "required": ["tipo_certificato"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verifica_stato_pensione",
            "description": "Verifica i contributi pensionistici e la pensione stimata",
            "parameters": {
                "type": "object",
                "properties": {
                    "codice_fiscale": {"type": "string"},
                    "includi_simulazione": {"type": "boolean", "default": True, "description": "Includi simulazione pensionistica"},
                    "eta_pensionamento": {"type": "integer", "description": "Età per la simulazione"}
                },
                "required": ["codice_fiscale"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "paga_tributo",
            "description": "Paga tributi e tasse online",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_tributo": {"type": "string", "enum": ["bollo_auto", "multa", "tassa_rifiuti", "contributi", "marca_bollo"]},
                    "importo": {"type": "number"},
                    "numero_riferimento": {"type": "string"},
                    "metodo_pagamento": {"type": "string", "enum": ["carta", "bonifico", "pagoPA"]}
                },
                "required": ["tipo_tributo", "importo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verifica_stato_veicolo",
            "description": "Verifica immatricolazione, tasse e assicurazione del veicolo",
            "parameters": {
                "type": "object",
                "properties": {
                    "targa": {"type": "string"},
                    "tipo_verifica": {"type": "string", "enum": ["bollo", "revisione", "assicurazione", "proprietario", "tutto"]}
                },
                "required": ["targa"]
            }
        }
    },
]
