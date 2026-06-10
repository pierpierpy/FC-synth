"""Funzioni di utilità per i mock tools."""

from datetime import datetime, timedelta
import re


# Italian date words mapping
DATE_WORDS_IT = {
    "oggi": 0,
    "domani": 1,
    "dopodomani": 2,
    "ieri": -1,
    "l'altro ieri": -2,
    "lunedì": "monday",
    "martedì": "tuesday", 
    "mercoledì": "wednesday",
    "giovedì": "thursday",
    "venerdì": "friday",
    "sabato": "saturday",
    "domenica": "sunday",
    "prossima settimana": 7,
    "settimana prossima": 7,
    "fra una settimana": 7,
    "tra una settimana": 7,
    "fra due settimane": 14,
    "tra due settimane": 14,
    "fra un mese": 30,
    "tra un mese": 30,
    "fine settimana": "weekend",
    "questo weekend": "weekend",
    "prossimo weekend": "next_weekend",
}


def parse_date_flexible(date_str: str) -> datetime:
    """Parse date from various formats including Italian natural language."""
    if not date_str:
        return datetime.now()
    
    date_str_lower = date_str.lower().strip()
    
    # Check Italian date words
    if date_str_lower in DATE_WORDS_IT:
        val = DATE_WORDS_IT[date_str_lower]
        if isinstance(val, int):
            return datetime.now() + timedelta(days=val)
        elif val == "weekend":
            today = datetime.now()
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            return today + timedelta(days=days_until_saturday)
        elif val == "next_weekend":
            today = datetime.now()
            days_until_saturday = (5 - today.weekday()) % 7
            return today + timedelta(days=days_until_saturday + 7)
        elif val in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            weekdays = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
            target = weekdays[val]
            today = datetime.now()
            days_ahead = (target - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return today + timedelta(days=days_ahead)
    
    # Try standard formats
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Default to now
    return datetime.now()


def safe_int(value, default=0):
    """Safely convert value to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format amount as currency."""
    symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
