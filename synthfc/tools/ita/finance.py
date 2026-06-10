"""Strumenti mock relativi alla finanza."""

import random
from datetime import datetime, timedelta

STRUMENTI_FINANZA = [
    {
        "type": "function",
        "function": {
            "name": "ottieni_prezzo_azione",
            "description": "Ottieni il prezzo corrente e le info di base per un simbolo azionario",
            "parameters": {
                "type": "object",
                "properties": {
                    "simbolo": {"type": "string", "description": "Simbolo ticker dell'azione (es. AAPL, MSFT)"},
                    "includi_storico": {"type": "boolean", "default": False}
                },
                "required": ["simbolo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_tasso_cambio",
            "description": "Ottieni il tasso di cambio tra due valute",
            "parameters": {
                "type": "object",
                "properties": {
                    "valuta_origine": {"type": "string", "description": "Codice valuta di origine (es. EUR, USD)"},
                    "valuta_destinazione": {"type": "string", "description": "Codice valuta di destinazione"},
                    "importo": {"type": "number", "default": 1}
                },
                "required": ["valuta_origine", "valuta_destinazione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_prezzo_crypto",
            "description": "Ottieni il prezzo e i dati di mercato di una criptovaluta",
            "parameters": {
                "type": "object",
                "properties": {
                    "moneta": {"type": "string", "description": "Nome o simbolo della criptovaluta (es. bitcoin, BTC)"},
                    "valuta": {"type": "string", "default": "EUR"}
                },
                "required": ["moneta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_saldo_banca",
            "description": "Ottieni il saldo corrente del conto bancario e le transazioni recenti",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_conto": {"type": "string", "description": "Identificativo del conto"},
                    "includi_transazioni": {"type": "boolean", "default": True}
                },
                "required": ["id_conto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trasferisci_denaro",
            "description": "Trasferisci denaro tra conti o verso un'altra persona",
            "parameters": {
                "type": "object",
                "properties": {
                    "conto_origine": {"type": "string"},
                    "conto_destinazione": {"type": "string", "description": "Conto di destinazione o IBAN"},
                    "importo": {"type": "number"},
                    "valuta": {"type": "string", "default": "EUR"},
                    "descrizione": {"type": "string"}
                },
                "required": ["conto_origine", "conto_destinazione", "importo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_notizie_mercato",
            "description": "Ottieni le ultime notizie e analisi dei mercati finanziari",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {"type": "string", "enum": ["azioni", "crypto", "forex", "materie_prime", "generale"]},
                    "limite": {"type": "integer", "default": 5}
                },
                "required": []
            }
        }
    },
]
