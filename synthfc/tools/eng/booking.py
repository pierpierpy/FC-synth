"""Booking and reservation mock tools (restaurants, events, services)."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible, safe_int

BOOKING_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_restaurant",
            "description": "Make a restaurant reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {"type": "string"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in HH:MM format"},
                    "party_size": {"type": "integer"},
                    "special_requests": {"type": "string"},
                    "outdoor_seating": {"type": "boolean", "default": False}
                },
                "required": ["restaurant_name", "date", "time", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Search for restaurants by criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "cuisine": {"type": "string", "enum": ["italiana", "giapponese", "cinese", "messicana", "americana", "indiana", "francese", "fusion", "pizzeria", "seafood"]},
                    "price_range": {"type": "string", "enum": ["$", "$$", "$$$", "$$$$"]},
                    "rating_min": {"type": "number", "minimum": 1, "maximum": 5},
                    "open_now": {"type": "boolean"},
                    "features": {"type": "array", "items": {"type": "string", "enum": ["outdoor", "wifi", "parking", "vegetarian", "vegan", "gluten_free", "delivery"]}}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_event_tickets",
            "description": "Book tickets for concerts, shows, sports events",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_name": {"type": "string"},
                    "date": {"type": "string"},
                    "venue": {"type": "string"},
                    "ticket_type": {"type": "string", "enum": ["standard", "vip", "premium", "gold", "platinum"]},
                    "quantity": {"type": "integer"},
                    "seat_preference": {"type": "string", "enum": ["any", "front", "middle", "back", "aisle"]}
                },
                "required": ["event_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": "Search for upcoming events",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "category": {"type": "string", "enum": ["concerts", "theater", "sports", "comedy", "festivals", "exhibitions", "conferences"]},
                    "date_from": {"type": "string"},
                    "date_to": {"type": "string"},
                    "artist_team": {"type": "string"},
                    "max_price": {"type": "number"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment (doctor, dentist, salon, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_type": {"type": "string", "enum": ["doctor", "dentist", "hair_salon", "spa", "mechanic", "veterinarian", "lawyer", "accountant"]},
                    "provider_name": {"type": "string"},
                    "date": {"type": "string"},
                    "preferred_time": {"type": "string", "enum": ["morning", "afternoon", "evening", "any"]},
                    "service_details": {"type": "string"},
                    "is_first_visit": {"type": "boolean", "default": False}
                },
                "required": ["service_type", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_availability",
            "description": "Check availability for a service or venue",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_id": {"type": "string"},
                    "date": {"type": "string"},
                    "duration_minutes": {"type": "integer"},
                    "party_size": {"type": "integer", "default": 1}
                },
                "required": ["service_id", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Cancel an existing booking",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string"},
                    "reason": {"type": "string"},
                    "request_refund": {"type": "boolean", "default": True}
                },
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_booking",
            "description": "Modify an existing booking",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string"},
                    "new_date": {"type": "string"},
                    "new_time": {"type": "string"},
                    "new_party_size": {"type": "integer"},
                    "additional_notes": {"type": "string"}
                },
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_booking_history",
            "description": "Get user's booking history",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["restaurants", "events", "appointments", "all"]},
                    "status": {"type": "string", "enum": ["upcoming", "past", "cancelled", "all"]},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
]

# Mock data
RESTAURANTS_IT = [
    {"name": "Trattoria da Mario", "cuisine": "italiana", "price": "$$", "rating": 4.5},
    {"name": "Osteria del Borgo", "cuisine": "italiana", "price": "$$$", "rating": 4.7},
    {"name": "Pizzeria Napoli", "cuisine": "pizzeria", "price": "$", "rating": 4.3},
    {"name": "Sakura Sushi", "cuisine": "giapponese", "price": "$$$", "rating": 4.6},
    {"name": "La Pergola", "cuisine": "italiana", "price": "$$$$", "rating": 4.9},
    {"name": "Ristorante Milano", "cuisine": "italiana", "price": "$$$", "rating": 4.4},
    {"name": "Dragon Palace", "cuisine": "cinese", "price": "$$", "rating": 4.2},
    {"name": "El Mexicano", "cuisine": "messicana", "price": "$$", "rating": 4.1},
]

EVENTS_MOCK = [
    {"name": "Concerto Coldplay", "category": "concerts", "venue": "San Siro", "price_from": 80},
    {"name": "Hamilton - Il Musical", "category": "theater", "venue": "Teatro Arcimboldi", "price_from": 60},
    {"name": "Inter vs Juventus", "category": "sports", "venue": "San Siro", "price_from": 45},
    {"name": "Zelig Live", "category": "comedy", "venue": "Teatro degli Arcimboldi", "price_from": 35},
    {"name": "Mostra Picasso", "category": "exhibitions", "venue": "Palazzo Reale", "price_from": 15},
]

PROVIDERS = {
    "doctor": ["Dr. Rossi", "Dr. Bianchi", "Dr. Verdi", "Dott.ssa Ferrari"],
    "dentist": ["Studio Dentistico Sorridenti", "Dental Clinic Milano", "Dr. Denti"],
    "hair_salon": ["Salon Glamour", "Hair Studio Milano", "BeautyHair", "Toni&Guy"],
    "spa": ["Spa Relax", "Wellness Center", "Oasi del Benessere"],
}


def execute_booking_tool(tool_name: str, args: dict) -> dict:
    """Execute booking mock tool."""
    
    if tool_name == "book_restaurant":
        booking_id = f"RST{random.randint(100000, 999999)}"
        
        return {
            "status": "confirmed",
            "booking": {
                "id": booking_id,
                "restaurant": args.get("restaurant_name"),
                "date": args.get("date"),
                "time": args.get("time"),
                "party_size": args.get("party_size"),
                "outdoor_seating": args.get("outdoor_seating", False),
                "special_requests": args.get("special_requests"),
                "table_number": random.randint(1, 30),
                "confirmation_code": f"CONF{random.randint(1000, 9999)}"
            },
            "restaurant_details": {
                "address": f"Via {random.choice(['Roma', 'Milano', 'Garibaldi', 'Dante'])}, {random.randint(1, 100)}",
                "phone": f"+39 02 {random.randint(1000000, 9999999)}",
                "notes": "Prenotazione confermata. Vi aspettiamo!"
            },
            "cancellation_policy": "Cancellazione gratuita fino a 2 ore prima"
        }
    
    elif tool_name == "search_restaurants":
        location = args.get("location", "Milano")
        cuisine = args.get("cuisine")
        price_range = args.get("price_range")
        
        restaurants = RESTAURANTS_IT.copy()
        if cuisine:
            restaurants = [r for r in restaurants if r["cuisine"] == cuisine]
        if price_range:
            restaurants = [r for r in restaurants if r["price"] == price_range]
        
        results = []
        for r in random.sample(restaurants, min(len(restaurants), random.randint(3, 6))):
            results.append({
                **r,
                "address": f"Via {random.choice(['Roma', 'Milano', 'Garibaldi', 'Dante', 'Torino'])}, {random.randint(1, 150)}, {location}",
                "distance_km": round(random.uniform(0.2, 5), 1),
                "reviews_count": random.randint(50, 2000),
                "open_now": random.choice([True, True, True, False]),
                "next_available": f"{random.randint(12, 21)}:{'00' if random.random() > 0.5 else '30'}",
                "features": random.sample(["outdoor", "wifi", "parking", "vegetarian"], random.randint(1, 3)),
                "popular_dishes": random.sample(["Carbonara", "Margherita", "Tiramisù", "Risotto", "Ossobuco"], 2)
            })
        
        return {
            "location": location,
            "filters_applied": {
                "cuisine": cuisine,
                "price_range": price_range,
                "rating_min": args.get("rating_min")
            },
            "results": results,
            "total_found": len(results)
        }
    
    elif tool_name == "book_event_tickets":
        booking_id = f"EVT{random.randint(100000, 999999)}"
        ticket_type = args.get("ticket_type", "standard")
        quantity = safe_int(args.get("quantity", 1), 1)
        
        prices = {"standard": 45, "vip": 120, "premium": 200, "gold": 80, "platinum": 300}
        unit_price = prices.get(ticket_type, 50)
        
        return {
            "status": "confirmed",
            "booking": {
                "id": booking_id,
                "event": args.get("event_name"),
                "date": args.get("date", (datetime.now() + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d")),
                "venue": args.get("venue", "Venue TBD"),
                "ticket_type": ticket_type,
                "quantity": quantity,
                "seats": [f"Fila {random.choice('ABCDEFGH')} - Posto {random.randint(1, 40)}" for _ in range(quantity)],
                "unit_price": unit_price,
                "total_price": unit_price * quantity,
                "fees": round(unit_price * quantity * 0.1, 2),
                "grand_total": round(unit_price * quantity * 1.1, 2)
            },
            "e_tickets_sent_to": "user@email.com",
            "qr_code_url": f"https://tickets.example.com/qr/{booking_id}",
            "important_info": "Presentarsi 30 minuti prima dell'inizio dell'evento"
        }
    
    elif tool_name == "search_events":
        location = args.get("location", "Milano")
        category = args.get("category")
        
        events = EVENTS_MOCK.copy()
        if category:
            events = [e for e in events if e["category"] == category]
        
        results = []
        for e in random.sample(events, min(len(events), random.randint(3, 5))):
            event_date = datetime.now() + timedelta(days=random.randint(1, 120))
            results.append({
                **e,
                "date": event_date.strftime("%Y-%m-%d"),
                "time": f"{random.randint(18, 21)}:00",
                "tickets_available": random.choice([True, True, True, False]),
                "price_range": f"€{e['price_from']} - €{e['price_from'] * 3}",
                "popularity": random.choice(["Alta richiesta", "Disponibile", "Ultimi posti"]),
                "location": location
            })
        
        return {
            "location": location,
            "category": category,
            "events": results,
            "total_found": len(results)
        }
    
    elif tool_name == "book_appointment":
        service_type = args.get("service_type", "doctor")
        booking_id = f"APT{random.randint(100000, 999999)}"
        
        provider = args.get("provider_name") or random.choice(PROVIDERS.get(service_type, ["Provider"]))
        
        # Generate available time
        base_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "14:00", "14:30", "15:00", "15:30", "16:00"]
        assigned_time = random.choice(base_times) if args.get("preferred_time") != "evening" else random.choice(["17:00", "17:30", "18:00"])
        
        return {
            "status": "confirmed",
            "appointment": {
                "id": booking_id,
                "service_type": service_type,
                "provider": provider,
                "date": args.get("date"),
                "time": assigned_time,
                "duration_minutes": {"doctor": 30, "dentist": 45, "hair_salon": 60, "spa": 90}.get(service_type, 30),
                "is_first_visit": args.get("is_first_visit", False),
                "service_details": args.get("service_details", "Visita standard")
            },
            "location": {
                "address": f"Via {random.choice(['Montenapoleone', 'Manzoni', 'della Spiga'])}, {random.randint(1, 50)}",
                "floor": random.choice(["Piano terra", "1° piano", "2° piano"]),
                "phone": f"+39 02 {random.randint(1000000, 9999999)}"
            },
            "preparation": {
                "doctor": "Portare tessera sanitaria e documenti",
                "dentist": "Non mangiare 2 ore prima",
                "hair_salon": "Arrivare con capelli asciutti",
                "spa": "Arrivare 15 minuti prima per cambiarsi"
            }.get(service_type, "Nessuna preparazione richiesta"),
            "reminder_set": True
        }
    
    elif tool_name == "get_availability":
        service_id = args.get("service_id", "service")
        date_str = args.get("date", datetime.now().strftime("%Y-%m-%d"))
        date = parse_date_flexible(date_str).strftime("%Y-%m-%d")
        date_dt = parse_date_flexible(date_str)
        
        slots = []
        for hour in range(9, 18):
            for minute in [0, 30]:
                if random.random() > 0.4:  # 60% availability
                    slots.append(f"{hour:02d}:{minute:02d}")
        
        return {
            "service_id": service_id,
            "date": date,
            "available_slots": slots,
            "total_available": len(slots),
            "next_available_date": date if slots else (date_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
            "booking_window_days": 30
        }
    
    elif tool_name == "cancel_booking":
        booking_id = args.get("booking_id")
        
        refund_eligible = random.random() > 0.2
        
        return {
            "status": "cancelled",
            "booking_id": booking_id,
            "cancellation_time": datetime.now().isoformat(),
            "reason_provided": args.get("reason"),
            "refund": {
                "eligible": refund_eligible,
                "amount": round(random.uniform(20, 200), 2) if refund_eligible else 0,
                "processing_days": 5 if refund_eligible else None,
                "refund_method": "Stesso metodo di pagamento" if refund_eligible else "Non applicabile"
            },
            "confirmation_sent_to": "user@email.com"
        }
    
    elif tool_name == "modify_booking":
        booking_id = args.get("booking_id")
        
        return {
            "status": "modified",
            "booking_id": booking_id,
            "changes": {
                "new_date": args.get("new_date"),
                "new_time": args.get("new_time"),
                "new_party_size": args.get("new_party_size"),
                "additional_notes": args.get("additional_notes")
            },
            "price_difference": round(random.uniform(-20, 50), 2) if random.random() > 0.5 else 0,
            "updated_at": datetime.now().isoformat(),
            "confirmation_sent": True
        }
    
    elif tool_name == "get_booking_history":
        category = args.get("category", "all")
        status = args.get("status", "all")
        limit = args.get("limit", 10)
        
        bookings = []
        categories = ["restaurants", "events", "appointments"] if category == "all" else [category]
        
        for i in range(min(limit, random.randint(3, 8))):
            cat = random.choice(categories)
            booking_date = datetime.now() + timedelta(days=random.randint(-60, 30))
            is_upcoming = booking_date > datetime.now()
            
            bookings.append({
                "id": f"BKG{random.randint(100000, 999999)}",
                "category": cat,
                "title": {
                    "restaurants": random.choice([r["name"] for r in RESTAURANTS_IT]),
                    "events": random.choice([e["name"] for e in EVENTS_MOCK]),
                    "appointments": f"Appuntamento {random.choice(['medico', 'dentista', 'parrucchiere'])}"
                }[cat],
                "date": booking_date.strftime("%Y-%m-%d"),
                "status": "upcoming" if is_upcoming else random.choice(["completed", "cancelled"]),
                "total_paid": round(random.uniform(20, 300), 2)
            })
        
        return {
            "bookings": bookings,
            "total": len(bookings),
            "filters": {"category": category, "status": status}
        }
    
    return {"error": f"Unknown booking tool: {tool_name}"}
