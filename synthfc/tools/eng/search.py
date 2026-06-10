"""Search and information retrieval mock tools."""

import random
from datetime import datetime, timedelta

SEARCH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "default": 5},
                    "language": {"type": "string", "default": "it"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search and retrieve information from Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Topic to search"},
                    "language": {"type": "string", "enum": ["it", "en", "de", "fr", "es"], "default": "it"},
                    "summary_only": {"type": "boolean", "default": True}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "Search for recent news articles",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "category": {"type": "string", "enum": ["general", "technology", "business", "sports", "entertainment", "science"]},
                    "time_range": {"type": "string", "enum": ["24h", "7d", "30d"], "default": "7d"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_images",
            "description": "Search for images on the web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "size": {"type": "string", "enum": ["small", "medium", "large"], "default": "medium"},
                    "type": {"type": "string", "enum": ["photo", "clipart", "illustration", "any"], "default": "any"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_definition",
            "description": "Look up the definition of a word or term",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {"type": "string"},
                    "language": {"type": "string", "default": "it"},
                    "include_examples": {"type": "boolean", "default": True}
                },
                "required": ["word"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_local_places",
            "description": "Search for local businesses, restaurants, or points of interest",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"},
                    "location": {"type": "string", "description": "City or address"},
                    "radius_km": {"type": "number", "default": 5},
                    "category": {"type": "string", "enum": ["restaurant", "hotel", "shop", "pharmacy", "gas_station", "any"]}
                },
                "required": ["query", "location"]
            }
        }
    },
]

# Mock data
WIKI_SUMMARIES = {
    "default": "Wikipedia fornisce informazioni enciclopediche su questo argomento. L'articolo copre la storia, le caratteristiche principali e le applicazioni moderne del soggetto richiesto.",
    "tech": "La tecnologia descritta in questo articolo rappresenta un'importante innovazione nel suo campo. Sviluppata negli ultimi decenni, ha rivoluzionato il modo in cui interagiamo con i sistemi digitali.",
    "science": "Questo fenomeno scientifico è stato studiato approfonditamente dalla comunità accademica. Le ricerche dimostrano correlazioni significative e applicazioni pratiche in diversi ambiti.",
    "history": "L'evento storico descritto ha avuto profonde ripercussioni sulla società dell'epoca. Gli storici concordano sull'importanza di questo momento nella formazione del mondo moderno."
}

NEWS_HEADLINES = [
    "Nuovi sviluppi nel settore tecnologico italiano",
    "Innovazione e sostenibilità al centro del dibattito",
    "Esperti analizzano le tendenze del mercato",
    "Studio rivela importanti scoperte nel campo",
    "Aziende italiane leader nel settore"
]

NEWS_SOURCES = ["ANSA", "Repubblica", "Corriere della Sera", "Il Sole 24 Ore", "Sky TG24", "AGI"]


def execute_search_tool(tool_name: str, args: dict) -> dict:
    """Execute search mock tool."""
    
    if tool_name == "web_search":
        query = args.get("query", "")
        num_results = args.get("num_results", 5)
        
        results = []
        for i in range(num_results):
            results.append({
                "title": f"Risultato per '{query}' - {random.choice(['Guida completa', 'Approfondimento', 'News', 'Tutorial'])}",
                "url": f"https://example{i+1}.com/{query.replace(' ', '-').lower()}",
                "snippet": f"Informazioni dettagliate su {query}. Scopri tutto quello che devi sapere su questo argomento con la nostra guida completa e aggiornata...",
                "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
            })
        
        return {
            "query": query,
            "results": results,
            "total_results": random.randint(1000, 100000),
            "search_time_ms": random.randint(100, 500)
        }
    
    elif tool_name == "search_wikipedia":
        query = args.get("query", "")
        language = args.get("language", "it")
        
        # Pick appropriate summary based on query keywords
        summary = WIKI_SUMMARIES["default"]
        if any(w in query.lower() for w in ["computer", "software", "ai", "digitale"]):
            summary = WIKI_SUMMARIES["tech"]
        elif any(w in query.lower() for w in ["scienza", "fisica", "chimica", "biologia"]):
            summary = WIKI_SUMMARIES["science"]
        elif any(w in query.lower() for w in ["storia", "guerra", "antico", "secolo"]):
            summary = WIKI_SUMMARIES["history"]
        
        return {
            "title": query.title(),
            "summary": summary.replace("questo argomento", query),
            "url": f"https://{language}.wikipedia.org/wiki/{query.replace(' ', '_')}",
            "categories": random.sample(["Storia", "Scienza", "Tecnologia", "Cultura", "Società", "Geografia"], 3),
            "last_updated": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
            "language": language
        }
    
    elif tool_name == "search_news":
        query = args.get("query", "")
        category = args.get("category", "general")
        time_range = args.get("time_range", "7d")
        
        articles = []
        for i in range(random.randint(3, 7)):
            hours_ago = random.randint(1, 168 if time_range == "7d" else 24 if time_range == "24h" else 720)
            articles.append({
                "title": f"{random.choice(NEWS_HEADLINES).replace('settore', query) if random.random() > 0.3 else query + ': ' + random.choice(['ultime notizie', 'aggiornamenti', 'breaking news'])}",
                "source": random.choice(NEWS_SOURCES),
                "url": f"https://news.example.com/article/{random.randint(10000, 99999)}",
                "published": f"{hours_ago}h fa" if hours_ago < 24 else f"{hours_ago // 24}g fa",
                "snippet": f"Le ultime notizie su {query}. Segui gli sviluppi in tempo reale..."
            })
        
        return {
            "query": query,
            "category": category,
            "time_range": time_range,
            "articles": articles,
            "total_found": len(articles)
        }
    
    elif tool_name == "search_images":
        query = args.get("query", "")
        limit = args.get("limit", 10)
        
        images = []
        for i in range(limit):
            images.append({
                "title": f"{query} - Immagine {i+1}",
                "url": f"https://images.example.com/{random.randint(100000, 999999)}.jpg",
                "thumbnail": f"https://images.example.com/thumb/{random.randint(100000, 999999)}.jpg",
                "width": random.choice([800, 1024, 1920, 2560]),
                "height": random.choice([600, 768, 1080, 1440]),
                "source": random.choice(["Unsplash", "Pexels", "Pixabay", "Wikimedia"])
            })
        
        return {
            "query": query,
            "images": images,
            "total_found": random.randint(100, 10000)
        }
    
    elif tool_name == "lookup_definition":
        word = args.get("word", "")
        
        definitions = [
            f"1. Termine che indica {word.lower()} in senso generale o specifico.",
            f"2. Nel linguaggio comune, si riferisce a qualcosa legato a {word.lower()}."
        ]
        
        result = {
            "word": word,
            "language": args.get("language", "it"),
            "definitions": definitions,
            "part_of_speech": random.choice(["sostantivo", "verbo", "aggettivo", "avverbio"]),
            "pronunciation": f"/{word.lower()}/",
        }
        
        if args.get("include_examples", True):
            result["examples"] = [
                f"Questo è un esempio di utilizzo della parola '{word}'.",
                f"'{word.capitalize()}' viene spesso usato in questo contesto."
            ]
            result["synonyms"] = random.sample(["termine1", "termine2", "termine3", "termine4"], 2)
        
        return result
    
    elif tool_name == "search_local_places":
        query = args.get("query", "")
        location = args.get("location", "Milano")
        radius = args.get("radius_km", 5)
        
        places = []
        for i in range(random.randint(3, 8)):
            places.append({
                "name": f"{query.title()} {random.choice(['Da Mario', 'Centrale', 'Express', 'Plus', 'Premium', 'Elite'])} {i+1}",
                "address": f"Via {random.choice(['Roma', 'Milano', 'Garibaldi', 'Dante', 'Mazzini'])} {random.randint(1, 200)}, {location}",
                "rating": round(random.uniform(3.0, 5.0), 1),
                "reviews_count": random.randint(10, 500),
                "distance_km": round(random.uniform(0.1, radius), 1),
                "open_now": random.random() > 0.3,
                "phone": f"+39 {random.randint(300, 399)} {random.randint(1000000, 9999999)}",
                "category": args.get("category", "any")
            })
        
        # Sort by distance
        places.sort(key=lambda x: x["distance_km"])
        
        return {
            "query": query,
            "location": location,
            "radius_km": radius,
            "places": places,
            "total_found": len(places)
        }
    
    return {"error": f"Unknown search tool: {tool_name}"}
