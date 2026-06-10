"""Utility functions for mock tools."""

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

# English date words
DATE_WORDS_EN = {
    "today": 0,
    "tomorrow": 1,
    "day after tomorrow": 2,
    "yesterday": -1,
    "next week": 7,
    "in a week": 7,
    "in two weeks": 14,
    "next month": 30,
    "this weekend": "weekend",
    "next weekend": "next_weekend",
    "monday": "monday",
    "tuesday": "tuesday",
    "wednesday": "wednesday",
    "thursday": "thursday",
    "friday": "friday",
    "saturday": "saturday",
    "sunday": "sunday",
}


def parse_date_flexible(date_str: str | None, default: datetime | None = None) -> datetime:
    """
    Parse a date string flexibly, handling:
    - ISO format (YYYY-MM-DD)
    - Italian words (oggi, domani, dopodomani, etc.)
    - English words (today, tomorrow, etc.)
    - Weekday names
    - Relative phrases
    
    Returns a datetime object.
    """
    if date_str is None:
        return default or datetime.now()
    
    # Clean input
    date_str_lower = date_str.strip().lower()
    
    # Try ISO format first
    try:
        return datetime.strptime(date_str_lower, "%Y-%m-%d")
    except ValueError:
        pass
    
    # Try ISO datetime format
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    
    # Try common date formats
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%d %B %Y", "%d %b %Y"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    
    now = datetime.now()
    
    # Check Italian words
    for word, value in DATE_WORDS_IT.items():
        if word in date_str_lower:
            if isinstance(value, int):
                return now + timedelta(days=value)
            elif value == "weekend":
                # This weekend (next Saturday)
                days_until_saturday = (5 - now.weekday()) % 7
                if days_until_saturday == 0 and now.hour >= 12:
                    days_until_saturday = 7
                return now + timedelta(days=days_until_saturday)
            elif value == "next_weekend":
                # Next weekend
                days_until_saturday = (5 - now.weekday()) % 7 + 7
                return now + timedelta(days=days_until_saturday)
            elif value in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                weekday_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
                              "friday": 4, "saturday": 5, "sunday": 6}
                target = weekday_map[value]
                days_ahead = (target - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7  # Next occurrence
                return now + timedelta(days=days_ahead)
    
    # Check English words
    for word, value in DATE_WORDS_EN.items():
        if word in date_str_lower:
            if isinstance(value, int):
                return now + timedelta(days=value)
            elif value == "weekend":
                days_until_saturday = (5 - now.weekday()) % 7
                if days_until_saturday == 0 and now.hour >= 12:
                    days_until_saturday = 7
                return now + timedelta(days=days_until_saturday)
            elif value == "next_weekend":
                days_until_saturday = (5 - now.weekday()) % 7 + 7
                return now + timedelta(days=days_until_saturday)
            elif value in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                weekday_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
                              "friday": 4, "saturday": 5, "sunday": 6}
                target = weekday_map[value]
                days_ahead = (target - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                return now + timedelta(days=days_ahead)
    
    # Try to extract numbers like "fra 3 giorni" or "in 5 days"
    match = re.search(r'(?:fra|tra|in)\s*(\d+)\s*(?:giorn|day)', date_str_lower)
    if match:
        days = int(match.group(1))
        return now + timedelta(days=days)
    
    # Default: return now or default
    return default or now


def safe_int(value, default: int = 1) -> int:
    """Safely convert a value to int."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Handle comma as decimal separator
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
    except (ValueError, TypeError):
        return default
