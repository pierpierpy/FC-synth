"""Strumenti mock per salute e fitness."""

import random
from datetime import datetime, timedelta

STRUMENTI_SALUTE = [
    {
        "type": "function",
        "function": {
            "name": "registra_allenamento",
            "description": "Registra un allenamento o sessione di esercizio",
            "parameters": {
                "type": "object",
                "properties": {
                    "attivita": {"type": "string", "description": "Tipo di allenamento (corsa, palestra, yoga, ecc.)"},
                    "durata_minuti": {"type": "integer"},
                    "calorie": {"type": "integer"},
                    "note": {"type": "string"}
                },
                "required": ["attivita", "durata_minuti"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_statistiche_fitness",
            "description": "Ottieni statistiche fitness e riepilogo attività",
            "parameters": {
                "type": "object",
                "properties": {
                    "periodo": {"type": "string", "enum": ["oggi", "settimana", "mese"], "default": "settimana"},
                    "includi_frequenza_cardiaca": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registra_pasto",
            "description": "Registra assunzione di cibo e nutrizione",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_pasto": {"type": "string", "enum": ["colazione", "pranzo", "cena", "spuntino"]},
                    "descrizione": {"type": "string", "description": "Descrizione del cibo"},
                    "calorie": {"type": "integer"},
                    "macronutrienti": {
                        "type": "object",
                        "properties": {
                            "proteine": {"type": "number"},
                            "carboidrati": {"type": "number"},
                            "grassi": {"type": "number"}
                        }
                    }
                },
                "required": ["tipo_pasto", "descrizione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_riepilogo_nutrizione",
            "description": "Ottieni riepilogo nutrizione e calorie",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "Data (AAAA-MM-GG)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registra_assunzione_acqua",
            "description": "Registra il consumo di acqua",
            "parameters": {
                "type": "object",
                "properties": {
                    "quantita_ml": {"type": "integer", "description": "Quantità in millilitri"}
                },
                "required": ["quantita_ml"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_dati_sonno",
            "description": "Ottieni dati sul monitoraggio del sonno",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string"},
                    "periodo": {"type": "string", "enum": ["notte", "settimana", "mese"], "default": "notte"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "imposta_obiettivo_salute",
            "description": "Imposta un obiettivo di salute o fitness",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_obiettivo": {"type": "string", "enum": ["passi", "calorie", "peso", "acqua", "sonno", "allenamento"]},
                    "target": {"type": "number"},
                    "scadenza": {"type": "string", "description": "Data target (AAAA-MM-GG)"}
                },
                "required": ["tipo_obiettivo", "target"]
            }
        }
    },
]
