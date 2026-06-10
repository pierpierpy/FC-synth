"""Strumenti knowledge base / assistente documenti - Versione italiana."""

STRUMENTI_KNOWLEDGE_BASE = [
    # ==================== VARIAZIONI RIASSUNTO DOCUMENTO ====================
    {
        "type": "function",
        "function": {
            "name": "riassunto_documento",
            "description": "Genera un riassunto completo dell'intero documento caricato utilizzando le istruzioni fornite dall'utente. Utile ogni qualvolta l'utente chiede un riassunto del documento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_documento": {"type": "string", "description": "Nome del documento da riassumere"}
                },
                "required": ["nome_documento"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "genera_riassunto",
            "description": "Crea un riassunto del documento specificato in base alle richieste dell'utente. Da usare quando l'utente vuole una panoramica del contenuto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_file": {"type": "string", "description": "Il nome del file da riassumere"}
                },
                "required": ["nome_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sintesi_documento",
            "description": "Produce una sintesi completa del file caricato seguendo le indicazioni dell'utente. Ideale per avere una visione d'insieme di documenti lunghi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "documento": {"type": "string", "description": "Nome del documento da elaborare"}
                },
                "required": ["documento"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_panoramica_documento",
            "description": "Estrae e fornisce una panoramica generale dell'intero documento. Ottimo quando l'utente ha bisogno di capire rapidamente i punti principali.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Nome del file caricato"}
                },
                "required": ["file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crea_sommario_file",
            "description": "Analizza il documento e genera un sommario condensato con le informazioni chiave. Perfetto per report o documenti lunghi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_origine": {"type": "string", "description": "Il file da sintetizzare"}
                },
                "required": ["file_origine"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estrai_riassunto",
            "description": "Legge l'intero documento ed estrae un riassunto esaustivo. Usalo quando l'utente vuole capire il documento senza leggerlo tutto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "documento_sorgente": {"type": "string", "description": "Nome del documento sorgente"}
                },
                "required": ["documento_sorgente"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "produci_sintesi",
            "description": "Crea una sintesi informativa dal contenuto del documento caricato. Utile quando gli utenti richiedono un riepilogo del loro file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {"type": "string", "description": "Documento da elaborare"}
                },
                "required": ["doc"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "panoramica_doc",
            "description": "Fornisce una vista riassuntiva del documento evidenziando argomenti principali e conclusioni. Adatto per qualsiasi richiesta di sintesi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_doc": {"type": "string", "description": "Nome file del documento"}
                },
                "required": ["file_doc"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generatore_riassunto",
            "description": "Genera automaticamente un riassunto basato sul contenuto completo del documento specificato. Ottimo per comprendere rapidamente i documenti.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_input": {"type": "string", "description": "Nome del file in input da riassumere"}
                },
                "required": ["file_input"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "riassumi_doc_caricato",
            "description": "Prende il documento caricato e produce un riassunto dettagliato ma conciso seguendo le istruzioni dell'utente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "documento_caricato": {"type": "string", "description": "Nome del documento caricato"}
                },
                "required": ["documento_caricato"]
            }
        }
    },
    # ==================== VARIAZIONI CONTENUTO PAGINA ====================
    {
        "type": "function",
        "function": {
            "name": "ottieni_contenuto_pagina",
            "description": "Restituisce il contenuto di una pagina specifica del documento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_documento": {"type": "string", "description": "Nome del documento"},
                    "numero_pagina": {"type": "integer", "description": "Numero di pagina richiesto dall'utente", "minimum": 1}
                },
                "required": ["nome_documento", "numero_pagina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "leggi_pagina",
            "description": "Legge e restituisce il contenuto testuale da una pagina specificata nel documento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_file": {"type": "string", "description": "Il nome del file documento"},
                    "pagina": {"type": "integer", "description": "Il numero di pagina da leggere", "minimum": 1}
                },
                "required": ["nome_file", "pagina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recupera_contenuto_pagina",
            "description": "Recupera il contenuto di una particolare pagina dal documento caricato.",
            "parameters": {
                "type": "object",
                "properties": {
                    "documento": {"type": "string", "description": "Nome documento"},
                    "num_pagina": {"type": "integer", "description": "Numero della pagina da recuperare", "minimum": 1}
                },
                "required": ["documento", "num_pagina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estrai_pagina",
            "description": "Estrae e restituisce il contenuto da una singola pagina del documento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Nome del file"},
                    "indice_pagina": {"type": "integer", "description": "Indice della pagina (parte da 1)", "minimum": 1}
                },
                "required": ["file", "indice_pagina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_pagina_specifica",
            "description": "Recupera il testo di una pagina specifica dal documento. Utile quando l'utente vuole vedere una determinata pagina.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_doc": {"type": "string", "description": "Il file documento"},
                    "pagina_target": {"type": "integer", "description": "Il numero della pagina target", "minimum": 1}
                },
                "required": ["file_doc", "pagina_target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "preleva_testo_pagina",
            "description": "Preleva il contenuto testuale dal numero di pagina specificato nel documento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "documento_sorgente": {"type": "string", "description": "Nome documento sorgente"},
                    "n_pagina": {"type": "integer", "description": "Numero pagina da prelevare", "minimum": 1}
                },
                "required": ["documento_sorgente", "n_pagina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mostra_pagina",
            "description": "Visualizza il contenuto di una pagina richiesta dal documento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {"type": "string", "description": "Il documento da cui leggere"},
                    "pagina_da_mostrare": {"type": "integer", "description": "Numero pagina da visualizzare", "minimum": 1}
                },
                "required": ["doc", "pagina_da_mostrare"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lettore_pagina",
            "description": "Legge una pagina specifica e ne restituisce il contenuto completo. Usalo quando l'utente chiede di una particolare pagina.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_documento": {"type": "string", "description": "Nome file documento"},
                    "pagina_richiesta": {"type": "integer", "description": "Il numero della pagina richiesta", "minimum": 1}
                },
                "required": ["file_documento", "pagina_richiesta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ottieni_pagina_doc",
            "description": "Ottiene il contenuto di una singola pagina dal documento specificato.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_input": {"type": "string", "description": "File documento in input"},
                    "nr_pagina": {"type": "integer", "description": "Numero pagina (a partire da 1)", "minimum": 1}
                },
                "required": ["file_input", "nr_pagina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "carica_contenuto_pagina",
            "description": "Carica e restituisce il contenuto da una pagina designata nel documento caricato.",
            "parameters": {
                "type": "object",
                "properties": {
                    "documento_caricato": {"type": "string", "description": "Nome documento caricato"},
                    "id_pagina": {"type": "integer", "description": "Identificativo pagina (numero)", "minimum": 1}
                },
                "required": ["documento_caricato", "id_pagina"]
            }
        }
    },
]
