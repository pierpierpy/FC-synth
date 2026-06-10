"""
FC Dataset Sampler
Generates parameters for building multi-turn function-calling conversations.
"""

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import json

# Import config
from ..config import get_config


# =============================================================================
# DISTRIBUTION CONFIGURATION (defaults)
# =============================================================================

DEFAULT_DISTRIBUTIONS = {
    # Language
    "language_combo": {
        ("it", "it"): 0.50,  # tool IT, conv IT
        ("en", "it"): 0.20,  # tool EN, conv IT
        ("en", "en"): 0.20,  # tool EN, conv EN
        ("it", "en"): 0.10,  # tool IT, conv EN
    },

    # Tool selection
    "num_tools_available": {2: 0.20, 3: 0.35, 4: 0.30, 5: 0.15},

    # Main call type
    "call_type": {
        "positive": 0.50,
        "negative": 0.35,
        "clarification": 0.15
    },

    # Positive subtypes
    "positive_type": {
        "direct": 0.25,
        "after_chitchat": 0.35,
        "followup": 0.20,
        "multi_tool": 0.12,
        "after_clarification": 0.08
    },
    
    # Negative subtypes
    "negative_reason": {
        "no_need": 0.50,
        "out_of_scope": 0.30,
        "already_answered": 0.20
    },

    # Clarification subtypes
    "clarification_outcome": {
        "resolved": 0.50,
        "unresolved": 0.30,
        "partial": 0.20
    },

    # Number of tool calls (for positive)
    "num_tool_calls": {1: 0.55, 2: 0.30, 3: 0.15},

    # Position of the first tool call
    "first_tool_position": {1: 0.20, 3: 0.25, 5: 0.25, 7: 0.20, 9: 0.10},

    # Conversation length
    "conversation_length": {
        "short": 0.25,      # 2-4 msg
        "medium": 0.40,     # 6-10 msg
        "long": 0.25,       # 12-18 msg
        "very_long": 0.10   # 20+ msg
    },

    # History type - added multi_topic
    "history_type": {
        "none": 0.18,
        "chitchat": 0.30,
        "context_setting": 0.22,
        "previous_tool": 0.18,
        "multi_topic": 0.12
    },
    
    # User style - added frustrated, confused, verbose
    "user_style": {
        "formal": 0.22,
        "informal": 0.28,
        "vague": 0.15,
        "telegraphic": 0.12,
        "frustrated": 0.08,
        "confused": 0.08,
        "verbose": 0.07
    },
    
    # System prompt type
    "system_prompt_type": {
        "none": 0.10,
        "minimal": 0.25,
        "standard": 0.40,
        "detailed": 0.25
    },
    
    # Edge cases - added ambiguous_request, multi_step_task, partial_success, tool_error_recovery
    "edge_case": {
        None: 0.65,
        "topic_change": 0.05,
        "user_correction": 0.05,
        "tool_error": 0.05,
        "tool_error_recovery": 0.08,  # NEW: tool error -> new request -> mandatory tool call
        "ambiguous_request": 0.04,
        "multi_step_task": 0.04,
        "partial_success": 0.04
    },

    # Param complexity - added missing
    "param_complexity": {
        "explicit": 0.40,
        "implicit": 0.25,
        "mixed": 0.20,
        "missing": 0.15
    },

    # Number of "out of scope" requests during the conversation
    "out_of_scope_requests": {
        0: 0.70,
        1: 0.20,
        2: 0.08,
        3: 0.02
    }
}


def _parse_config_distribution(key: str, config_dist: Dict) -> Dict:
    """Converts a distribution from the YAML config to the internal format."""
    if key == "language_combo":
        # Converts "it,it" -> ("it", "it")
        return {tuple(k.split(",")): v for k, v in config_dist.items()}
    elif key == "edge_case":
        # Converts "null" -> None
        return {(None if k == "null" else k): v for k, v in config_dist.items()}
    elif key in ("num_tools_available", "num_tool_calls", "first_tool_position", "out_of_scope_requests"):
        # Converts strings to int for numeric keys
        return {int(k): v for k, v in config_dist.items()}
    else:
        return config_dist


def get_distributions() -> Dict:
    """Gets distributions from config (falling back to the defaults)."""
    cfg = get_config()
    sampling = cfg.sampling

    if not sampling:
        return DEFAULT_DISTRIBUTIONS.copy()

    result = DEFAULT_DISTRIBUTIONS.copy()
    for key, default_dist in DEFAULT_DISTRIBUTIONS.items():
        if key in sampling:
            result[key] = _parse_config_distribution(key, sampling[key])

    return result


# Lazy getter for the distributions
_distributions: Optional[Dict] = None

def _get_dist() -> Dict:
    global _distributions
    if _distributions is None:
        _distributions = get_distributions()
    return _distributions


# Alias for backward compatibility
DISTRIBUTIONS = DEFAULT_DISTRIBUTIONS

# Available domains - much more specific and realistic
DOMAINS = [
    # === TELECOM & ISP (weight 2x) ===
    "supporto_linea_fissa",
    "supporto_linea_mobile", 
    "configurazione_router_modem",
    "problemi_connessione_internet",
    "attivazione_servizi_fibra",
    "gestione_abbonamenti_telefonici",
    "portabilità_numero",
    "fatturazione_bollette_telecom",
    "assistenza_tecnica_rete",
    "configurazione_vpn_aziendale",
    
    # === BANKING & FINANCE ===
    "conto_corrente_bancario",
    "carte_credito_debito",
    "mutui_prestiti",
    "investimenti_trading",
    "assicurazioni_polizze",
    "pagamenti_bonifici",
    "gestione_portafoglio",
    "criptovalute_exchange",
    "consulenza_fiscale",
    "contabilità_aziendale",
    
    # === E-COMMERCE & RETAIL ===
    "ordini_spedizioni",
    "resi_rimborsi",
    "tracking_pacchi",
    "catalogo_prodotti",
    "carrello_checkout",
    "recensioni_prodotti",
    "programmi_fedeltà",
    "comparazione_prezzi",
    "gestione_magazzino",
    "dropshipping",
    
    # === TRAVEL & HOSPITALITY ===
    "prenotazione_voli",
    "prenotazione_hotel",
    "noleggio_auto",
    "pacchetti_vacanze",
    "visti_documenti_viaggio",
    "assicurazione_viaggio",
    "transfer_aeroporto",
    "escursioni_tours",
    "prenotazione_ristoranti",
    "eventi_biglietti",
    
    # === HEALTH & WELLNESS ===
    "prenotazione_visite_mediche",
    "referti_esami_clinici",
    "farmacia_medicinali",
    "telemedicina",
    "fitness_palestra",
    "nutrizione_diete",
    "salute_mentale",
    "assicurazione_sanitaria",
    "pronto_soccorso_urgenze",
    "veterinario_animali",
    
    # === PUBLIC ADMINISTRATION ===
    "anagrafe_documenti_identità",
    "dichiarazione_redditi",
    "previdenza_pensioni",
    "permessi_licenze",
    "multe_sanzioni",
    "catasto_immobili",
    "iscrizione_scuole",
    "servizi_sociali",
    "bollo_auto",
    "passaporto_carta_identità",
    
    # === LAVORO & HR ===
    "ricerca_lavoro",
    "gestione_candidature",
    "buste_paga_cedolini",
    "ferie_permessi",
    "formazione_aziendale",
    "valutazione_performance",
    "onboarding_dipendenti",
    "timesheet_presenze",
    "benefit_welfare",
    "colloqui_selezione",
    
    # === REAL ESTATE ===
    "ricerca_immobili",
    "valutazione_casa",
    "contratti_affitto",
    "gestione_condominio",
    "ristrutturazioni",
    "traslochi",
    "utenze_casa",
    "agenzie_immobiliari",
    
    # === AUTOMOTIVE ===
    "acquisto_auto",
    "manutenzione_auto",
    "assicurazione_auto",
    "revisione_collaudo",
    "parcheggi_ztl",
    "carburante_ricarica_elettrica",
    "noleggio_lungo_termine",
    "concessionarie",
    
    # === EDUCATION ===
    "corsi_online",
    "università_iscrizioni",
    "certificazioni_lingue",
    "tutoring_ripetizioni",
    "biblioteca_risorse",
    "tesi_ricerca",
    "erasmus_scambi",
    "master_specializzazioni",
    
    # === TECH & SOFTWARE ===
    "supporto_software",
    "licenze_abbonamenti_sw",
    "cloud_storage",
    "cybersecurity",
    "sviluppo_web",
    "database_analytics",
    "automazione_processi",
    "helpdesk_it",
    "backup_recovery",
    "integrazione_api",
    
    # === MEDIA & ENTERTAINMENT ===
    "streaming_video",
    "streaming_musica",
    "gaming_videogiochi",
    "podcast_audiolibri",
    "abbonamenti_giornali",
    "cinema_teatro",
    "tv_digitale",
    "social_media_management",
    
    # === FOOD & DELIVERY ===
    "food_delivery",
    "spesa_online",
    "meal_kit",
    "prenotazione_tavoli",
    "catering_eventi",
    "recensioni_ristoranti",
    
    # === SMART HOME & IOT ===
    "domotica_casa",
    "termostati_smart",
    "sicurezza_allarmi",
    "elettrodomestici_connessi",
    "illuminazione_smart",
    "assistenti_vocali",
    
    # === ENERGY & UTILITIES ===
    "bollette_luce_gas",
    "fotovoltaico",
    "cambio_fornitore_energia",
    "lettura_contatori",
    "efficienza_energetica",
    "rifiuti_raccolta_differenziata",
    
    # === LEGAL ===
    "consulenza_legale",
    "contratti_documenti",
    "recupero_crediti",
    "diritto_lavoro",
    "privacy_gdpr",
    "proprietà_intellettuale",
    
    # === GENERAL ===
    "assistente_personale",
    "informazioni_generali",
    "ricerche_web",
    "traduzioni",
    "calcoli_conversioni",
    "reminder_promemoria"
]

# Domain weights (some have higher weight)
DOMAIN_WEIGHTS = {
    # Telecom - high weight
    "supporto_linea_fissa": 2.0,
    "supporto_linea_mobile": 2.0,
    "configurazione_router_modem": 2.0,
    "problemi_connessione_internet": 2.5,
    "attivazione_servizi_fibra": 2.0,
    "fatturazione_bollette_telecom": 2.0,
    "assistenza_tecnica_rete": 2.0,
    # E-commerce - medium-high weight
    "ordini_spedizioni": 1.5,
    "resi_rimborsi": 1.5,
    "tracking_pacchi": 1.5,
    # Banking - medium-high weight
    "conto_corrente_bancario": 1.5,
    "carte_credito_debito": 1.5,
    "pagamenti_bonifici": 1.5,
    # Other common ones
    "food_delivery": 1.3,
    "prenotazione_visite_mediche": 1.3,
    "prenotazione_voli": 1.3,
    "prenotazione_hotel": 1.3,
}

# Tool category -> file mapping
TOOL_CATEGORIES = {
    "knowledge_base": ["knowledge_base"],
    "documents": ["documents", "knowledge_base"],
    "booking": ["booking"],
    "communication": ["communication", "social_media"],
    "productivity": ["productivity", "calendar", "code_tools"],
    "database": ["database", "search"],
    "utilities": ["utilities", "weather", "smart_home", "iot_sensors"],
    "business": ["crm", "ecommerce", "finance"],
    "other": ["travel", "health", "news", "media", "government"]
}


# =============================================================================
# SAMPLING FUNCTIONS
# =============================================================================

def weighted_choice(distribution: Dict[Any, float]) -> Any:
    """Chooses a value based on the distribution weights."""
    items = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(items, weights=weights, k=1)[0]


def sample_domain() -> str:
    """Samples a domain using weights."""
    weights = [DOMAIN_WEIGHTS.get(d, 1.0) for d in DOMAINS]
    return random.choices(DOMAINS, weights=weights, k=1)[0]


def get_compatible_categories(domain: str) -> List[str]:
    """Returns tool categories compatible with the domain."""
    domain_to_categories = {
        # Telecom
        "supporto_linea_fissa": ["knowledge_base", "communication"],
        "supporto_linea_mobile": ["knowledge_base", "communication"],
        "configurazione_router_modem": ["knowledge_base", "utilities"],
        "problemi_connessione_internet": ["knowledge_base", "utilities", "database"],
        "attivazione_servizi_fibra": ["knowledge_base", "documents"],
        "gestione_abbonamenti_telefonici": ["knowledge_base", "business"],
        "portabilità_numero": ["knowledge_base", "documents"],
        "fatturazione_bollette_telecom": ["knowledge_base", "documents", "business"],
        "assistenza_tecnica_rete": ["knowledge_base", "utilities", "database"],
        "configurazione_vpn_aziendale": ["knowledge_base", "utilities"],

        # Banking & Finance
        "conto_corrente_bancario": ["business", "documents"],
        "carte_credito_debito": ["business"],
        "mutui_prestiti": ["business", "documents"],
        "investimenti_trading": ["business", "database"],
        "assicurazioni_polizze": ["business", "documents"],
        "pagamenti_bonifici": ["business"],
        "gestione_portafoglio": ["business", "database"],
        "criptovalute_exchange": ["business", "database"],
        "consulenza_fiscale": ["business", "documents"],
        "contabilità_aziendale": ["business", "documents", "database"],
        
        # E-commerce
        "ordini_spedizioni": ["business", "communication"],
        "resi_rimborsi": ["business", "communication"],
        "tracking_pacchi": ["business", "utilities"],
        "catalogo_prodotti": ["business", "database"],
        "carrello_checkout": ["business"],
        "recensioni_prodotti": ["business", "database"],
        "programmi_fedeltà": ["business"],
        "comparazione_prezzi": ["business", "database"],
        "gestione_magazzino": ["business", "database"],
        "dropshipping": ["business"],
        
        # Travel
        "prenotazione_voli": ["booking", "utilities"],
        "prenotazione_hotel": ["booking"],
        "noleggio_auto": ["booking"],
        "pacchetti_vacanze": ["booking", "utilities"],
        "visti_documenti_viaggio": ["documents", "other"],
        "assicurazione_viaggio": ["business", "documents"],
        "transfer_aeroporto": ["booking"],
        "escursioni_tours": ["booking"],
        "prenotazione_ristoranti": ["booking"],
        "eventi_biglietti": ["booking"],
        
        # Health
        "prenotazione_visite_mediche": ["booking", "other"],
        "referti_esami_clinici": ["documents", "other"],
        "farmacia_medicinali": ["other", "database"],
        "telemedicina": ["communication", "other"],
        "fitness_palestra": ["booking", "other"],
        "nutrizione_diete": ["other", "utilities"],
        "salute_mentale": ["communication", "other"],
        "assicurazione_sanitaria": ["business", "documents"],
        "pronto_soccorso_urgenze": ["communication", "other"],
        "veterinario_animali": ["booking", "other"],
        
        # PA
        "anagrafe_documenti_identità": ["documents", "other"],
        "dichiarazione_redditi": ["documents", "business"],
        "previdenza_pensioni": ["documents", "other"],
        "permessi_licenze": ["documents", "other"],
        "multe_sanzioni": ["documents", "business"],
        "catasto_immobili": ["documents", "database"],
        "iscrizione_scuole": ["documents", "other"],
        "servizi_sociali": ["documents", "other"],
        "bollo_auto": ["documents", "business"],
        "passaporto_carta_identità": ["documents", "other"],
        
        # HR
        "ricerca_lavoro": ["database", "communication"],
        "gestione_candidature": ["documents", "communication"],
        "buste_paga_cedolini": ["documents", "business"],
        "ferie_permessi": ["productivity", "documents"],
        "formazione_aziendale": ["productivity", "documents"],
        "valutazione_performance": ["productivity", "documents"],
        "onboarding_dipendenti": ["documents", "communication"],
        "timesheet_presenze": ["productivity", "database"],
        "benefit_welfare": ["business", "documents"],
        "colloqui_selezione": ["productivity", "communication"],
        
        # Real Estate
        "ricerca_immobili": ["database", "business"],
        "valutazione_casa": ["business", "utilities"],
        "contratti_affitto": ["documents", "business"],
        "gestione_condominio": ["documents", "communication"],
        "ristrutturazioni": ["business", "booking"],
        "traslochi": ["booking", "utilities"],
        "utenze_casa": ["business", "utilities"],
        "agenzie_immobiliari": ["business", "communication"],
        
        # Automotive
        "acquisto_auto": ["business", "database"],
        "manutenzione_auto": ["booking", "utilities"],
        "assicurazione_auto": ["business", "documents"],
        "revisione_collaudo": ["booking", "documents"],
        "parcheggi_ztl": ["utilities", "business"],
        "carburante_ricarica_elettrica": ["utilities", "database"],
        "noleggio_lungo_termine": ["business", "documents"],
        "concessionarie": ["business", "database"],
        
        # Education
        "corsi_online": ["productivity", "documents"],
        "università_iscrizioni": ["documents", "other"],
        "certificazioni_lingue": ["documents", "productivity"],
        "tutoring_ripetizioni": ["booking", "communication"],
        "biblioteca_risorse": ["database", "documents"],
        "tesi_ricerca": ["documents", "database"],
        "erasmus_scambi": ["documents", "other"],
        "master_specializzazioni": ["documents", "productivity"],
        
        # Tech
        "supporto_software": ["utilities", "communication"],
        "licenze_abbonamenti_sw": ["business", "documents"],
        "cloud_storage": ["utilities", "database"],
        "cybersecurity": ["utilities", "database"],
        "sviluppo_web": ["productivity", "database"],
        "database_analytics": ["database", "productivity"],
        "automazione_processi": ["productivity", "utilities"],
        "helpdesk_it": ["communication", "utilities"],
        "backup_recovery": ["utilities", "database"],
        "integrazione_api": ["productivity", "database"],
        
        # Media
        "streaming_video": ["other", "business"],
        "streaming_musica": ["other", "business"],
        "gaming_videogiochi": ["other", "business"],
        "podcast_audiolibri": ["other", "database"],
        "abbonamenti_giornali": ["business", "documents"],
        "cinema_teatro": ["booking", "other"],
        "tv_digitale": ["other", "utilities"],
        "social_media_management": ["communication", "productivity"],
        
        # Food
        "food_delivery": ["booking", "business"],
        "spesa_online": ["business", "database"],
        "meal_kit": ["business", "booking"],
        "prenotazione_tavoli": ["booking"],
        "catering_eventi": ["booking", "business"],
        "recensioni_ristoranti": ["database", "communication"],
        
        # Smart Home
        "domotica_casa": ["utilities"],
        "termostati_smart": ["utilities"],
        "sicurezza_allarmi": ["utilities", "communication"],
        "elettrodomestici_connessi": ["utilities"],
        "illuminazione_smart": ["utilities"],
        "assistenti_vocali": ["utilities", "communication"],
        
        # Energy
        "bollette_luce_gas": ["business", "documents"],
        "fotovoltaico": ["business", "utilities"],
        "cambio_fornitore_energia": ["business", "documents"],
        "lettura_contatori": ["utilities"],
        "efficienza_energetica": ["utilities", "database"],
        "rifiuti_raccolta_differenziata": ["utilities", "other"],
        
        # Legal
        "consulenza_legale": ["documents", "communication"],
        "contratti_documenti": ["documents"],
        "recupero_crediti": ["business", "documents"],
        "diritto_lavoro": ["documents", "other"],
        "privacy_gdpr": ["documents", "database"],
        "proprietà_intellettuale": ["documents", "other"],
        
        # General
        "assistente_personale": list(TOOL_CATEGORIES.keys()),
        "informazioni_generali": ["database", "utilities"],
        "ricerche_web": ["database"],
        "traduzioni": ["utilities", "productivity"],
        "calcoli_conversioni": ["utilities"],
        "reminder_promemoria": ["productivity", "utilities"],
    }
    return domain_to_categories.get(domain, ["utilities", "database", "communication"])


# =============================================================================
# PARAMETER DATACLASS
# =============================================================================

@dataclass
class SampledParams:
    """Sampled parameters for a conversation."""

    # Language
    tool_language: str
    conversation_language: str

    # Tool
    num_tools_available: int
    tool_categories: List[str]

    # Call type
    call_type: str  # "positive", "negative", "clarification"
    positive_type: Optional[str] = None
    negative_reason: Optional[str] = None
    clarification_outcome: Optional[str] = None

    # Tool call details (only when applicable)
    num_tool_calls: int = 0
    first_tool_position: int = 0
    param_complexity: Optional[str] = None

    # Conversation
    conversation_length: str = "medium"
    history_type: str = "none"
    user_style: str = "informal"
    domain: str = "generale"

    # System prompt
    system_prompt_type: str = "standard"

    # Edge case
    edge_case: Optional[str] = None

    # Out of scope requests
    out_of_scope_requests: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


# =============================================================================
# MAIN SAMPLER
# =============================================================================

def sample_params() -> SampledParams:
    """
    Samples all parameters for a conversation.
    Handles conditional dependencies between parameters.
    """
    dist = _get_dist()  # Uses distributions from config

    # 1. Language
    tool_lang, conv_lang = weighted_choice(dist["language_combo"])

    # 2. Domain (before tool selection for consistency)
    domain = sample_domain()

    # 3. Tool selection
    num_tools = weighted_choice(dist["num_tools_available"])
    compatible_cats = get_compatible_categories(domain)
    # Pick 1-2 compatible categories
    num_cats = min(2, len(compatible_cats))
    tool_categories = random.sample(compatible_cats, k=num_cats)

    # 4. Call type
    call_type = weighted_choice(dist["call_type"])

    # 5. Subtype and conditional parameters
    positive_type = None
    negative_reason = None
    clarification_outcome = None
    num_tool_calls = 0
    first_tool_position = 0
    param_complexity = None

    if call_type == "positive":
        positive_type = weighted_choice(dist["positive_type"])

        # Number of tool calls depends on the type
        if positive_type == "multi_tool":
            num_tool_calls = random.choices([2, 3], weights=[0.7, 0.3], k=1)[0]
        elif positive_type == "followup":
            num_tool_calls = random.choices([2, 3], weights=[0.8, 0.2], k=1)[0]
        else:
            num_tool_calls = weighted_choice(dist["num_tool_calls"])

        # Position of the first tool call depends on the type
        if positive_type == "direct":
            first_tool_position = 1
        elif positive_type == "after_chitchat":
            first_tool_position = weighted_choice({5: 0.4, 7: 0.4, 9: 0.2})
        elif positive_type == "after_clarification":
            first_tool_position = weighted_choice({5: 0.5, 7: 0.3, 9: 0.2})
        else:
            first_tool_position = weighted_choice(dist["first_tool_position"])

        param_complexity = weighted_choice(dist["param_complexity"])

    elif call_type == "negative":
        negative_reason = weighted_choice(dist["negative_reason"])
        num_tool_calls = 0
        first_tool_position = 0

    elif call_type == "clarification":
        clarification_outcome = weighted_choice(dist["clarification_outcome"])

        if clarification_outcome == "resolved":
            num_tool_calls = 1
            first_tool_position = weighted_choice({5: 0.4, 7: 0.4, 9: 0.2})
            param_complexity = weighted_choice(dist["param_complexity"])
        else:
            num_tool_calls = 0
            first_tool_position = 0

    # 6. Conversation
    conversation_length = weighted_choice(dist["conversation_length"])

    # History type depends on the position of the tool call
    if first_tool_position <= 1:
        history_type = "none"
    else:
        history_type = weighted_choice(dist["history_type"])

    user_style = weighted_choice(dist["user_style"])

    # 7. System prompt
    system_prompt_type = weighted_choice(dist["system_prompt_type"])

    # 8. Edge case
    edge_case = weighted_choice(dist["edge_case"])

    # 9. Out of scope requests (only for positive and resolved clarification)
    out_of_scope_requests = 0
    if call_type == "positive" or (call_type == "clarification" and clarification_outcome == "resolved"):
        out_of_scope_requests = weighted_choice(dist["out_of_scope_requests"])
    
    return SampledParams(
        tool_language=tool_lang,
        conversation_language=conv_lang,
        num_tools_available=num_tools,
        tool_categories=tool_categories,
        call_type=call_type,
        positive_type=positive_type,
        negative_reason=negative_reason,
        clarification_outcome=clarification_outcome,
        num_tool_calls=num_tool_calls,
        first_tool_position=first_tool_position,
        param_complexity=param_complexity,
        conversation_length=conversation_length,
        history_type=history_type,
        user_style=user_style,
        domain=domain,
        system_prompt_type=system_prompt_type,
        edge_case=edge_case,
        out_of_scope_requests=out_of_scope_requests
    )


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def sample_batch(n: int) -> List[SampledParams]:
    """Generates n sampled parameter sets."""
    return [sample_params() for _ in range(n)]


def analyze_distribution(samples: List[SampledParams]) -> Dict:
    """Analyzes the distribution of the sampled parameters."""
    n = len(samples)
    
    stats = {
        "total_samples": n,
        "language_combo": {},
        "call_type": {},
        "positive_type": {},
        "negative_reason": {},
        "clarification_outcome": {},
        "conversation_length": {},
        "user_style": {},
        "domain": {},
        "system_prompt_type": {},
        "num_tools_available": {},
        "first_tool_position": {},
        "avg_tool_calls": 0,
        "edge_cases": {}
    }
    
    total_tool_calls = 0
    
    for s in samples:
        # Language combo
        combo = (s.tool_language, s.conversation_language)
        stats["language_combo"][combo] = stats["language_combo"].get(combo, 0) + 1
        
        # Call type
        stats["call_type"][s.call_type] = stats["call_type"].get(s.call_type, 0) + 1
        
        # Subtypes
        if s.positive_type:
            stats["positive_type"][s.positive_type] = stats["positive_type"].get(s.positive_type, 0) + 1
        if s.negative_reason:
            stats["negative_reason"][s.negative_reason] = stats["negative_reason"].get(s.negative_reason, 0) + 1
        if s.clarification_outcome:
            stats["clarification_outcome"][s.clarification_outcome] = stats["clarification_outcome"].get(s.clarification_outcome, 0) + 1
        
        # Others
        stats["conversation_length"][s.conversation_length] = stats["conversation_length"].get(s.conversation_length, 0) + 1
        stats["user_style"][s.user_style] = stats["user_style"].get(s.user_style, 0) + 1
        stats["domain"][s.domain] = stats["domain"].get(s.domain, 0) + 1
        stats["system_prompt_type"][s.system_prompt_type] = stats["system_prompt_type"].get(s.system_prompt_type, 0) + 1
        stats["num_tools_available"][s.num_tools_available] = stats["num_tools_available"].get(s.num_tools_available, 0) + 1
        
        if s.first_tool_position > 0:
            stats["first_tool_position"][s.first_tool_position] = stats["first_tool_position"].get(s.first_tool_position, 0) + 1
        
        total_tool_calls += s.num_tool_calls
        
        if s.edge_case:
            stats["edge_cases"][s.edge_case] = stats["edge_cases"].get(s.edge_case, 0) + 1
    
    stats["avg_tool_calls"] = total_tool_calls / n

    # Convert to percentages
    for key in ["language_combo", "call_type", "conversation_length", "user_style", "system_prompt_type", "num_tools_available"]:
        for k, v in stats[key].items():
            stats[key][k] = f"{v} ({v/n*100:.1f}%)"
    
    return stats


def print_analysis(stats: Dict):
    """Prints the analysis in a readable form."""
    print("=" * 60)
    print(f"DISTRIBUTION ANALYSIS - {stats['total_samples']} samples")
    print("=" * 60)

    print("\nLANGUAGE (tool, conv):")
    for k, v in stats["language_combo"].items():
        print(f"   {k}: {v}")

    print("\nCALL TYPE:")
    for k, v in stats["call_type"].items():
        print(f"   {k}: {v}")

    print("\nPOSITIVE TYPE:")
    for k, v in stats["positive_type"].items():
        print(f"   {k}: {v}")

    print("\nNEGATIVE REASON:")
    for k, v in stats["negative_reason"].items():
        print(f"   {k}: {v}")

    print("\nCLARIFICATION OUTCOME:")
    for k, v in stats["clarification_outcome"].items():
        print(f"   {k}: {v}")

    print("\nCONVERSATION LENGTH:")
    for k, v in stats["conversation_length"].items():
        print(f"   {k}: {v}")

    print("\nUSER STYLE:")
    for k, v in stats["user_style"].items():
        print(f"   {k}: {v}")

    print("\nSYSTEM PROMPT TYPE:")
    for k, v in stats["system_prompt_type"].items():
        print(f"   {k}: {v}")

    print("\nNUM TOOLS AVAILABLE:")
    for k, v in sorted(stats["num_tools_available"].items()):
        print(f"   {k}: {v}")

    print("\nFIRST TOOL POSITION (when present):")
    for k, v in sorted(stats["first_tool_position"].items()):
        print(f"   turn {k}: {v}")

    print(f"\nAVG TOOL CALLS: {stats['avg_tool_calls']:.2f}")

    print("\nEDGE CASES:")
    for k, v in stats["edge_cases"].items():
        print(f"   {k}: {v}")

    print("\nTOP 10 DOMAINS:")
    # domain is not converted to a percentage, it is still an int
    domains_sorted = sorted(stats["domain"].items(), key=lambda x: x[1] if isinstance(x[1], int) else int(x[1].split()[0]), reverse=True)[:10]
    for k, v in domains_sorted:
        if isinstance(v, int):
            print(f"   {k}: {v} ({v/stats['total_samples']*100:.1f}%)")
        else:
            print(f"   {k}: {v}")

