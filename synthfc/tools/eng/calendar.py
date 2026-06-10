"""Calendar and scheduling mock tools."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible, safe_int

CALENDAR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Get calendar events for a specific date range",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "calendar_id": {"type": "string", "default": "primary"}
                },
                "required": ["start_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a new calendar event or appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "start_time": {"type": "string", "description": "Start datetime (ISO format)"},
                    "end_time": {"type": "string", "description": "End datetime (ISO format)"},
                    "location": {"type": "string"},
                    "description": {"type": "string"},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of email addresses"},
                    "reminder_minutes": {"type": "integer", "default": 30}
                },
                "required": ["title", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_calendar_event",
            "description": "Delete a calendar event by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event identifier"}
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_calendar_event",
            "description": "Update an existing calendar event",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "title": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "location": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_free_slots",
            "description": "Find available time slots for scheduling",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date to check (YYYY-MM-DD)"},
                    "duration_minutes": {"type": "integer", "description": "Required duration in minutes"},
                    "working_hours_only": {"type": "boolean", "default": True}
                },
                "required": ["date", "duration_minutes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder for a specific time",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Reminder text"},
                    "datetime": {"type": "string", "description": "When to remind (ISO format)"},
                    "repeat": {"type": "string", "enum": ["none", "daily", "weekly", "monthly"], "default": "none"}
                },
                "required": ["message", "datetime"]
            }
        }
    },
]

# Mock data
EVENT_TITLES = [
    "Meeting con il team", "Call con cliente", "Standup giornaliero",
    "Review progetto", "Training", "Pranzo di lavoro",
    "Presentazione Q4", "1:1 con manager", "Workshop",
    "Brainstorming", "Demo prodotto", "Planning sprint"
]

LOCATIONS = [
    "Sala Riunioni A", "Sala Conferenze", "Online - Teams",
    "Online - Zoom", "Ufficio Milano", "Sede Roma", "Cafeteria"
]


def execute_calendar_tool(tool_name: str, args: dict) -> dict:
    """Execute calendar mock tool."""
    
    if tool_name == "get_calendar_events":
        start_date_str = args.get("start_date", datetime.now().strftime("%Y-%m-%d"))
        end_date_str = args.get("end_date", start_date_str)
        
        # Generate 0-5 random events
        num_events = random.randint(0, 5)
        events = []
        
        base_date = parse_date_flexible(start_date_str)
        start_date = base_date.strftime("%Y-%m-%d")
        end_date = parse_date_flexible(end_date_str).strftime("%Y-%m-%d")
        for i in range(num_events):
            event_date = base_date + timedelta(days=random.randint(0, 3))
            start_hour = random.randint(9, 16)
            duration = random.choice([30, 60, 90, 120])
            
            events.append({
                "id": f"evt_{random.randint(10000, 99999)}",
                "title": random.choice(EVENT_TITLES),
                "start": event_date.replace(hour=start_hour, minute=random.choice([0, 30])).isoformat(),
                "end": event_date.replace(hour=start_hour + duration // 60, minute=(duration % 60)).isoformat(),
                "location": random.choice(LOCATIONS),
                "status": "confirmed",
                "attendees": random.randint(1, 8)
            })
        
        # Sort by start time
        events.sort(key=lambda x: x["start"])
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "events": events,
            "total": len(events)
        }
    
    elif tool_name == "create_calendar_event":
        event_id = f"evt_{random.randint(10000, 99999)}"
        return {
            "status": "created",
            "event": {
                "id": event_id,
                "title": args.get("title"),
                "start": args.get("start_time"),
                "end": args.get("end_time"),
                "location": args.get("location", ""),
                "description": args.get("description", ""),
                "attendees": args.get("attendees", []),
                "reminder_minutes": args.get("reminder_minutes", 30),
                "created_at": datetime.now().isoformat()
            },
            "calendar_link": f"https://calendar.example.com/event/{event_id}"
        }
    
    elif tool_name == "delete_calendar_event":
        event_id = args.get("event_id")
        return {
            "status": "deleted",
            "event_id": event_id,
            "message": f"L'evento {event_id} è stato eliminato con successo",
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "update_calendar_event":
        event_id = args.get("event_id")
        updated_fields = [k for k in ["title", "start_time", "end_time", "location", "description"] if args.get(k)]
        return {
            "status": "updated",
            "event_id": event_id,
            "updated_fields": updated_fields,
            "message": f"Evento aggiornato: {', '.join(updated_fields)}",
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "find_free_slots":
        date_str = args.get("date", datetime.now().strftime("%Y-%m-%d"))
        duration = safe_int(args.get("duration_minutes", 60), 60)
        working_hours = args.get("working_hours_only", True)
        
        base = parse_date_flexible(date_str)
        date = base.strftime("%Y-%m-%d")
        start_hour = 9 if working_hours else 8
        end_hour = 18 if working_hours else 22
        
        # Generate 2-5 available slots
        slots = []
        current_hour = start_hour
        
        while current_hour < end_hour - duration // 60:
            if random.random() > 0.4:  # 60% chance of slot being free
                slot_start = base.replace(hour=current_hour, minute=random.choice([0, 30]))
                slots.append({
                    "start": slot_start.isoformat(),
                    "end": (slot_start + timedelta(minutes=duration)).isoformat(),
                    "duration_minutes": duration
                })
            current_hour += random.randint(1, 2)
        
        return {
            "date": date,
            "duration_requested": duration,
            "available_slots": slots[:5],  # Max 5 slots
            "total_slots": len(slots[:5])
        }
    
    elif tool_name == "set_reminder":
        reminder_id = f"rem_{random.randint(10000, 99999)}"
        return {
            "status": "created",
            "reminder": {
                "id": reminder_id,
                "message": args.get("message"),
                "datetime": args.get("datetime"),
                "repeat": args.get("repeat", "none"),
                "created_at": datetime.now().isoformat()
            },
            "message": f"Promemoria impostato per {args.get('datetime')}"
        }
    
    return {"error": f"Unknown calendar tool: {tool_name}"}
