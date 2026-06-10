"""Utility and miscellaneous mock tools."""

import random
from datetime import datetime, timedelta
import math

UTILITY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression to evaluate"},
                    "precision": {"type": "integer", "default": 2}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_units",
            "description": "Convert between different units of measurement",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "from_unit": {"type": "string"},
                    "to_unit": {"type": "string"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current date and time for a timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "Timezone name or offset"},
                    "format": {"type": "string", "enum": ["full", "date", "time"], "default": "full"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_password",
            "description": "Generate a secure random password",
            "parameters": {
                "type": "object",
                "properties": {
                    "length": {"type": "integer", "default": 16},
                    "include_symbols": {"type": "boolean", "default": True},
                    "include_numbers": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_qr_code",
            "description": "Generate a QR code for text or URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Text or URL to encode"},
                    "size": {"type": "string", "enum": ["small", "medium", "large"], "default": "medium"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "shorten_url",
            "description": "Create a shortened URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Long URL to shorten"},
                    "custom_alias": {"type": "string", "description": "Custom short alias (optional)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_random_fact",
            "description": "Get a random interesting fact",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["science", "history", "nature", "technology", "any"]}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_quote",
            "description": "Get an inspirational or famous quote",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["motivational", "wisdom", "funny", "famous", "any"]}
                },
                "required": []
            }
        }
    },
]

# Mock data
UNIT_CONVERSIONS = {
    ("km", "miles"): 0.621371,
    ("miles", "km"): 1.60934,
    ("kg", "lb"): 2.20462,
    ("lb", "kg"): 0.453592,
    ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
    ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
    ("meters", "feet"): 3.28084,
    ("feet", "meters"): 0.3048,
    ("liters", "gallons"): 0.264172,
    ("gallons", "liters"): 3.78541,
    ("cm", "inches"): 0.393701,
    ("inches", "cm"): 2.54,
}

FACTS = {
    "science": [
        "Il DNA umano è identico al 60% a quello di una banana.",
        "La luce del sole impiega circa 8 minuti per raggiungere la Terra.",
        "Il cervello umano usa circa il 20% dell'energia totale del corpo.",
    ],
    "history": [
        "La Grande Muraglia Cinese non è visibile dallo spazio a occhio nudo.",
        "Cleopatra visse più vicino nel tempo allo sbarco sulla Luna che alla costruzione delle piramidi.",
        "Oxford University è più antica dell'Impero Azteco.",
    ],
    "nature": [
        "Gli elefanti sono gli unici animali che non possono saltare.",
        "I polpi hanno tre cuori e sangue blu.",
        "Le api possono riconoscere i volti umani.",
    ],
    "technology": [
        "Il primo computer pesava più di 27 tonnellate.",
        "Ci sono più dispositivi connessi a internet che persone sulla Terra.",
        "Il primo SMS fu inviato nel 1992 e diceva 'Merry Christmas'.",
    ],
}

QUOTES = {
    "motivational": [
        {"text": "Il successo non è definitivo, il fallimento non è fatale: ciò che conta è il coraggio di continuare.", "author": "Winston Churchill"},
        {"text": "L'unico modo per fare un ottimo lavoro è amare quello che fai.", "author": "Steve Jobs"},
    ],
    "wisdom": [
        {"text": "La vita è quello che ti accade mentre sei impegnato a fare altri progetti.", "author": "John Lennon"},
        {"text": "Sii il cambiamento che vuoi vedere nel mondo.", "author": "Mahatma Gandhi"},
    ],
    "funny": [
        {"text": "Non ho fallito. Ho solo trovato 10.000 modi che non funzionano.", "author": "Thomas Edison"},
        {"text": "L'unica cosa che so è che non so nulla.", "author": "Socrate"},
    ],
    "famous": [
        {"text": "Essere o non essere, questo è il problema.", "author": "William Shakespeare"},
        {"text": "Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura.", "author": "Dante Alighieri"},
    ],
}

TIMEZONES = {
    "Rome": 1, "London": 0, "New York": -5, "Los Angeles": -8,
    "Tokyo": 9, "Sydney": 11, "Dubai": 4, "Moscow": 3,
    "CET": 1, "EST": -5, "PST": -8, "UTC": 0,
}


def execute_utility_tool(tool_name: str, args: dict) -> dict:
    """Execute utility mock tool."""
    
    if tool_name == "calculate":
        expression = args.get("expression", "0")
        precision = args.get("precision", 2)
        
        # Safe evaluation of simple math expressions
        try:
            # Allow only safe math operations
            allowed_chars = set("0123456789+-*/().^ ")
            if all(c in allowed_chars for c in expression):
                # Replace ^ with ** for power
                expr = expression.replace("^", "**")
                result = eval(expr)
                return {
                    "expression": expression,
                    "result": round(result, precision),
                    "formatted": f"{round(result, precision):,}"
                }
            else:
                return {"error": "Expression contains invalid characters"}
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}
    
    elif tool_name == "convert_units":
        value = args.get("value", 0)
        from_unit = args.get("from_unit", "").lower()
        to_unit = args.get("to_unit", "").lower()
        
        key = (from_unit, to_unit)
        if key in UNIT_CONVERSIONS:
            factor = UNIT_CONVERSIONS[key]
            if callable(factor):
                result = factor(value)
            else:
                result = value * factor
            
            return {
                "original": {"value": value, "unit": from_unit},
                "converted": {"value": round(result, 4), "unit": to_unit},
                "formula": f"{value} {from_unit} = {round(result, 4)} {to_unit}"
            }
        else:
            return {
                "error": f"Conversion from {from_unit} to {to_unit} not supported",
                "supported_conversions": list(UNIT_CONVERSIONS.keys())
            }
    
    elif tool_name == "get_current_time":
        tz = args.get("timezone", "Rome")
        fmt = args.get("format", "full")
        
        offset = TIMEZONES.get(tz, 1)  # Default to Rome (CET)
        now = datetime.utcnow() + timedelta(hours=offset)
        
        if fmt == "date":
            formatted = now.strftime("%Y-%m-%d")
        elif fmt == "time":
            formatted = now.strftime("%H:%M:%S")
        else:
            formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "timezone": tz,
            "utc_offset": f"UTC{'+' if offset >= 0 else ''}{offset}",
            "datetime": formatted,
            "timestamp": int(now.timestamp()),
            "day_of_week": now.strftime("%A")
        }
    
    elif tool_name == "generate_password":
        length = args.get("length", 16)
        include_symbols = args.get("include_symbols", True)
        include_numbers = args.get("include_numbers", True)
        
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if include_numbers:
            chars += "0123456789"
        if include_symbols:
            chars += "!@#$%^&*()-_=+"
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Strength calculation
        strength = "debole"
        if length >= 12 and include_numbers and include_symbols:
            strength = "forte"
        elif length >= 8:
            strength = "media"
        
        return {
            "password": password,
            "length": length,
            "strength": strength,
            "includes_numbers": include_numbers,
            "includes_symbols": include_symbols
        }
    
    elif tool_name == "generate_qr_code":
        content = args.get("content", "")
        size = args.get("size", "medium")
        
        sizes = {"small": 150, "medium": 250, "large": 400}
        
        return {
            "content": content,
            "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size={sizes[size]}x{sizes[size]}&data={content}",
            "size_px": sizes[size],
            "format": "PNG"
        }
    
    elif tool_name == "shorten_url":
        url = args.get("url", "")
        alias = args.get("custom_alias")
        
        short_id = alias or ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
        
        return {
            "original_url": url,
            "short_url": f"https://short.link/{short_id}",
            "alias": short_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
        }
    
    elif tool_name == "get_random_fact":
        category = args.get("category", "any")
        
        if category == "any":
            category = random.choice(list(FACTS.keys()))
        
        facts = FACTS.get(category, FACTS["science"])
        
        return {
            "category": category,
            "fact": random.choice(facts),
            "source": "Enciclopedia dei fatti interessanti"
        }
    
    elif tool_name == "get_quote":
        category = args.get("category", "any")
        
        if category == "any":
            category = random.choice(list(QUOTES.keys()))
        
        quotes = QUOTES.get(category, QUOTES["wisdom"])
        quote = random.choice(quotes)
        
        return {
            "category": category,
            "quote": quote["text"],
            "author": quote["author"]
        }
    
    return {"error": f"Unknown utility tool: {tool_name}"}
