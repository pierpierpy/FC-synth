"""Travel and transportation mock tools."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible, safe_int

TRAVEL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for available flights between two cities",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin airport code or city"},
                    "destination": {"type": "string", "description": "Destination airport code or city"},
                    "departure_date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                    "return_date": {"type": "string", "description": "Return date for round trip"},
                    "passengers": {"type": "integer", "default": 1},
                    "class": {"type": "string", "enum": ["economy", "business", "first"], "default": "economy"}
                },
                "required": ["origin", "destination", "departure_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Search for available hotels in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "check_out": {"type": "string", "description": "Check-out date"},
                    "guests": {"type": "integer", "default": 2},
                    "rooms": {"type": "integer", "default": 1},
                    "min_stars": {"type": "integer", "description": "Minimum hotel stars (1-5)"}
                },
                "required": ["location", "check_in", "check_out"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_trains",
            "description": "Search for train connections",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_station": {"type": "string"},
                    "to_station": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string", "description": "Preferred departure time (HH:MM)"},
                    "passengers": {"type": "integer", "default": 1}
                },
                "required": ["from_station", "to_station", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_taxi",
            "description": "Book a taxi or ride",
            "parameters": {
                "type": "object",
                "properties": {
                    "pickup_location": {"type": "string"},
                    "destination": {"type": "string"},
                    "pickup_time": {"type": "string", "description": "Pickup time (ISO format) or 'now'"},
                    "vehicle_type": {"type": "string", "enum": ["standard", "premium", "xl", "eco"], "default": "standard"}
                },
                "required": ["pickup_location", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_directions",
            "description": "Get directions and route information between two points",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "mode": {"type": "string", "enum": ["driving", "walking", "transit", "cycling"], "default": "driving"},
                    "avoid": {"type": "array", "items": {"type": "string"}, "description": "Avoid tolls, highways, ferries"}
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_traffic_info",
            "description": "Get current traffic conditions for a route or area",
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {"type": "string", "description": "Route or highway name"},
                    "area": {"type": "string", "description": "City or region"}
                },
                "required": []
            }
        }
    },
]

# Mock data
AIRLINES = ["Alitalia/ITA", "Ryanair", "EasyJet", "Lufthansa", "Air France", "Vueling", "Emirates", "British Airways"]
AIRPORTS = {
    "Milano": "MXP", "Roma": "FCO", "Napoli": "NAP", "Venezia": "VCE", "Firenze": "FLR",
    "London": "LHR", "Paris": "CDG", "Amsterdam": "AMS", "Frankfurt": "FRA", "Madrid": "MAD"
}

HOTELS = [
    "Grand Hotel", "Hotel Centrale", "Boutique Inn", "City Suites", "Palace Hotel",
    "NH Collection", "Hilton", "Marriott", "Best Western", "Holiday Inn"
]

TRAIN_TYPES = ["Frecciarossa", "Frecciargento", "Italo", "Regionale Veloce", "Intercity"]


def execute_travel_tool(tool_name: str, args: dict) -> dict:
    """Execute travel mock tool."""
    
    if tool_name == "search_flights":
        origin = args.get("origin", "Milano")
        destination = args.get("destination", "Roma")
        departure_str = args.get("departure_date", datetime.now().strftime("%Y-%m-%d"))
        departure = parse_date_flexible(departure_str).strftime("%Y-%m-%d")
        flight_class = args.get("class", "economy")
        
        origin_code = AIRPORTS.get(origin, origin[:3].upper())
        dest_code = AIRPORTS.get(destination, destination[:3].upper())
        
        flights = []
        for i in range(random.randint(3, 6)):
            dep_hour = random.randint(6, 20)
            duration = random.randint(60, 180)
            base_price = random.randint(50, 300)
            
            if flight_class == "business":
                base_price *= 2.5
            elif flight_class == "first":
                base_price *= 4
            
            flights.append({
                "flight_number": f"{random.choice(['AZ', 'FR', 'U2', 'LH', 'AF'])}{random.randint(100, 999)}",
                "airline": random.choice(AIRLINES),
                "origin": origin_code,
                "destination": dest_code,
                "departure": f"{departure}T{dep_hour:02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "arrival": f"{departure}T{(dep_hour + duration // 60) % 24:02d}:{(duration % 60):02d}:00",
                "duration_minutes": duration,
                "stops": random.choice([0, 0, 0, 1]),
                "price": round(base_price, 2),
                "currency": "EUR",
                "class": flight_class,
                "seats_available": random.randint(1, 20)
            })
        
        flights.sort(key=lambda x: x["price"])
        
        return {
            "origin": origin,
            "destination": destination,
            "date": departure,
            "flights": flights,
            "total_found": len(flights)
        }
    
    elif tool_name == "search_hotels":
        location = args.get("location", "Milano")
        check_in = args.get("check_in")
        check_out = args.get("check_out")
        min_stars = args.get("min_stars", 1)
        
        hotels = []
        for i in range(random.randint(4, 8)):
            stars = random.randint(max(min_stars, 2), 5)
            price = 50 + (stars * 30) + random.randint(-20, 50)
            
            hotels.append({
                "id": f"hotel_{random.randint(10000, 99999)}",
                "name": f"{random.choice(HOTELS)} {location}",
                "stars": stars,
                "rating": round(random.uniform(3.5, 4.9), 1),
                "reviews_count": random.randint(50, 2000),
                "price_per_night": price,
                "currency": "EUR",
                "address": f"Via {random.choice(['Roma', 'Milano', 'Garibaldi', 'Nazionale'])} {random.randint(1, 200)}, {location}",
                "amenities": random.sample(["WiFi", "Colazione", "Parcheggio", "Spa", "Palestra", "Ristorante", "Bar"], random.randint(3, 6)),
                "free_cancellation": random.random() > 0.3
            })
        
        hotels.sort(key=lambda x: x["price_per_night"])
        
        return {
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "hotels": hotels,
            "total_found": len(hotels)
        }
    
    elif tool_name == "search_trains":
        from_station = args.get("from_station", "Milano Centrale")
        to_station = args.get("to_station", "Roma Termini")
        date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        trains = []
        for i in range(random.randint(4, 8)):
            dep_hour = random.randint(6, 21)
            duration = random.randint(60, 240)
            train_type = random.choice(TRAIN_TYPES)
            
            price = 20 if "Regionale" in train_type else random.randint(30, 90)
            
            trains.append({
                "train_number": f"{random.randint(1000, 9999)}",
                "train_type": train_type,
                "operator": "Trenitalia" if "Freccia" in train_type or "Regionale" in train_type else "Italo",
                "departure_station": from_station,
                "arrival_station": to_station,
                "departure_time": f"{date}T{dep_hour:02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "arrival_time": f"{date}T{(dep_hour + duration // 60) % 24:02d}:{(duration % 60):02d}:00",
                "duration_minutes": duration,
                "price": price,
                "currency": "EUR",
                "class_options": ["Standard", "Business"] if "Freccia" in train_type or "Italo" in train_type else ["2a classe"],
                "seats_available": random.randint(5, 50)
            })
        
        trains.sort(key=lambda x: x["departure_time"])
        
        return {
            "from": from_station,
            "to": to_station,
            "date": date,
            "trains": trains,
            "total_found": len(trains)
        }
    
    elif tool_name == "book_taxi":
        pickup = args.get("pickup_location", "")
        destination = args.get("destination", "")
        vehicle = args.get("vehicle_type", "standard")
        
        prices = {"standard": 15, "premium": 25, "xl": 30, "eco": 12}
        base_price = prices.get(vehicle, 15)
        estimated_price = base_price + random.randint(5, 25)
        
        return {
            "status": "confirmed",
            "booking_id": f"TAXI{random.randint(100000, 999999)}",
            "pickup": pickup,
            "destination": destination,
            "vehicle_type": vehicle,
            "estimated_price": estimated_price,
            "currency": "EUR",
            "driver": {
                "name": random.choice(["Marco", "Giuseppe", "Antonio", "Luigi"]),
                "rating": round(random.uniform(4.5, 5.0), 1),
                "vehicle": random.choice(["Toyota Prius", "Fiat 500L", "Mercedes E-Class", "Tesla Model 3"])
            },
            "eta_minutes": random.randint(3, 15),
            "pickup_time": args.get("pickup_time", datetime.now().isoformat())
        }
    
    elif tool_name == "get_directions":
        origin = args.get("origin", "")
        destination = args.get("destination", "")
        mode = args.get("mode", "driving")
        
        # Generate plausible route
        distance = random.randint(2, 50)
        
        speeds = {"driving": 40, "walking": 5, "cycling": 15, "transit": 25}
        speed = speeds.get(mode, 40)
        duration = int((distance / speed) * 60)
        
        steps = [
            f"Parti da {origin}",
            f"Procedi verso {'nord' if random.random() > 0.5 else 'sud'}",
            f"Svolta a {'destra' if random.random() > 0.5 else 'sinistra'} in Via Roma",
            "Continua dritto per 2 km",
            f"Arrivo a {destination}"
        ]
        
        if mode == "transit":
            steps = [
                f"Cammina fino alla fermata/stazione più vicina",
                f"Prendi la {'metro linea ' + random.choice(['M1', 'M2', 'M3']) if random.random() > 0.5 else 'bus ' + str(random.randint(10, 99))}",
                "Scendi dopo 4 fermate",
                f"Cammina per 5 minuti fino a {destination}"
            ]
        
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance_km": distance,
            "duration_minutes": duration,
            "steps": steps,
            "traffic_info": "Traffico moderato" if mode == "driving" else None,
            "toll_cost": random.randint(2, 15) if mode == "driving" and distance > 20 and "tolls" not in args.get("avoid", []) else 0
        }
    
    elif tool_name == "get_traffic_info":
        route = args.get("route", "")
        area = args.get("area", "Milano")
        
        conditions = ["Traffico scorrevole", "Traffico moderato", "Traffico intenso", "Rallentamenti", "Code"]
        incidents = [
            "Incidente segnalato",
            "Lavori in corso",
            "Veicolo fermo",
            "Nessun incidente segnalato"
        ]
        
        return {
            "area": area,
            "route": route if route else f"Tangenziale {area}",
            "overall_condition": random.choice(conditions),
            "congestion_level": random.randint(1, 10),
            "average_speed_kmh": random.randint(15, 80),
            "incidents": [random.choice(incidents)],
            "delay_minutes": random.randint(0, 30),
            "updated_at": datetime.now().isoformat(),
            "peak_hours": "07:30-09:30, 17:30-19:30"
        }
    
    return {"error": f"Unknown travel tool: {tool_name}"}
