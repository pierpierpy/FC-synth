"""
Mock Tools Library for Realistic Multi-Turn FC Conversations

This module provides 130+ realistic mock tools organized by category.
Each mock returns plausible, contextually appropriate data.
"""

from .weather import WEATHER_TOOLS, execute_weather_tool
from .finance import FINANCE_TOOLS, execute_finance_tool
from .calendar import CALENDAR_TOOLS, execute_calendar_tool
from .search import SEARCH_TOOLS, execute_search_tool
from .communication import COMMUNICATION_TOOLS, execute_communication_tool
from .productivity import PRODUCTIVITY_TOOLS, execute_productivity_tool
from .travel import TRAVEL_TOOLS, execute_travel_tool
from .ecommerce import ECOMMERCE_TOOLS, execute_ecommerce_tool
from .smart_home import SMART_HOME_TOOLS, execute_smart_home_tool
from .media import MEDIA_TOOLS, execute_media_tool
from .health import HEALTH_TOOLS, execute_health_tool
from .utilities import UTILITY_TOOLS, execute_utility_tool
# New advanced modules
from .database import DATABASE_TOOLS, execute_database_tool
from .documents import DOCUMENT_TOOLS, execute_document_tool
from .social_media import SOCIAL_TOOLS, execute_social_tool
from .code_tools import CODE_TOOLS, execute_code_tool
from .booking import BOOKING_TOOLS, execute_booking_tool
from .news import NEWS_TOOLS, execute_news_tool
from .government import GOVERNMENT_TOOLS, execute_government_tool
from .iot_sensors import IOT_TOOLS, execute_iot_tool
from .crm import CRM_TOOLS, execute_crm_tool
from .knowledge_base import KNOWLEDGE_BASE_TOOLS

# All tools combined
ALL_TOOLS = (
    WEATHER_TOOLS +
    FINANCE_TOOLS +
    CALENDAR_TOOLS +
    SEARCH_TOOLS +
    COMMUNICATION_TOOLS +
    PRODUCTIVITY_TOOLS +
    TRAVEL_TOOLS +
    ECOMMERCE_TOOLS +
    SMART_HOME_TOOLS +
    MEDIA_TOOLS +
    HEALTH_TOOLS +
    UTILITY_TOOLS +
    # New modules
    DATABASE_TOOLS +
    DOCUMENT_TOOLS +
    SOCIAL_TOOLS +
    CODE_TOOLS +
    BOOKING_TOOLS +
    NEWS_TOOLS +
    GOVERNMENT_TOOLS +
    IOT_TOOLS +
    CRM_TOOLS +
    KNOWLEDGE_BASE_TOOLS
)

# Tool name -> category mapping
TOOL_CATEGORIES = {}
for tool in WEATHER_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "weather"
for tool in FINANCE_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "finance"
for tool in CALENDAR_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "calendar"
for tool in SEARCH_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "search"
for tool in COMMUNICATION_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "communication"
for tool in PRODUCTIVITY_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "productivity"
for tool in TRAVEL_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "travel"
for tool in ECOMMERCE_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "ecommerce"
for tool in SMART_HOME_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "smart_home"
for tool in MEDIA_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "media"
for tool in HEALTH_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "health"
for tool in UTILITY_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "utilities"
# New modules categories
for tool in DATABASE_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "database"
for tool in DOCUMENT_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "documents"
for tool in SOCIAL_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "social_media"
for tool in CODE_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "code"
for tool in BOOKING_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "booking"
for tool in NEWS_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "news"
for tool in GOVERNMENT_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "government"
for tool in IOT_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "iot"
for tool in CRM_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "crm"
for tool in KNOWLEDGE_BASE_TOOLS:
    TOOL_CATEGORIES[tool["function"]["name"]] = "knowledge_base"

# Executor mapping
EXECUTORS = {
    "weather": execute_weather_tool,
    "finance": execute_finance_tool,
    "calendar": execute_calendar_tool,
    "search": execute_search_tool,
    "communication": execute_communication_tool,
    "productivity": execute_productivity_tool,
    "travel": execute_travel_tool,
    "ecommerce": execute_ecommerce_tool,
    "smart_home": execute_smart_home_tool,
    "media": execute_media_tool,
    "health": execute_health_tool,
    "utilities": execute_utility_tool,
    # New executors
    "database": execute_database_tool,
    "documents": execute_document_tool,
    "social_media": execute_social_tool,
    "code": execute_code_tool,
    "booking": execute_booking_tool,
    "news": execute_news_tool,
    "government": execute_government_tool,
    "iot": execute_iot_tool,
    "crm": execute_crm_tool,
}


def sanitize_arguments(arguments: dict) -> dict:
    """
    Sanitize tool arguments to handle common type mismatches.
    LLMs sometimes return strings where ints are expected.
    """
    sanitized = {}
    for key, value in arguments.items():
        # Handle integer fields that might be strings
        if key in ('limit', 'quantity', 'count', 'num', 'number', 'duration', 
                   'duration_minutes', 'party_size', 'guests', 'rooms', 
                   'passengers', 'data_points', 'reminder_minutes', 'timeout',
                   'min_stars', 'rating_min', 'failed', 'passed'):
            if isinstance(value, str):
                try:
                    sanitized[key] = int(value)
                except ValueError:
                    sanitized[key] = 1  # Default fallback
            else:
                sanitized[key] = value
        # Handle float fields
        elif key in ('min_price', 'max_price', 'amount', 'temperature', 
                     'rating', 'latitude', 'longitude'):
            if isinstance(value, str):
                try:
                    sanitized[key] = float(value.replace(',', '.'))
                except ValueError:
                    sanitized[key] = 0.0
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value
    return sanitized


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a mock tool and return realistic results."""
    category = TOOL_CATEGORIES.get(tool_name)
    if not category:
        return {"error": f"Unknown tool: {tool_name}"}
    
    # Sanitize arguments to handle type mismatches
    safe_args = sanitize_arguments(arguments)

    executor = EXECUTORS.get(category)
    if executor is None:
        return {"error": f"No executor registered for category: {category}"}
    return executor(tool_name, safe_args)


def get_tools_by_category(categories: list[str]) -> list[dict]:
    """Get tools filtered by category names."""
    result = []
    category_map = {
        "weather": WEATHER_TOOLS,
        "finance": FINANCE_TOOLS,
        "calendar": CALENDAR_TOOLS,
        "search": SEARCH_TOOLS,
        "communication": COMMUNICATION_TOOLS,
        "productivity": PRODUCTIVITY_TOOLS,
        "travel": TRAVEL_TOOLS,
        "ecommerce": ECOMMERCE_TOOLS,
        "smart_home": SMART_HOME_TOOLS,
        "media": MEDIA_TOOLS,
        "health": HEALTH_TOOLS,
        "utilities": UTILITY_TOOLS,
        # New categories
        "database": DATABASE_TOOLS,
        "documents": DOCUMENT_TOOLS,
        "social_media": SOCIAL_TOOLS,
        "code": CODE_TOOLS,
        "booking": BOOKING_TOOLS,
        "news": NEWS_TOOLS,
        "government": GOVERNMENT_TOOLS,
        "iot": IOT_TOOLS,
        "crm": CRM_TOOLS,
        "knowledge_base": KNOWLEDGE_BASE_TOOLS,
    }
    for cat in categories:
        if cat in category_map:
            result.extend(category_map[cat])
    return result


def get_random_tool_subset(n: int = 8, categories: list[str] | None = None) -> list[dict]:
    """Get a random subset of tools, optionally filtered by categories."""
    import random
    
    if categories:
        pool = get_tools_by_category(categories)
    else:
        pool = ALL_TOOLS
    
    return random.sample(pool, min(n, len(pool)))


# Tools by category (same structure as Italian STRUMENTI_PER_CATEGORIA)
TOOLS_BY_CATEGORY = {
    "weather": WEATHER_TOOLS,
    "finance": FINANCE_TOOLS,
    "calendar": CALENDAR_TOOLS,
    "search": SEARCH_TOOLS,
    "communication": COMMUNICATION_TOOLS,
    "productivity": PRODUCTIVITY_TOOLS,
    "travel": TRAVEL_TOOLS,
    "ecommerce": ECOMMERCE_TOOLS,
    "smart_home": SMART_HOME_TOOLS,
    "media": MEDIA_TOOLS,
    "health": HEALTH_TOOLS,
    "utilities": UTILITY_TOOLS,
    "database": DATABASE_TOOLS,
    "documents": DOCUMENT_TOOLS,
    "social_media": SOCIAL_TOOLS,
    "code": CODE_TOOLS,
    "booking": BOOKING_TOOLS,
    "news": NEWS_TOOLS,
    "government": GOVERNMENT_TOOLS,
    "iot": IOT_TOOLS,
    "crm": CRM_TOOLS,
    "knowledge_base": KNOWLEDGE_BASE_TOOLS,
}
