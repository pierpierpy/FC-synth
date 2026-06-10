"""Smart home and IoT device mock tools."""

import random
from datetime import datetime, timedelta

SMART_HOME_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "control_lights",
            "description": "Control smart lights (on/off, brightness, color)",
            "parameters": {
                "type": "object",
                "properties": {
                    "room": {"type": "string", "description": "Room name or 'all'"},
                    "action": {"type": "string", "enum": ["on", "off", "toggle", "dim", "brighten"]},
                    "brightness": {"type": "integer", "description": "Brightness level 0-100"},
                    "color": {"type": "string", "description": "Color name or hex code"}
                },
                "required": ["room", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_thermostat",
            "description": "Control smart thermostat temperature",
            "parameters": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number", "description": "Target temperature in Celsius"},
                    "mode": {"type": "string", "enum": ["heat", "cool", "auto", "off"]},
                    "zone": {"type": "string", "description": "Zone name (optional)"}
                },
                "required": ["temperature"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_home_status",
            "description": "Get overall smart home status and device states",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_energy": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_door_lock",
            "description": "Lock or unlock smart door locks",
            "parameters": {
                "type": "object",
                "properties": {
                    "door": {"type": "string", "description": "Door identifier (front, back, garage)"},
                    "action": {"type": "string", "enum": ["lock", "unlock"]}
                },
                "required": ["door", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_security_camera_feed",
            "description": "Get security camera status or snapshot",
            "parameters": {
                "type": "object",
                "properties": {
                    "camera": {"type": "string", "description": "Camera name or location"},
                    "action": {"type": "string", "enum": ["status", "snapshot", "recording"], "default": "status"}
                },
                "required": ["camera"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_blinds",
            "description": "Control smart blinds or curtains",
            "parameters": {
                "type": "object",
                "properties": {
                    "room": {"type": "string"},
                    "position": {"type": "integer", "description": "Position 0 (closed) to 100 (open)"},
                    "action": {"type": "string", "enum": ["open", "close", "set_position"]}
                },
                "required": ["room"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Control smart speakers and play music",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["play", "pause", "stop", "next", "previous", "volume"]},
                    "query": {"type": "string", "description": "Song, artist, or playlist name"},
                    "speaker": {"type": "string", "description": "Speaker or room name"},
                    "volume": {"type": "integer", "description": "Volume level 0-100"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_alarm_system",
            "description": "Arm or disarm the home security alarm",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["arm_away", "arm_home", "disarm"]},
                    "code": {"type": "string", "description": "Security code"}
                },
                "required": ["action"]
            }
        }
    },
]

# Mock data
ROOMS = ["Soggiorno", "Camera da letto", "Cucina", "Bagno", "Studio", "Corridoio", "Ingresso"]
DEVICES_PER_ROOM = {
    "Soggiorno": ["Luce principale", "Lampada", "TV", "Smart Speaker"],
    "Camera da letto": ["Luce", "Lampada comodino", "Climatizzatore"],
    "Cucina": ["Luce", "Cappa", "Forno smart"],
    "Studio": ["Lampada scrivania", "Computer", "Stampante"],
}


def execute_smart_home_tool(tool_name: str, args: dict) -> dict:
    """Execute smart home mock tool."""
    
    if tool_name == "control_lights":
        room = args.get("room", "Soggiorno")
        action = args.get("action", "toggle")
        brightness = args.get("brightness")
        color = args.get("color")
        
        new_state = {
            "on": True, "off": False, "toggle": random.choice([True, False]),
            "dim": True, "brighten": True
        }.get(action, True)
        
        result = {
            "status": "success",
            "room": room,
            "lights_state": "accese" if new_state else "spente",
            "brightness": brightness if brightness else (random.randint(50, 100) if new_state else 0),
        }
        
        if color:
            result["color"] = color
        
        if room.lower() == "all" or room.lower() == "tutte":
            result["rooms_affected"] = ROOMS
            result["message"] = f"Tutte le luci sono state {'accese' if new_state else 'spente'}"
        else:
            result["message"] = f"Luci {room}: {'accese' if new_state else 'spente'}"
        
        return result
    
    elif tool_name == "set_thermostat":
        temp = args.get("temperature", 20)
        mode = args.get("mode", "auto")
        zone = args.get("zone", "Casa")
        
        return {
            "status": "success",
            "zone": zone,
            "target_temperature": temp,
            "current_temperature": round(temp + random.uniform(-2, 2), 1),
            "mode": mode,
            "humidity": random.randint(40, 60),
            "estimated_time_to_target": f"{random.randint(5, 30)} minuti" if abs(temp - 20) > 2 else "Già a temperatura",
            "message": f"Termostato impostato a {temp}°C in modalità {mode}"
        }
    
    elif tool_name == "get_home_status":
        include_energy = args.get("include_energy", True)
        
        devices = []
        for room, device_list in DEVICES_PER_ROOM.items():
            for device in device_list:
                devices.append({
                    "room": room,
                    "device": device,
                    "status": random.choice(["online", "online", "online", "offline"]),
                    "state": random.choice(["on", "off", "standby"])
                })
        
        result = {
            "total_devices": len(devices),
            "devices_online": sum(1 for d in devices if d["status"] == "online"),
            "devices_offline": sum(1 for d in devices if d["status"] == "offline"),
            "thermostat": {
                "current_temp": round(random.uniform(18, 24), 1),
                "target_temp": random.choice([20, 21, 22]),
                "mode": random.choice(["heat", "cool", "auto"])
            },
            "security": {
                "alarm_status": random.choice(["disarmed", "armed_home", "armed_away"]),
                "doors_locked": random.randint(2, 3),
                "doors_unlocked": random.randint(0, 1)
            },
            "devices": devices[:10]  # First 10 devices
        }
        
        if include_energy:
            result["energy"] = {
                "today_kwh": round(random.uniform(5, 25), 2),
                "month_kwh": round(random.uniform(150, 400), 2),
                "current_power_w": random.randint(200, 2000),
                "estimated_monthly_cost": f"€{random.randint(50, 150)}"
            }
        
        return result
    
    elif tool_name == "control_door_lock":
        door = args.get("door", "front")
        action = args.get("action", "lock")
        
        door_names = {
            "front": "Porta principale",
            "back": "Porta posteriore",
            "garage": "Garage"
        }
        
        return {
            "status": "success",
            "door": door_names.get(door, door),
            "action": action,
            "new_state": "bloccata" if action == "lock" else "sbloccata",
            "timestamp": datetime.now().isoformat(),
            "message": f"{door_names.get(door, door)} {'bloccata' if action == 'lock' else 'sbloccata'}"
        }
    
    elif tool_name == "get_security_camera_feed":
        camera = args.get("camera", "ingresso")
        action = args.get("action", "status")
        
        result = {
            "camera": camera,
            "status": "online",
            "recording": random.choice([True, True, True, False]),
            "motion_detected": random.random() > 0.7,
            "last_motion": (datetime.now() - timedelta(minutes=random.randint(5, 120))).isoformat()
        }
        
        if action == "snapshot":
            result["snapshot_url"] = f"https://cameras.home/snapshot/{camera}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            result["message"] = "Snapshot acquisito"
        elif action == "recording":
            result["recording_url"] = f"https://cameras.home/recording/{camera}/live"
            result["message"] = "Streaming attivo"
        
        return result
    
    elif tool_name == "control_blinds":
        room = args.get("room", "Soggiorno")
        position = args.get("position", 50)
        action = args.get("action", "set_position")
        
        if action == "open":
            position = 100
        elif action == "close":
            position = 0
        
        return {
            "status": "success",
            "room": room,
            "position": position,
            "state": "aperte" if position > 70 else "chiuse" if position < 30 else "parzialmente aperte",
            "message": f"Tapparelle {room}: {'aperte' if position > 70 else 'chiuse' if position < 30 else f'al {position}%'}"
        }
    
    elif tool_name == "play_music":
        action = args.get("action", "play")
        query = args.get("query", "")
        speaker = args.get("speaker", "Soggiorno")
        volume = args.get("volume")
        
        result = {
            "status": "success",
            "speaker": speaker,
            "action": action
        }
        
        if action == "play" and query:
            result["now_playing"] = {
                "title": query if query else random.choice(["Blinding Lights", "Shape of You", "Bella Ciao", "Perfect"]),
                "artist": random.choice(["The Weeknd", "Ed Sheeran", "Måneskin", "Coldplay"]),
                "album": "Top Hits",
                "duration": f"{random.randint(2, 4)}:{random.randint(10, 59):02d}"
            }
            result["message"] = f"In riproduzione: {result['now_playing']['title']}"
        elif action == "volume" and volume is not None:
            result["volume"] = volume
            result["message"] = f"Volume impostato a {volume}%"
        else:
            result["message"] = f"Riproduzione {'in pausa' if action == 'pause' else 'fermata' if action == 'stop' else 'avviata'}"
        
        return result
    
    elif tool_name == "set_alarm_system":
        action = args.get("action", "disarm")
        
        status_messages = {
            "arm_away": "Allarme attivato (modalità assente)",
            "arm_home": "Allarme attivato (modalità notte)",
            "disarm": "Allarme disattivato"
        }
        
        return {
            "status": "success",
            "alarm_state": action.replace("_", " ").title(),
            "armed_zones": ["Perimetro", "Sensori movimento", "Telecamere"] if "arm" in action else [],
            "timestamp": datetime.now().isoformat(),
            "message": status_messages.get(action, "Stato allarme aggiornato")
        }
    
    return {"error": f"Unknown smart home tool: {tool_name}"}
