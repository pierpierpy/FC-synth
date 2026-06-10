"""IoT sensors and monitoring mock tools."""

import random
from datetime import datetime, timedelta

IOT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_sensor_data",
            "description": "Get data from IoT sensors",
            "parameters": {
                "type": "object",
                "properties": {
                    "sensor_id": {"type": "string"},
                    "sensor_type": {"type": "string", "enum": ["temperature", "humidity", "motion", "air_quality", "noise", "light", "pressure", "water", "energy"]},
                    "location": {"type": "string"},
                    "timerange": {"type": "string", "enum": ["realtime", "1h", "24h", "7d", "30d"]}
                },
                "required": ["sensor_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_sensor_alert",
            "description": "Configure alerts for sensor thresholds",
            "parameters": {
                "type": "object",
                "properties": {
                    "sensor_id": {"type": "string"},
                    "condition": {"type": "string", "enum": ["above", "below", "equals", "change"]},
                    "threshold": {"type": "number"},
                    "alert_method": {"type": "string", "enum": ["push", "email", "sms", "webhook"]},
                    "cooldown_minutes": {"type": "integer", "default": 15}
                },
                "required": ["sensor_id", "condition", "threshold"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_status",
            "description": "Get status of connected IoT devices",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "string"},
                    "device_type": {"type": "string", "enum": ["sensor", "actuator", "gateway", "camera", "speaker", "display"]},
                    "include_diagnostics": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_actuator",
            "description": "Control an IoT actuator (relay, motor, valve, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "actuator_id": {"type": "string"},
                    "action": {"type": "string", "enum": ["on", "off", "toggle", "set_level", "pulse"]},
                    "value": {"type": "number", "description": "Value for set_level (0-100)"},
                    "duration_seconds": {"type": "integer", "description": "Duration for pulse action"}
                },
                "required": ["actuator_id", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_energy_consumption",
            "description": "Get energy consumption data from smart meters",
            "parameters": {
                "type": "object",
                "properties": {
                    "meter_id": {"type": "string"},
                    "period": {"type": "string", "enum": ["today", "yesterday", "week", "month", "year"]},
                    "granularity": {"type": "string", "enum": ["hourly", "daily", "weekly", "monthly"]},
                    "compare_previous": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_automation_rule",
            "description": "Create an automation rule for IoT devices",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "trigger": {"type": "object", "description": "Trigger condition (sensor, time, event)"},
                    "action": {"type": "object", "description": "Action to perform"},
                    "conditions": {"type": "array", "items": {"type": "object"}, "description": "Additional conditions"},
                    "enabled": {"type": "boolean", "default": True}
                },
                "required": ["name", "trigger", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_environmental_data",
            "description": "Get environmental monitoring data (outdoor/indoor)",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "metrics": {"type": "array", "items": {"type": "string", "enum": ["temperature", "humidity", "pm25", "pm10", "co2", "voc", "noise", "uv"]}},
                    "timerange": {"type": "string", "enum": ["current", "24h", "7d"]}
                },
                "required": ["location"]
            }
        }
    },
]

# Mock data
SENSOR_LOCATIONS = ["Soggiorno", "Camera da letto", "Cucina", "Bagno", "Garage", "Giardino", "Ufficio", "Cantina"]


def execute_iot_tool(tool_name: str, args: dict) -> dict:
    """Execute IoT mock tool."""
    
    if tool_name == "get_sensor_data":
        sensor_type = args.get("sensor_type", "temperature")
        sensor_id = args.get("sensor_id", f"sensor_{random.randint(1000, 9999)}")
        location = args.get("location", random.choice(SENSOR_LOCATIONS))
        timerange = args.get("timerange", "realtime")
        
        # Generate realistic sensor data based on type
        sensor_ranges = {
            "temperature": {"min": 15, "max": 30, "unit": "°C"},
            "humidity": {"min": 30, "max": 80, "unit": "%"},
            "motion": {"min": 0, "max": 1, "unit": "detected"},
            "air_quality": {"min": 0, "max": 500, "unit": "AQI"},
            "noise": {"min": 20, "max": 90, "unit": "dB"},
            "light": {"min": 0, "max": 1000, "unit": "lux"},
            "pressure": {"min": 980, "max": 1050, "unit": "hPa"},
            "water": {"min": 0, "max": 100, "unit": "L"},
            "energy": {"min": 0, "max": 5000, "unit": "W"}
        }
        
        range_info = sensor_ranges.get(sensor_type, {"min": 0, "max": 100, "unit": ""})
        current_value = round(random.uniform(range_info["min"], range_info["max"]), 1)
        
        result = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "location": location,
            "current": {
                "value": current_value,
                "unit": range_info["unit"],
                "timestamp": datetime.now().isoformat(),
                "quality": random.choice(["good", "good", "good", "degraded"])
            },
            "status": "online",
            "battery_level": random.randint(20, 100) if random.random() > 0.3 else None
        }
        
        if timerange != "realtime":
            # Generate historical data
            hours = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}[timerange]
            data_points = min(hours, 48)
            
            result["history"] = {
                "period": timerange,
                "data_points": data_points,
                "values": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=i * (hours // data_points))).isoformat(),
                        "value": round(random.uniform(range_info["min"], range_info["max"]), 1)
                    } for i in range(data_points)
                ],
                "statistics": {
                    "min": round(random.uniform(range_info["min"], current_value), 1),
                    "max": round(random.uniform(current_value, range_info["max"]), 1),
                    "avg": round(current_value + random.uniform(-5, 5), 1),
                    "trend": random.choice(["rising", "falling", "stable"])
                }
            }
        
        return result
    
    elif tool_name == "set_sensor_alert":
        alert_id = f"ALERT{random.randint(10000, 99999)}"
        
        return {
            "status": "created",
            "alert": {
                "id": alert_id,
                "sensor_id": args.get("sensor_id"),
                "condition": args.get("condition"),
                "threshold": args.get("threshold"),
                "alert_method": args.get("alert_method", "push"),
                "cooldown_minutes": args.get("cooldown_minutes", 15),
                "enabled": True,
                "created_at": datetime.now().isoformat()
            },
            "message": f"Alert configurato: notifica quando valore {args.get('condition')} {args.get('threshold')}"
        }
    
    elif tool_name == "get_device_status":
        device_id = args.get("device_id")
        device_type = args.get("device_type")
        include_diagnostics = args.get("include_diagnostics", False)
        
        # Generate list of devices or single device
        if device_id:
            devices = [{
                "id": device_id,
                "type": device_type or random.choice(["sensor", "actuator", "gateway"]),
                "name": f"Dispositivo {device_id}",
                "status": random.choice(["online", "online", "online", "offline"]),
                "last_seen": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                "location": random.choice(SENSOR_LOCATIONS),
                "firmware_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}"
            }]
        else:
            devices = []
            for i in range(random.randint(5, 15)):
                devices.append({
                    "id": f"device_{random.randint(1000, 9999)}",
                    "type": random.choice(["sensor", "actuator", "gateway", "camera", "speaker"]),
                    "name": f"{random.choice(['Sensore', 'Attuatore', 'Gateway', 'Camera'])} {random.choice(SENSOR_LOCATIONS)}",
                    "status": random.choice(["online", "online", "online", "offline", "updating"]),
                    "last_seen": (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
                    "location": random.choice(SENSOR_LOCATIONS)
                })
        
        result = {
            "devices": devices,
            "total": len(devices),
            "online": sum(1 for d in devices if d["status"] == "online"),
            "offline": sum(1 for d in devices if d["status"] == "offline")
        }
        
        if include_diagnostics and device_id:
            result["diagnostics"] = {
                "uptime_hours": random.randint(1, 8760),
                "memory_used_percent": random.randint(20, 80),
                "cpu_usage_percent": random.randint(5, 50),
                "wifi_signal_dbm": random.randint(-80, -30),
                "errors_last_24h": random.randint(0, 5),
                "last_restart": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
        
        return result
    
    elif tool_name == "control_actuator":
        actuator_id = args.get("actuator_id")
        action = args.get("action")
        value = args.get("value")
        
        # Simulate action result
        success = random.random() > 0.05  # 95% success rate
        
        if success:
            new_state = {
                "on": "on",
                "off": "off",
                "toggle": random.choice(["on", "off"]),
                "set_level": f"{value}%",
                "pulse": "pulsed"
            }.get(action, "unknown")
            
            return {
                "status": "success",
                "actuator_id": actuator_id,
                "action_performed": action,
                "new_state": new_state,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "response_time_ms": random.randint(50, 500)
            }
        else:
            return {
                "status": "error",
                "actuator_id": actuator_id,
                "error": "Dispositivo non raggiungibile",
                "retry_suggested": True
            }
    
    elif tool_name == "get_energy_consumption":
        period = args.get("period", "today")
        granularity = args.get("granularity", "hourly")
        compare_previous = args.get("compare_previous", False)
        
        period_multipliers = {"today": 1, "yesterday": 1, "week": 7, "month": 30, "year": 365}
        base_consumption = random.uniform(5, 15)  # kWh per day
        total_kwh = round(base_consumption * period_multipliers.get(period, 1), 2)
        
        result = {
            "meter_id": args.get("meter_id", f"meter_{random.randint(1000, 9999)}"),
            "period": period,
            "consumption": {
                "total_kwh": total_kwh,
                "total_cost": round(total_kwh * 0.25, 2),  # €0.25/kWh
                "currency": "EUR",
                "co2_kg": round(total_kwh * 0.4, 2)
            },
            "breakdown": {
                "peak_hours": round(total_kwh * 0.6, 2),
                "off_peak_hours": round(total_kwh * 0.4, 2),
                "by_device": {
                    "Climatizzazione": f"{random.randint(30, 50)}%",
                    "Elettrodomestici": f"{random.randint(20, 30)}%",
                    "Illuminazione": f"{random.randint(10, 20)}%",
                    "Altro": f"{random.randint(5, 15)}%"
                }
            },
            "readings": []
        }
        
        # Generate granular readings
        if granularity == "hourly" and period in ["today", "yesterday"]:
            for h in range(24):
                result["readings"].append({
                    "hour": f"{h:02d}:00",
                    "kwh": round(random.uniform(0.1, 1.5), 2)
                })
        
        if compare_previous:
            prev_consumption = total_kwh * random.uniform(0.8, 1.2)
            result["comparison"] = {
                "previous_period_kwh": round(prev_consumption, 2),
                "change_percent": round(((total_kwh - prev_consumption) / prev_consumption) * 100, 1),
                "trend": "increase" if total_kwh > prev_consumption else "decrease"
            }
        
        return result
    
    elif tool_name == "create_automation_rule":
        rule_id = f"RULE{random.randint(10000, 99999)}"
        
        return {
            "status": "created",
            "rule": {
                "id": rule_id,
                "name": args.get("name"),
                "trigger": args.get("trigger"),
                "action": args.get("action"),
                "conditions": args.get("conditions", []),
                "enabled": args.get("enabled", True),
                "created_at": datetime.now().isoformat(),
                "executions_count": 0
            },
            "message": f"Regola '{args.get('name')}' creata con successo"
        }
    
    elif tool_name == "get_environmental_data":
        location = args.get("location", "Indoor")
        metrics = args.get("metrics", ["temperature", "humidity", "co2"])
        timerange = args.get("timerange", "current")
        
        data = {}
        metric_ranges = {
            "temperature": {"value": round(random.uniform(18, 28), 1), "unit": "°C", "rating": "good"},
            "humidity": {"value": random.randint(35, 65), "unit": "%", "rating": "good"},
            "pm25": {"value": random.randint(5, 50), "unit": "µg/m³", "rating": random.choice(["good", "moderate"])},
            "pm10": {"value": random.randint(10, 80), "unit": "µg/m³", "rating": random.choice(["good", "moderate"])},
            "co2": {"value": random.randint(400, 1500), "unit": "ppm", "rating": random.choice(["good", "moderate", "poor"])},
            "voc": {"value": random.randint(50, 500), "unit": "ppb", "rating": random.choice(["good", "moderate"])},
            "noise": {"value": random.randint(30, 70), "unit": "dB", "rating": random.choice(["good", "moderate"])},
            "uv": {"value": random.randint(1, 11), "unit": "index", "rating": random.choice(["low", "moderate", "high"])}
        }
        
        for metric in metrics:
            if metric in metric_ranges:
                data[metric] = metric_ranges[metric]
        
        return {
            "location": location,
            "timerange": timerange,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "overall_quality": random.choice(["Buona", "Moderata", "Scarsa"]),
            "recommendations": [
                "Aprire le finestre per migliorare la ventilazione"
            ] if any(d.get("rating") == "poor" for d in data.values()) else []
        }
    
    return {"error": f"Unknown IoT tool: {tool_name}"}
