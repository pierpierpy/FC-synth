"""Productivity and task management mock tools."""

import random
from datetime import datetime, timedelta

PRODUCTIVITY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task or to-do item",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "project": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Retrieve tasks filtered by various criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "all"], "default": "pending"},
                    "project": {"type": "string"},
                    "due_before": {"type": "string"},
                    "priority": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Create a new note or document",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "folder": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Search through saved notes",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "folder": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Set a countdown timer",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration_minutes": {"type": "integer"},
                    "label": {"type": "string"},
                    "alert_sound": {"type": "boolean", "default": True}
                },
                "required": ["duration_minutes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_stopwatch",
            "description": "Start a stopwatch for time tracking",
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "description": "What you're timing"},
                    "project": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_text",
            "description": "Translate text between languages",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "source_language": {"type": "string", "description": "Source language code (auto-detect if not specified)"},
                    "target_language": {"type": "string", "description": "Target language code"}
                },
                "required": ["text", "target_language"]
            }
        }
    },
]

# Mock data
TASK_TITLES = [
    "Completare report mensile",
    "Chiamare cliente",
    "Aggiornare documentazione",
    "Preparare presentazione",
    "Review codice",
    "Rispondere alle email",
    "Pianificare sprint",
    "Testare nuova funzionalità",
    "Meeting con stakeholders",
    "Formazione team"
]

PROJECTS = ["Progetto Alpha", "Marketing Q4", "Sviluppo App", "Migrazione Cloud", "Redesign Sito"]

NOTE_TITLES = [
    "Appunti riunione",
    "Idee brainstorming",
    "Note tecniche",
    "Lista contatti",
    "Procedure operative"
]


def execute_productivity_tool(tool_name: str, args: dict) -> dict:
    """Execute productivity mock tool."""
    
    if tool_name == "create_task":
        task_id = f"task_{random.randint(10000, 99999)}"
        return {
            "status": "created",
            "task": {
                "id": task_id,
                "title": args.get("title"),
                "description": args.get("description", ""),
                "due_date": args.get("due_date"),
                "priority": args.get("priority", "medium"),
                "project": args.get("project"),
                "tags": args.get("tags", []),
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
        }
    
    elif tool_name == "get_tasks":
        status_filter = args.get("status", "pending")
        
        tasks = []
        num_tasks = random.randint(2, 7)
        
        for i in range(num_tasks):
            task_status = status_filter if status_filter != "all" else random.choice(["pending", "in_progress", "completed"])
            due = (datetime.now() + timedelta(days=random.randint(-2, 14))).strftime("%Y-%m-%d")
            
            tasks.append({
                "id": f"task_{random.randint(10000, 99999)}",
                "title": random.choice(TASK_TITLES),
                "due_date": due,
                "priority": random.choice(["low", "medium", "high", "urgent"]),
                "project": random.choice(PROJECTS + [None]),
                "status": task_status,
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })
        
        # Sort by due date
        tasks.sort(key=lambda x: x["due_date"])
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "filters": {"status": status_filter, "project": args.get("project")}
        }
    
    elif tool_name == "complete_task":
        task_id = args.get("task_id")
        return {
            "status": "completed",
            "task_id": task_id,
            "completed_at": datetime.now().isoformat(),
            "message": f"Task {task_id} completato con successo!"
        }
    
    elif tool_name == "create_note":
        note_id = f"note_{random.randint(10000, 99999)}"
        return {
            "status": "created",
            "note": {
                "id": note_id,
                "title": args.get("title"),
                "content_preview": args.get("content", "")[:100] + "..." if len(args.get("content", "")) > 100 else args.get("content", ""),
                "folder": args.get("folder", "Default"),
                "tags": args.get("tags", []),
                "word_count": len(args.get("content", "").split()),
                "created_at": datetime.now().isoformat()
            }
        }
    
    elif tool_name == "search_notes":
        query = args.get("query", "")
        limit = args.get("limit", 10)
        
        notes = []
        for i in range(min(limit, random.randint(1, 5))):
            notes.append({
                "id": f"note_{random.randint(10000, 99999)}",
                "title": f"{random.choice(NOTE_TITLES)} - {query}",
                "preview": f"...contenuto relativo a {query}...",
                "folder": random.choice(["Lavoro", "Personale", "Progetti", "Archivio"]),
                "updated_at": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                "relevance_score": round(random.uniform(0.7, 1.0), 2)
            })
        
        return {
            "query": query,
            "notes": notes,
            "total": len(notes)
        }
    
    elif tool_name == "set_timer":
        timer_id = f"timer_{random.randint(1000, 9999)}"
        duration = args.get("duration_minutes", 25)
        end_time = datetime.now() + timedelta(minutes=duration)
        
        return {
            "status": "started",
            "timer": {
                "id": timer_id,
                "duration_minutes": duration,
                "label": args.get("label", "Timer"),
                "ends_at": end_time.isoformat(),
                "alert_sound": args.get("alert_sound", True)
            },
            "message": f"Timer di {duration} minuti avviato. Termina alle {end_time.strftime('%H:%M')}"
        }
    
    elif tool_name == "start_stopwatch":
        sw_id = f"sw_{random.randint(1000, 9999)}"
        return {
            "status": "running",
            "stopwatch": {
                "id": sw_id,
                "label": args.get("label", "Cronometro"),
                "project": args.get("project"),
                "started_at": datetime.now().isoformat(),
                "elapsed": "00:00:00"
            },
            "message": "Cronometro avviato"
        }
    
    elif tool_name == "translate_text":
        text = args.get("text", "")
        source = args.get("source_language", "auto")
        target = args.get("target_language", "en")
        
        # Fake translations
        translations = {
            "it": {
                "Hello": "Ciao",
                "Thank you": "Grazie",
                "How are you?": "Come stai?",
            },
            "en": {
                "Ciao": "Hello",
                "Grazie": "Thank you",
                "Come stai?": "How are you?",
            }
        }
        
        # Generate a plausible "translation"
        if text in translations.get(target, {}):
            translated = translations[target][text]
        else:
            translated = f"[Traduzione in {target}]: {text}"
        
        return {
            "source_text": text,
            "translated_text": translated,
            "source_language": source if source != "auto" else "it" if any(c in text for c in "àèìòù") else "en",
            "target_language": target,
            "confidence": round(random.uniform(0.85, 0.99), 2)
        }
    
    return {"error": f"Unknown productivity tool: {tool_name}"}
