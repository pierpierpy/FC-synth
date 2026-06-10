"""Strumenti mock per sensori IoT e monitoraggio."""

import random
from datetime import datetime, timedelta

STRUMENTI_IOT = [
    {
        "type": "function",
        "function": {
            "name": "ottieni_dati_sensore",
            "description": "Ottieni dati dai sensori IoT",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_sensore": {"type": "string"},
                    "tipo_sensore": {"type": "string", "enum": ["temperatura", "umidita", "movimento", "qualita_aria", "rumore", "luce", "pressione", "acqua", "energia"]},
                    "posizione": {"type": "string"},
                    "intervallo_tempo": {"type": "string", "enum": ["tempo_reale", "1h", "24h", "7g", "30g"]}
                },
                "required": ["tipo_sensore"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "imposta_allarme_sensore",
            "description": "Configura allarmi per soglie dei sensori",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_sensore": {"type": "string"},
                    "condizione": {"type": "string", "enum": ["sopra", "sotto", "uguale", "variazione"]},
                    "soglia": {"type": "number"},
                    "metodo_allarme": {"type": "string", "enum": ["push", "email", "sms", "webhook"]},
                    "pausa_minuti": {"type": "integer", "default": 15}
                },
                "required": ["id_sensore", "condizione", "soglia"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_stato_dispositivo",
            "description": "Ottieni lo stato dei dispositivi IoT connessi",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_dispositivo": {"type": "string"},
                    "tipo_dispositivo": {"type": "string", "enum": ["sensore", "attuatore", "gateway", "telecamera", "speaker", "display"]},
                    "includi_diagnostica": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "controlla_attuatore",
            "description": "Controlla un attuatore IoT (relè, motore, valvola, ecc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_attuatore": {"type": "string"},
                    "azione": {"type": "string", "enum": ["accendi", "spegni", "alterna", "imposta_livello", "impulso"]},
                    "valore": {"type": "number", "description": "Valore per imposta_livello (0-100)"},
                    "durata_secondi": {"type": "integer", "description": "Durata per azione impulso"}
                },
                "required": ["id_attuatore", "azione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_consumo_energia",
            "description": "Ottieni dati sul consumo energetico dai contatori smart",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_contatore": {"type": "string"},
                    "periodo": {"type": "string", "enum": ["oggi", "ieri", "settimana", "mese", "anno"]},
                    "granularita": {"type": "string", "enum": ["oraria", "giornaliera", "settimanale", "mensile"]},
                    "confronta_precedente": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_regola_automazione",
            "description": "Crea una regola di automazione per dispositivi IoT",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "trigger": {"type": "object", "description": "Condizione di attivazione (sensore, ora, evento)"},
                    "azione": {"type": "object", "description": "Azione da eseguire"},
                    "condizioni": {"type": "array", "items": {"type": "object"}, "description": "Condizioni aggiuntive"},
                    "abilitata": {"type": "boolean", "default": True}
                },
                "required": ["nome", "trigger", "azione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_dati_ambientali",
            "description": "Ottieni dati di monitoraggio ambientale (esterno/interno)",
            "parameters": {
                "type": "object",
                "properties": {
                    "posizione": {"type": "string"},
                    "metriche": {"type": "array", "items": {"type": "string", "enum": ["temperatura", "umidita", "pm25", "pm10", "co2", "voc", "rumore", "uv"]}},
                    "intervallo_tempo": {"type": "string", "enum": ["attuale", "24h", "7g"]}
                },
                "required": ["posizione"]
            }
        }
    },
]
