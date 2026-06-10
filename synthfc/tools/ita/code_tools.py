"""Strumenti mock per sviluppatori e assistenza alla programmazione."""

import random
from datetime import datetime, timedelta

STRUMENTI_CODICE = [
    {
        "type": "function",
        "function": {
            "name": "esegui_codice",
            "description": "Esegui codice in un ambiente sandbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "linguaggio": {"type": "string", "enum": ["python", "javascript", "typescript", "bash", "sql", "rust", "go"]},
                    "codice": {"type": "string", "description": "Codice da eseguire"},
                    "timeout": {"type": "integer", "default": 30, "description": "Timeout in secondi"},
                    "stdin": {"type": "string", "description": "Input standard"}
                },
                "required": ["linguaggio", "codice"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cerca_github",
            "description": "Cerca codice, repository o issue su GitHub",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "tipo": {"type": "string", "enum": ["repository", "codice", "issue", "utenti"]},
                    "linguaggio": {"type": "string"},
                    "ordina_per": {"type": "string", "enum": ["stelle", "fork", "aggiornamento", "rilevanza"]},
                    "limite": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_info_pacchetto",
            "description": "Ottieni informazioni su un pacchetto da npm, PyPI o altri registry",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_pacchetto": {"type": "string"},
                    "registry": {"type": "string", "enum": ["npm", "pypi", "crates", "maven", "rubygems"]},
                    "versione": {"type": "string", "description": "Versione specifica, o 'latest'"}
                },
                "required": ["nome_pacchetto", "registry"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analizza_codice",
            "description": "Esegui linter/analisi statica sul codice",
            "parameters": {
                "type": "object",
                "properties": {
                    "codice": {"type": "string"},
                    "linguaggio": {"type": "string", "enum": ["python", "javascript", "typescript", "go", "rust"]},
                    "regole": {"type": "array", "items": {"type": "string"}, "description": "Regole specifiche da verificare"}
                },
                "required": ["codice", "linguaggio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "formatta_codice",
            "description": "Formatta il codice secondo le linee guida di stile",
            "parameters": {
                "type": "object",
                "properties": {
                    "codice": {"type": "string"},
                    "linguaggio": {"type": "string", "enum": ["python", "javascript", "typescript", "json", "yaml", "sql", "html", "css"]},
                    "stile": {"type": "string", "description": "Guida di stile (es. 'black', 'prettier', 'google')"}
                },
                "required": ["codice", "linguaggio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spiega_errore",
            "description": "Ottieni spiegazione e suggerimenti di correzione per un messaggio di errore",
            "parameters": {
                "type": "object",
                "properties": {
                    "messaggio_errore": {"type": "string"},
                    "linguaggio": {"type": "string"},
                    "codice_contesto": {"type": "string", "description": "Contesto del codice circostante"}
                },
                "required": ["messaggio_errore"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_documentazione_api",
            "description": "Recupera la documentazione API per una libreria o servizio",
            "parameters": {
                "type": "object",
                "properties": {
                    "libreria": {"type": "string"},
                    "metodo": {"type": "string", "description": "Metodo o endpoint specifico"},
                    "versione": {"type": "string"}
                },
                "required": ["libreria"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "esegui_test",
            "description": "Esegui suite di test e restituisci i risultati",
            "parameters": {
                "type": "object",
                "properties": {
                    "codice_test": {"type": "string"},
                    "linguaggio": {"type": "string", "enum": ["python", "javascript", "typescript"]},
                    "framework": {"type": "string", "enum": ["pytest", "jest", "mocha", "unittest"]},
                    "copertura": {"type": "boolean", "default": False}
                },
                "required": ["codice_test", "linguaggio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "genera_regex",
            "description": "Genera un pattern di espressione regolare per una descrizione",
            "parameters": {
                "type": "object",
                "properties": {
                    "descrizione": {"type": "string", "description": "Cosa deve matchare la regex"},
                    "stringhe_test": {"type": "array", "items": {"type": "string"}, "description": "Stringhe su cui testare"},
                    "variante": {"type": "string", "enum": ["python", "javascript", "pcre"]}
                },
                "required": ["descrizione"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "converti_codice",
            "description": "Converti codice da un linguaggio a un altro",
            "parameters": {
                "type": "object",
                "properties": {
                    "codice": {"type": "string"},
                    "da_linguaggio": {"type": "string"},
                    "a_linguaggio": {"type": "string"},
                    "preserva_commenti": {"type": "boolean", "default": True}
                },
                "required": ["codice", "da_linguaggio", "a_linguaggio"]
            }
        }
    },
]
