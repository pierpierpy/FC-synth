"""Strumenti mock per Database, Analytics e Business Intelligence."""

import random
from datetime import datetime, timedelta

STRUMENTI_DATABASE = [
    {
        "type": "function",
        "function": {
            "name": "interroga_database",
            "description": "Esegui una query SQL di sola lettura sul database connesso",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query SQL SELECT da eseguire"},
                    "database": {"type": "string", "description": "Nome del database", "enum": ["vendite", "clienti", "inventario", "analytics"]},
                    "limite": {"type": "integer", "default": 100}
                },
                "required": ["query", "database"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_report_vendite",
            "description": "Genera un report delle vendite per un periodo specifico",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_inizio": {"type": "string", "description": "Data di inizio (AAAA-MM-GG)"},
                    "data_fine": {"type": "string", "description": "Data di fine (AAAA-MM-GG)"},
                    "raggruppa_per": {"type": "string", "enum": ["giorno", "settimana", "mese", "prodotto", "regione", "venditore"]},
                    "filtri": {
                        "type": "object",
                        "properties": {
                            "regione": {"type": "string"},
                            "categoria_prodotto": {"type": "string"},
                            "importo_minimo": {"type": "number"}
                        }
                    }
                },
                "required": ["data_inizio", "data_fine"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_analytics_clienti",
            "description": "Ottieni analytics sul comportamento dei clienti e dati di segmentazione",
            "parameters": {
                "type": "object",
                "properties": {
                    "metrica": {"type": "string", "enum": ["rischio_abbandono", "valore_lifetime", "engagement", "soddisfazione", "frequenza_acquisto"]},
                    "segmento": {"type": "string", "description": "Segmento di clienti da analizzare"},
                    "periodo": {"type": "string", "enum": ["7g", "30g", "90g", "1a"]}
                },
                "required": ["metrica"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_stato_inventario",
            "description": "Verifica i livelli di inventario e lo stato delle scorte",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_prodotto": {"type": "string"},
                    "magazzino": {"type": "string"},
                    "includi_previsioni": {"type": "boolean", "default": False},
                    "solo_scorte_basse": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_widget_dashboard",
            "description": "Crea un nuovo widget per la dashboard di analytics",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_widget": {"type": "string", "enum": ["grafico_linee", "grafico_barre", "grafico_torta", "kpi_card", "tabella", "mappa_calore"]},
                    "fonte_dati": {"type": "string"},
                    "titolo": {"type": "string"},
                    "intervallo_aggiornamento_minuti": {"type": "integer", "default": 60}
                },
                "required": ["tipo_widget", "fonte_dati", "titolo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "esporta_report",
            "description": "Esporta dati o report in vari formati",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_report": {"type": "string", "enum": ["vendite", "inventario", "clienti", "finanziario", "personalizzato"]},
                    "formato": {"type": "string", "enum": ["csv", "xlsx", "pdf", "json"]},
                    "intervallo_date": {"type": "object", "properties": {"inizio": {"type": "string"}, "fine": {"type": "string"}}},
                    "invia_email_a": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["tipo_report", "formato"]
            }
        }
    },
]
