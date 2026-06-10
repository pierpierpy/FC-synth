"""Media and entertainment mock tools."""

import random
from datetime import datetime, timedelta

MEDIA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_movies",
            "description": "Search for movies by title, genre, or actor",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "genre": {"type": "string", "enum": ["action", "comedy", "drama", "horror", "sci-fi", "romance", "thriller"]},
                    "year": {"type": "integer"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_movie_details",
            "description": "Get detailed information about a movie",
            "parameters": {
                "type": "object",
                "properties": {
                    "movie_id": {"type": "string"},
                    "title": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_streaming_availability",
            "description": "Check which streaming platforms have a movie/show",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "country": {"type": "string", "default": "IT"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tv_schedule",
            "description": "Get TV programming schedule",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                    "prime_time_only": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_podcast_episodes",
            "description": "Get episodes from a podcast",
            "parameters": {
                "type": "object",
                "properties": {
                    "podcast_name": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["podcast_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sports_scores",
            "description": "Get live or recent sports scores",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "enum": ["football", "basketball", "tennis", "f1", "moto_gp"]},
                    "league": {"type": "string"},
                    "team": {"type": "string"}
                },
                "required": ["sport"]
            }
        }
    },
]

# Mock data
MOVIES = [
    {"title": "Oppenheimer", "year": 2023, "director": "Christopher Nolan", "genre": "drama", "rating": 8.5},
    {"title": "Barbie", "year": 2023, "director": "Greta Gerwig", "genre": "comedy", "rating": 7.2},
    {"title": "Dune: Part Two", "year": 2024, "director": "Denis Villeneuve", "genre": "sci-fi", "rating": 8.8},
    {"title": "The Batman", "year": 2022, "director": "Matt Reeves", "genre": "action", "rating": 7.8},
    {"title": "Everything Everywhere All at Once", "year": 2022, "director": "Daniels", "genre": "sci-fi", "rating": 8.0},
    {"title": "Io Capitano", "year": 2023, "director": "Matteo Garrone", "genre": "drama", "rating": 7.8},
    {"title": "C'è ancora domani", "year": 2023, "director": "Paola Cortellesi", "genre": "drama", "rating": 8.3},
]

STREAMING_PLATFORMS = ["Netflix", "Amazon Prime Video", "Disney+", "NOW TV", "Apple TV+", "Paramount+", "RaiPlay"]

TV_CHANNELS = ["Rai 1", "Rai 2", "Rai 3", "Canale 5", "Italia 1", "Rete 4", "La7", "TV8", "NOVE", "Sky Uno"]

SPORTS_TEAMS_FOOTBALL = [
    "Inter", "Milan", "Juventus", "Napoli", "Roma", "Lazio", "Fiorentina", "Atalanta"
]


def execute_media_tool(tool_name: str, args: dict) -> dict:
    """Execute media mock tool."""
    
    if tool_name == "search_movies":
        query = args.get("query", "").lower()
        genre = args.get("genre")
        year = args.get("year")
        limit = args.get("limit", 10)
        
        results = []
        for movie in MOVIES:
            if query and query not in movie["title"].lower():
                continue
            if genre and movie["genre"] != genre:
                continue
            if year and movie["year"] != year:
                continue
            results.append({
                "id": f"movie_{random.randint(10000, 99999)}",
                **movie,
                "poster_url": f"https://posters.example.com/{movie['title'].replace(' ', '_')}.jpg"
            })
        
        # Add generic results if needed
        while len(results) < min(limit, 5):
            results.append({
                "id": f"movie_{random.randint(10000, 99999)}",
                "title": f"{query.title() if query else 'Film'} {random.choice(['Returns', 'Legacy', 'Rising', 'Reborn'])}",
                "year": year or random.randint(2020, 2024),
                "director": random.choice(["Steven Spielberg", "Martin Scorsese", "Quentin Tarantino"]),
                "genre": genre or random.choice(["action", "drama", "comedy"]),
                "rating": round(random.uniform(6.0, 9.0), 1),
                "poster_url": f"https://posters.example.com/generic_{random.randint(1, 1000)}.jpg"
            })
        
        return {
            "query": query,
            "filters": {"genre": genre, "year": year},
            "movies": results[:limit],
            "total_found": len(results)
        }
    
    elif tool_name == "get_movie_details":
        title = args.get("title", "")
        
        # Find movie or generate one
        movie = None
        for m in MOVIES:
            if title.lower() in m["title"].lower():
                movie = m
                break
        
        if not movie:
            movie = {
                "title": title or "Unknown Movie",
                "year": random.randint(2020, 2024),
                "director": "Unknown",
                "genre": "drama",
                "rating": round(random.uniform(6.0, 8.5), 1)
            }
        
        return {
            "id": args.get("movie_id", f"movie_{random.randint(10000, 99999)}"),
            "title": movie["title"],
            "year": movie["year"],
            "director": movie["director"],
            "genre": movie["genre"],
            "rating": movie["rating"],
            "runtime_minutes": random.randint(90, 180),
            "plot": f"Un avvincente {movie['genre']} che racconta una storia emozionante di sfide, trionfi e crescita personale.",
            "cast": random.sample(["Leonardo DiCaprio", "Margot Robbie", "Brad Pitt", "Tom Hanks", "Cate Blanchett", "Tilda Swinton", "Toni Servillo", "Monica Bellucci"], 4),
            "awards": f"{random.randint(0, 5)} nomination Oscar" if random.random() > 0.3 else "Nessuna nomination principale",
            "box_office": f"${random.randint(50, 500)}M",
            "reviews_count": random.randint(100, 5000)
        }
    
    elif tool_name == "get_streaming_availability":
        title = args.get("title", "")
        country = args.get("country", "IT")
        
        # Random availability
        available_on = random.sample(STREAMING_PLATFORMS, random.randint(1, 3))
        
        return {
            "title": title,
            "country": country,
            "available_on": [
                {
                    "platform": platform,
                    "type": random.choice(["subscription", "rent", "buy"]),
                    "quality": random.choice(["HD", "4K", "SD"]),
                    "price": None if random.random() > 0.5 else f"€{random.randint(3, 15)}.99"
                }
                for platform in available_on
            ],
            "not_available_on": [p for p in STREAMING_PLATFORMS if p not in available_on][:3]
        }
    
    elif tool_name == "get_tv_schedule":
        channel = args.get("channel")
        date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
        prime_time = args.get("prime_time_only", False)
        
        channels = [channel] if channel else random.sample(TV_CHANNELS, 3)
        
        schedule = []
        for ch in channels:
            programs = []
            start_hour = 20 if prime_time else 6
            end_hour = 24 if prime_time else 24
            
            current_hour = start_hour
            while current_hour < end_hour:
                duration = random.choice([30, 60, 90, 120])
                programs.append({
                    "time": f"{current_hour:02d}:{random.choice(['00', '30'])}",
                    "title": random.choice([
                        "TG Notizie", "Film della sera", "Talk show", "Serie TV",
                        "Documentario", "Reality show", "Quiz", "Sport"
                    ]),
                    "genre": random.choice(["News", "Film", "Serie", "Intrattenimento", "Sport"]),
                    "duration_minutes": duration
                })
                current_hour += duration // 60
            
            schedule.append({
                "channel": ch,
                "date": date,
                "programs": programs[:8]  # Limit programs
            })
        
        return {
            "date": date,
            "prime_time_only": prime_time,
            "schedule": schedule
        }
    
    elif tool_name == "get_podcast_episodes":
        podcast = args.get("podcast_name", "")
        limit = args.get("limit", 10)
        
        episodes = []
        for i in range(min(limit, random.randint(5, 10))):
            episodes.append({
                "episode_number": 100 - i,
                "title": f"Episodio {100 - i}: {random.choice(['Intervista esclusiva', 'Approfondimento', 'Speciale', 'Live Q&A'])}",
                "duration": f"{random.randint(20, 90)} min",
                "date": (datetime.now() - timedelta(days=i * 7)).strftime("%Y-%m-%d"),
                "description": "Una puntata imperdibile con ospiti speciali e discussioni approfondite.",
                "plays": random.randint(1000, 100000)
            })
        
        return {
            "podcast": podcast,
            "episodes": episodes,
            "total_episodes": random.randint(50, 200),
            "subscribers": random.randint(10000, 500000)
        }
    
    elif tool_name == "get_sports_scores":
        sport = args.get("sport", "football")
        league = args.get("league")
        team = args.get("team")
        
        if sport == "football":
            matches = []
            for i in range(random.randint(3, 6)):
                teams = random.sample(SPORTS_TEAMS_FOOTBALL, 2)
                matches.append({
                    "home": teams[0],
                    "away": teams[1],
                    "score": f"{random.randint(0, 4)} - {random.randint(0, 4)}",
                    "status": random.choice(["Terminata", "In corso", "2° tempo", "Intervallo"]),
                    "minute": random.randint(1, 90) if "corso" in random.choice(["In corso", "altro"]) else None,
                    "competition": league or "Serie A"
                })
            
            return {
                "sport": sport,
                "league": league or "Serie A",
                "matches": matches,
                "last_update": datetime.now().isoformat()
            }
        
        elif sport == "f1":
            return {
                "sport": "Formula 1",
                "event": f"GP {random.choice(['Monaco', 'Monza', 'Silverstone', 'Spa'])}",
                "standings": [
                    {"position": i+1, "driver": random.choice(["Verstappen", "Hamilton", "Leclerc", "Norris", "Sainz"]), 
                     "team": random.choice(["Red Bull", "Mercedes", "Ferrari", "McLaren"]), 
                     "gap": f"+{random.uniform(0.1, 30):.3f}s" if i > 0 else "Leader"}
                    for i in range(5)
                ],
                "status": random.choice(["In corso", "Bandiera a scacchi", "Non iniziato"])
            }
        
        return {"sport": sport, "message": "Sport non supportato al momento"}
    
    return {"error": f"Unknown media tool: {tool_name}"}
