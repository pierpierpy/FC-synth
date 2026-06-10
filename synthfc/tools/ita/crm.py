"""Strumenti mock per CRM e gestione clienti."""

import random
from datetime import datetime, timedelta

STRUMENTI_CRM = [
    {
        "type": "function",
        "function": {
            "name": "cerca_clienti",
            "description": "Cerca clienti nel CRM",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Nome, email, telefono o azienda"},
                    "filtri": {"type": "object", "properties": {
                        "stato": {"type": "string", "enum": ["attivo", "inattivo", "potenziale", "perso"]},
                        "segmento": {"type": "string"},
                        "creato_dopo": {"type": "string"}
                    }},
                    "limite": {"type": "integer", "default": 20}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_dettagli_cliente",
            "description": "Ottieni informazioni dettagliate su un cliente",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_cliente": {"type": "string"},
                    "includi_ordini": {"type": "boolean", "default": True},
                    "includi_interazioni": {"type": "boolean", "default": True},
                    "includi_ticket": {"type": "boolean", "default": False}
                },
                "required": ["id_cliente"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_cliente",
            "description": "Crea un nuovo record cliente",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "email": {"type": "string"},
                    "telefono": {"type": "string"},
                    "azienda": {"type": "string"},
                    "segmento": {"type": "string", "enum": ["privato", "piccola_impresa", "enterprise"]},
                    "origine": {"type": "string", "enum": ["sito_web", "referral", "pubblicita", "evento", "chiamata_fredda"]},
                    "note": {"type": "string"}
                },
                "required": ["nome", "email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registra_interazione",
            "description": "Registra un'interazione con il cliente (chiamata, email, riunione)",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_cliente": {"type": "string"},
                    "tipo_interazione": {"type": "string", "enum": ["chiamata", "email", "riunione", "chat", "social", "ticket_supporto"]},
                    "oggetto": {"type": "string"},
                    "note": {"type": "string"},
                    "esito": {"type": "string", "enum": ["positivo", "neutro", "negativo", "follow_up_richiesto"]},
                    "data_prossima_azione": {"type": "string"}
                },
                "required": ["id_cliente", "tipo_interazione", "oggetto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_opportunita",
            "description": "Crea un'opportunità/trattativa di vendita",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_cliente": {"type": "string"},
                    "titolo": {"type": "string"},
                    "valore": {"type": "number"},
                    "valuta": {"type": "string", "default": "EUR"},
                    "fase": {"type": "string", "enum": ["lead", "qualificato", "proposta", "negoziazione", "vinto", "perso"]},
                    "data_chiusura_prevista": {"type": "string"},
                    "probabilita": {"type": "integer", "minimum": 0, "maximum": 100},
                    "prodotti": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["id_cliente", "titolo", "valore"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_pipeline_vendite",
            "description": "Ottieni panoramica della pipeline di vendita",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_responsabile": {"type": "string", "description": "Filtra per commerciale"},
                    "periodo": {"type": "string", "enum": ["mese_corrente", "trimestre_corrente", "anno_corrente"]},
                    "includi_previsioni": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "invia_campagna",
            "description": "Invia campagna marketing a un segmento di clienti",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_campagna": {"type": "string"},
                    "segmento": {"type": "string", "description": "Segmento di clienti target"},
                    "canale": {"type": "string", "enum": ["email", "sms", "push", "whatsapp"]},
                    "id_template": {"type": "string"},
                    "orario_invio": {"type": "string", "description": "Data/ora ISO o 'adesso'"},
                    "personalizzazione": {"type": "boolean", "default": True}
                },
                "required": ["nome_campagna", "segmento", "canale"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_punteggio_salute_cliente",
            "description": "Ottieni punteggio di salute del cliente e rischio abbandono",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_cliente": {"type": "string"},
                    "includi_fattori": {"type": "boolean", "default": True}
                },
                "required": ["id_cliente"]
            }
        }
    },
]
