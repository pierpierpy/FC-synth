"""
Libreria di Strumenti Mock per Conversazioni FC Multi-Turno Realistiche

Questo modulo fornisce oltre 130 strumenti mock realistici organizzati per categoria.
Ogni mock restituisce dati plausibili e contestualmente appropriati.
"""

from .weather import STRUMENTI_METEO
from .finance import STRUMENTI_FINANZA
from .calendar import STRUMENTI_CALENDARIO
from .search import STRUMENTI_RICERCA
from .communication import STRUMENTI_COMUNICAZIONE
from .productivity import STRUMENTI_PRODUTTIVITA
from .travel import STRUMENTI_VIAGGI
from .ecommerce import STRUMENTI_ECOMMERCE
from .smart_home import STRUMENTI_CASA_SMART
from .media import STRUMENTI_MEDIA
from .health import STRUMENTI_SALUTE
from .utilities import STRUMENTI_UTILITA
# Moduli avanzati
from .database import STRUMENTI_DATABASE
from .documents import STRUMENTI_DOCUMENTI
from .social_media import STRUMENTI_SOCIAL
from .code_tools import STRUMENTI_CODICE
from .booking import STRUMENTI_PRENOTAZIONI
from .news import STRUMENTI_NOTIZIE
from .government import STRUMENTI_PA
from .iot_sensors import STRUMENTI_IOT
from .crm import STRUMENTI_CRM
from .knowledge_base import STRUMENTI_KNOWLEDGE_BASE

# Tutti gli strumenti combinati
TUTTI_GLI_STRUMENTI = (
    STRUMENTI_METEO +
    STRUMENTI_FINANZA +
    STRUMENTI_CALENDARIO +
    STRUMENTI_RICERCA +
    STRUMENTI_COMUNICAZIONE +
    STRUMENTI_PRODUTTIVITA +
    STRUMENTI_VIAGGI +
    STRUMENTI_ECOMMERCE +
    STRUMENTI_CASA_SMART +
    STRUMENTI_MEDIA +
    STRUMENTI_SALUTE +
    STRUMENTI_UTILITA +
    # Moduli avanzati
    STRUMENTI_DATABASE +
    STRUMENTI_DOCUMENTI +
    STRUMENTI_SOCIAL +
    STRUMENTI_CODICE +
    STRUMENTI_PRENOTAZIONI +
    STRUMENTI_NOTIZIE +
    STRUMENTI_PA +
    STRUMENTI_IOT +
    STRUMENTI_CRM +
    STRUMENTI_KNOWLEDGE_BASE
)

# Strumenti raggruppati per categoria
STRUMENTI_PER_CATEGORIA = {
    "meteo": STRUMENTI_METEO,
    "finanza": STRUMENTI_FINANZA,
    "calendario": STRUMENTI_CALENDARIO,
    "ricerca": STRUMENTI_RICERCA,
    "comunicazione": STRUMENTI_COMUNICAZIONE,
    "produttivita": STRUMENTI_PRODUTTIVITA,
    "viaggi": STRUMENTI_VIAGGI,
    "ecommerce": STRUMENTI_ECOMMERCE,
    "casa_smart": STRUMENTI_CASA_SMART,
    "media": STRUMENTI_MEDIA,
    "salute": STRUMENTI_SALUTE,
    "utilita": STRUMENTI_UTILITA,
    "database": STRUMENTI_DATABASE,
    "documenti": STRUMENTI_DOCUMENTI,
    "social": STRUMENTI_SOCIAL,
    "codice": STRUMENTI_CODICE,
    "prenotazioni": STRUMENTI_PRENOTAZIONI,
    "notizie": STRUMENTI_NOTIZIE,
    "pubblica_amministrazione": STRUMENTI_PA,
    "iot": STRUMENTI_IOT,
    "crm": STRUMENTI_CRM,
    "knowledge_base": STRUMENTI_KNOWLEDGE_BASE,
}


# English-friendly alias, mirroring the eng package export name.
TOOLS_BY_CATEGORY = STRUMENTI_PER_CATEGORIA


def ottieni_strumenti_per_categoria(categoria: str) -> list:
    """Ottieni gli strumenti per una categoria specifica."""
    return STRUMENTI_PER_CATEGORIA.get(categoria, [])


def ottieni_strumento_per_nome(nome: str) -> dict | None:
    """Trova uno strumento per nome in tutte le categorie."""
    for strumento in TUTTI_GLI_STRUMENTI:
        if strumento["function"]["name"] == nome:
            return strumento
    return None


__all__ = [
    "TUTTI_GLI_STRUMENTI",
    "STRUMENTI_PER_CATEGORIA",
    "TOOLS_BY_CATEGORY",
    "STRUMENTI_METEO",
    "STRUMENTI_FINANZA",
    "STRUMENTI_CALENDARIO",
    "STRUMENTI_RICERCA",
    "STRUMENTI_COMUNICAZIONE",
    "STRUMENTI_PRODUTTIVITA",
    "STRUMENTI_VIAGGI",
    "STRUMENTI_ECOMMERCE",
    "STRUMENTI_CASA_SMART",
    "STRUMENTI_MEDIA",
    "STRUMENTI_SALUTE",
    "STRUMENTI_UTILITA",
    "STRUMENTI_DATABASE",
    "STRUMENTI_DOCUMENTI",
    "STRUMENTI_SOCIAL",
    "STRUMENTI_CODICE",
    "STRUMENTI_PRENOTAZIONI",
    "STRUMENTI_NOTIZIE",
    "STRUMENTI_PA",
    "STRUMENTI_IOT",
    "STRUMENTI_CRM",
    "STRUMENTI_KNOWLEDGE_BASE",
    "ottieni_strumenti_per_categoria",
    "ottieni_strumento_per_nome",
    "TOOLS_BY_CATEGORY",
]


# Alias canonico per gli importatori (compatibile con il pacchetto eng).
# Manteniamo STRUMENTI_PER_CATEGORIA per retro-compatibilita'.
TOOLS_BY_CATEGORY = STRUMENTI_PER_CATEGORIA
