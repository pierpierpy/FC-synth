"""Weather-related mock tools."""

import random
from datetime import datetime, timedelta

WEATHER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather conditions for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name or coordinates"},
                    "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get weather forecast for the next days",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "description": "Number of forecast days (1-14)", "default": 7}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_alerts",
            "description": "Get active weather alerts and warnings for a region",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Region or city name"},
                    "severity": {"type": "string", "enum": ["all", "minor", "moderate", "severe"], "default": "all"}
                },
                "required": ["region"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_air_quality",
            "description": "Get air quality index and pollutant levels",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City or address"},
                    "include_forecast": {"type": "boolean", "default": False}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_uv_index",
            "description": "Get UV index and sun exposure recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                },
                "required": ["location"]
            }
        }
    },
]

# Mock data pools
WEATHER_CONDITIONS = ["Sereno", "Parzialmente nuvoloso", "Nuvoloso", "Pioggia leggera", "Pioggia", "Temporale", "Neve", "Nebbia"]
WEATHER_CONDITIONS_EN = ["Clear", "Partly cloudy", "Cloudy", "Light rain", "Rain", "Thunderstorm", "Snow", "Fog"]

CITIES_IT = ["Milano", "Roma", "Napoli", "Torino", "Firenze", "Bologna", "Venezia", "Palermo", "Genova", "Bari"]
CITIES_WORLD = ["London", "Paris", "New York", "Tokyo", "Berlin", "Madrid", "Amsterdam", "Vienna", "Prague", "Lisbon"]


def execute_weather_tool(tool_name: str, args: dict) -> dict:
    """Execute weather mock tool."""
    
    if tool_name == "get_current_weather":
        location = args.get("location", "Milano")
        units = args.get("units", "celsius")
        temp = random.randint(5, 35) if units == "celsius" else random.randint(40, 95)
        condition = random.choice(WEATHER_CONDITIONS)
        return {
            "location": location,
            "temperature": temp,
            "units": units,
            "condition": condition,
            "humidity": random.randint(30, 90),
            "wind_speed": random.randint(0, 50),
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "feels_like": temp + random.randint(-3, 3),
            "pressure": random.randint(990, 1030),
            "visibility": random.randint(5, 20),
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "get_weather_forecast":
        location = args.get("location", "Milano")
        days = args.get("days", 7)
        forecast = []
        base_temp = random.randint(10, 25)
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append({
                "date": date,
                "condition": random.choice(WEATHER_CONDITIONS),
                "temp_min": base_temp + random.randint(-5, 0),
                "temp_max": base_temp + random.randint(0, 10),
                "precipitation_prob": random.randint(0, 100),
                "humidity": random.randint(40, 85)
            })
        return {
            "location": location,
            "forecast": forecast,
            "generated_at": datetime.now().isoformat()
        }
    
    elif tool_name == "get_weather_alerts":
        region = args.get("region", "Lombardia")
        severity = args.get("severity", "all")
        # 30% chance of having alerts
        if random.random() < 0.3:
            alert_types = ["Allerta meteo gialla", "Allerta meteo arancione", "Rischio temporali", "Vento forte", "Neve in quota"]
            return {
                "region": region,
                "alerts": [{
                    "type": random.choice(alert_types),
                    "severity": random.choice(["minor", "moderate", "severe"]) if severity == "all" else severity,
                    "description": "Si prevede maltempo nelle prossime 24-48 ore. Prestare attenzione.",
                    "valid_from": datetime.now().isoformat(),
                    "valid_until": (datetime.now() + timedelta(hours=random.randint(12, 48))).isoformat()
                }],
                "total_alerts": 1
            }
        return {
            "region": region,
            "alerts": [],
            "total_alerts": 0,
            "message": "Nessuna allerta attiva per questa regione"
        }
    
    elif tool_name == "get_air_quality":
        location = args.get("location", "Milano")
        aqi = random.randint(20, 150)
        if aqi <= 50:
            quality = "Buona"
        elif aqi <= 100:
            quality = "Moderata"
        else:
            quality = "Scarsa"
        
        result = {
            "location": location,
            "aqi": aqi,
            "quality": quality,
            "pollutants": {
                "pm25": round(random.uniform(5, 80), 1),
                "pm10": round(random.uniform(10, 120), 1),
                "o3": round(random.uniform(20, 100), 1),
                "no2": round(random.uniform(10, 80), 1),
                "co": round(random.uniform(0.1, 2), 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if args.get("include_forecast", False):
            result["forecast"] = [
                {"date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"), "aqi": random.randint(20, 150)}
                for i in range(1, 4)
            ]
        return result
    
    elif tool_name == "get_uv_index":
        location = args.get("location", "Milano")
        uv = random.randint(1, 11)
        if uv <= 2:
            risk = "Basso"
            advice = "Nessuna protezione necessaria"
        elif uv <= 5:
            risk = "Moderato"
            advice = "Usa protezione solare SPF 30+"
        elif uv <= 7:
            risk = "Alto"
            advice = "Usa protezione solare SPF 50+, cerca l'ombra"
        elif uv <= 10:
            risk = "Molto alto"
            advice = "Evita l'esposizione nelle ore centrali"
        else:
            risk = "Estremo"
            advice = "Evita l'esposizione al sole"
        
        return {
            "location": location,
            "date": args.get("date", datetime.now().strftime("%Y-%m-%d")),
            "uv_index": uv,
            "risk_level": risk,
            "advice": advice,
            "peak_hours": "11:00 - 15:00"
        }
    
    return {"error": f"Unknown weather tool: {tool_name}"}
