"""Communication mock tools (email, messaging, calls)."""

import random
from datetime import datetime, timedelta

COMMUNICATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to one or more recipients",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "array", "items": {"type": "string"}, "description": "List of recipient email addresses"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "cc": {"type": "array", "items": {"type": "string"}},
                    "attachments": {"type": "array", "items": {"type": "string"}, "description": "File paths to attach"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_emails",
            "description": "Retrieve emails from inbox or specific folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "enum": ["inbox", "sent", "drafts", "spam", "trash"], "default": "inbox"},
                    "unread_only": {"type": "boolean", "default": False},
                    "limit": {"type": "integer", "default": 10},
                    "search_query": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_sms",
            "description": "Send an SMS text message",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {"type": "string", "description": "Recipient phone number"},
                    "message": {"type": "string", "description": "Message text (max 160 chars)"}
                },
                "required": ["phone_number", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp_message",
            "description": "Send a WhatsApp message to a contact",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "Contact name or phone number"},
                    "message": {"type": "string"}
                },
                "required": ["contact", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_phone_call",
            "description": "Initiate a phone call",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {"type": "string"},
                    "contact_name": {"type": "string"}
                },
                "required": ["phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_contacts",
            "description": "Search and retrieve contacts from address book",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search by name, email, or phone"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule a video/audio meeting and send invites",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "participants": {"type": "array", "items": {"type": "string"}},
                    "datetime": {"type": "string", "description": "Meeting start time (ISO format)"},
                    "duration_minutes": {"type": "integer", "default": 60},
                    "platform": {"type": "string", "enum": ["teams", "zoom", "meet", "webex"], "default": "teams"},
                    "agenda": {"type": "string"}
                },
                "required": ["title", "participants", "datetime"]
            }
        }
    },
]

# Mock data
SENDERS = [
    ("Mario Rossi", "mario.rossi@example.com"),
    ("Laura Bianchi", "laura.bianchi@company.it"),
    ("Giuseppe Verdi", "g.verdi@email.com"),
    ("HR Department", "hr@company.it"),
    ("Newsletter", "newsletter@service.com"),
    ("Amazon", "noreply@amazon.it"),
    ("LinkedIn", "notifications@linkedin.com"),
    ("Google", "no-reply@google.com"),
]

EMAIL_SUBJECTS = [
    "Re: Progetto Q4 - Aggiornamento",
    "Meeting domani alle 15:00",
    "Fattura n. {num}",
    "Conferma prenotazione",
    "Documento da firmare",
    "Reminder: scadenza venerdì",
    "Nuova proposta commerciale",
    "Benvenuto nel team!",
    "Report settimanale",
    "Richiesta informazioni"
]

CONTACTS = [
    {"name": "Mario Rossi", "phone": "+39 333 1234567", "email": "mario.rossi@example.com"},
    {"name": "Laura Bianchi", "phone": "+39 339 7654321", "email": "laura.bianchi@company.it"},
    {"name": "Giuseppe Verdi", "phone": "+39 320 1112233", "email": "g.verdi@email.com"},
    {"name": "Anna Ferrari", "phone": "+39 347 9998877", "email": "anna.ferrari@mail.it"},
    {"name": "Marco Colombo", "phone": "+39 335 5556666", "email": "m.colombo@work.com"},
    {"name": "Giulia Romano", "phone": "+39 328 4443322", "email": "giulia.romano@email.it"},
    {"name": "Luca Esposito", "phone": "+39 366 2221100", "email": "luca.esposito@azienda.it"},
    {"name": "Sofia Marino", "phone": "+39 340 8887766", "email": "sofia.marino@company.com"},
]


def execute_communication_tool(tool_name: str, args: dict) -> dict:
    """Execute communication mock tool."""
    
    if tool_name == "send_email":
        email_id = f"msg_{random.randint(100000, 999999)}"
        return {
            "status": "sent",
            "message_id": email_id,
            "to": args.get("to", []),
            "cc": args.get("cc", []),
            "subject": args.get("subject"),
            "timestamp": datetime.now().isoformat(),
            "attachments_count": len(args.get("attachments", [])),
            "message": "Email inviata con successo"
        }
    
    elif tool_name == "get_emails":
        folder = args.get("folder", "inbox")
        unread_only = args.get("unread_only", False)
        limit = args.get("limit", 10)
        search = args.get("search_query", "")
        
        emails = []
        for i in range(min(limit, random.randint(3, 10))):
            sender_name, sender_email = random.choice(SENDERS)
            is_unread = random.random() > 0.6
            
            if unread_only and not is_unread:
                continue
                
            emails.append({
                "id": f"msg_{random.randint(100000, 999999)}",
                "from": {"name": sender_name, "email": sender_email},
                "subject": random.choice(EMAIL_SUBJECTS).format(num=random.randint(1000, 9999)),
                "preview": "Buongiorno, ti scrivo per informarti che...",
                "date": (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
                "is_read": not is_unread,
                "has_attachments": random.random() > 0.7,
                "is_starred": random.random() > 0.8
            })
        
        return {
            "folder": folder,
            "emails": emails,
            "total": len(emails),
            "unread_count": sum(1 for e in emails if not e["is_read"])
        }
    
    elif tool_name == "send_sms":
        return {
            "status": "delivered",
            "message_id": f"sms_{random.randint(100000, 999999)}",
            "to": args.get("phone_number"),
            "message_length": len(args.get("message", "")),
            "segments": 1 if len(args.get("message", "")) <= 160 else (len(args.get("message", "")) // 160) + 1,
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "send_whatsapp_message":
        return {
            "status": "sent",
            "message_id": f"wa_{random.randint(100000, 999999)}",
            "to": args.get("contact"),
            "delivered": True,
            "read": False,
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "make_phone_call":
        return {
            "status": "calling",
            "call_id": f"call_{random.randint(100000, 999999)}",
            "to": args.get("phone_number"),
            "contact_name": args.get("contact_name", "Sconosciuto"),
            "started_at": datetime.now().isoformat(),
            "message": "Chiamata in corso..."
        }
    
    elif tool_name == "get_contacts":
        query = args.get("query", "").lower()
        limit = args.get("limit", 10)
        
        if query:
            matches = [c for c in CONTACTS if query in c["name"].lower() or query in c.get("email", "").lower()]
        else:
            matches = CONTACTS
        
        return {
            "contacts": matches[:limit],
            "total": len(matches[:limit]),
            "query": query
        }
    
    elif tool_name == "schedule_meeting":
        meeting_id = f"meet_{random.randint(100000, 999999)}"
        platform = args.get("platform", "teams")
        
        platform_urls = {
            "teams": f"https://teams.microsoft.com/l/meetup/{meeting_id}",
            "zoom": f"https://zoom.us/j/{random.randint(10000000000, 99999999999)}",
            "meet": f"https://meet.google.com/{meeting_id[:3]}-{meeting_id[3:7]}-{meeting_id[7:]}",
            "webex": f"https://webex.com/meet/{meeting_id}"
        }
        
        return {
            "status": "scheduled",
            "meeting_id": meeting_id,
            "title": args.get("title"),
            "datetime": args.get("datetime"),
            "duration_minutes": args.get("duration_minutes", 60),
            "participants": args.get("participants", []),
            "platform": platform,
            "join_url": platform_urls.get(platform, platform_urls["teams"]),
            "invites_sent": len(args.get("participants", [])),
            "message": f"Meeting creato. Inviti inviati a {len(args.get('participants', []))} partecipanti."
        }
    
    return {"error": f"Unknown communication tool: {tool_name}"}
