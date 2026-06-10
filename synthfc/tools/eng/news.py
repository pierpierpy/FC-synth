"""News and RSS feed mock tools."""

import random
from datetime import datetime, timedelta

NEWS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_news_headlines",
            "description": "Get latest news headlines by category or source",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["general", "technology", "business", "sports", "entertainment", "science", "health", "politics"]},
                    "country": {"type": "string", "description": "Country code (it, us, uk, etc.)"},
                    "source": {"type": "string", "description": "News source name"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "Search for news articles by keywords",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "from_date": {"type": "string", "description": "Start date YYYY-MM-DD"},
                    "to_date": {"type": "string", "description": "End date YYYY-MM-DD"},
                    "language": {"type": "string", "default": "it"},
                    "sort_by": {"type": "string", "enum": ["relevance", "date", "popularity"]}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_rss_feed",
            "description": "Get and parse RSS feed from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "feed_url": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                    "include_content": {"type": "boolean", "default": False}
                },
                "required": ["feed_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subscribe_news_alert",
            "description": "Subscribe to news alerts for specific topics",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "frequency": {"type": "string", "enum": ["instant", "daily", "weekly"]},
                    "delivery_method": {"type": "string", "enum": ["email", "push", "sms"]},
                    "sources": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_article_summary",
            "description": "Get AI-generated summary of a news article",
            "parameters": {
                "type": "object",
                "properties": {
                    "article_url": {"type": "string"},
                    "summary_length": {"type": "string", "enum": ["short", "medium", "long"]},
                    "include_key_points": {"type": "boolean", "default": True},
                    "translate_to": {"type": "string", "description": "Target language for translation"}
                },
                "required": ["article_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trending_news",
            "description": "Get currently trending news stories",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "default": "IT"},
                    "timeframe": {"type": "string", "enum": ["1h", "6h", "24h", "7d"]},
                    "category": {"type": "string"}
                },
                "required": []
            }
        }
    },
]

# Mock data
NEWS_SOURCES_IT = [
    "ANSA", "Corriere della Sera", "La Repubblica", "Il Sole 24 Ore", 
    "La Stampa", "Il Messaggero", "Sky TG24", "RaiNews"
]

NEWS_SOURCES_INTL = [
    "BBC", "CNN", "Reuters", "The Guardian", "New York Times", "Bloomberg"
]

HEADLINES_IT = {
    "general": [
        "Il governo annuncia nuove misure per l'economia",
        "Maltempo in arrivo: allerta meteo in 5 regioni",
        "Sciopero dei trasporti: disagi previsti per domani",
        "Nuova riforma della scuola approvata in Senato",
        "Italia-Germania: incontro tra i premier a Berlino"
    ],
    "technology": [
        "Apple annuncia il nuovo iPhone 16: tutte le novità",
        "Intelligenza artificiale: nuove linee guida dall'UE",
        "Cybersecurity: attacco hacker a infrastrutture italiane",
        "5G: copertura raggiunge il 70% del territorio",
        "Startup italiana raccoglie 50 milioni di investimenti"
    ],
    "business": [
        "Borsa Milano chiude in rialzo: +1.2%",
        "BCE: possibile taglio dei tassi in arrivo",
        "Fiat-Stellantis: nuovo piano industriale 2025",
        "Inflazione in calo: dati ISTAT positivi",
        "Export italiano: record storico nel trimestre"
    ],
    "sports": [
        "Serie A: risultati e classifica della giornata",
        "Formula 1: Ferrari vince il GP di Monza",
        "Tennis: Sinner in finale agli Australian Open",
        "Olimpiadi 2024: medaglie azzurre in crescita",
        "Calciomercato: ultime trattative in corso"
    ],
    "entertainment": [
        "Sanremo 2024: anticipazioni sui cantanti in gara",
        "Cinema: film italiano candidato agli Oscar",
        "Netflix annuncia nuova serie originale italiana",
        "Musica: Måneskin tornano con nuovo album",
        "Teatro: sold out per lo spettacolo alla Scala"
    ]
}


def execute_news_tool(tool_name: str, args: dict) -> dict:
    """Execute news mock tool."""
    
    if tool_name == "get_news_headlines":
        category = args.get("category", "general")
        country = args.get("country", "it")
        limit = args.get("limit", 10)
        
        headlines = HEADLINES_IT.get(category, HEADLINES_IT["general"])
        sources = NEWS_SOURCES_IT if country == "it" else NEWS_SOURCES_INTL
        
        articles = []
        for i in range(min(limit, len(headlines) + random.randint(0, 5))):
            pub_time = datetime.now() - timedelta(hours=random.randint(1, 48))
            articles.append({
                "title": headlines[i % len(headlines)] if i < len(headlines) else f"Notizia {category} #{i}",
                "source": random.choice(sources),
                "published_at": pub_time.isoformat(),
                "url": f"https://news.example.com/article/{random.randint(10000, 99999)}",
                "image_url": f"https://images.news.com/{random.randint(1000, 9999)}.jpg",
                "description": f"Ultime notizie su {category}. Continua a leggere per tutti i dettagli...",
                "author": f"{random.choice(['Marco', 'Giulia', 'Andrea', 'Sara'])} {random.choice(['Rossi', 'Bianchi', 'Verdi'])}"
            })
        
        return {
            "category": category,
            "country": country,
            "articles": articles,
            "total_results": len(articles),
            "fetched_at": datetime.now().isoformat()
        }
    
    elif tool_name == "search_news":
        query = args.get("query", "")
        from_date = args.get("from_date")
        to_date = args.get("to_date")
        
        articles = []
        for i in range(random.randint(5, 15)):
            pub_time = datetime.now() - timedelta(days=random.randint(1, 30))
            
            articles.append({
                "title": f"{query}: {random.choice(['Ultime novità', 'Aggiornamenti', 'Sviluppi', 'Analisi', 'Approfondimento'])}",
                "source": random.choice(NEWS_SOURCES_IT + NEWS_SOURCES_INTL),
                "published_at": pub_time.isoformat(),
                "url": f"https://news.example.com/search/{random.randint(10000, 99999)}",
                "relevance_score": round(random.uniform(0.6, 1.0), 2),
                "snippet": f"... {query} è al centro dell'attenzione. Gli esperti commentano... continua a leggere...",
                "word_count": random.randint(300, 2000),
                "reading_time_minutes": random.randint(2, 10)
            })
        
        articles.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "query": query,
            "from_date": from_date,
            "to_date": to_date,
            "total_results": len(articles),
            "articles": articles
        }
    
    elif tool_name == "get_rss_feed":
        feed_url = args.get("feed_url", "")
        limit = args.get("limit", 20)
        include_content = args.get("include_content", False)
        
        items = []
        for i in range(min(limit, random.randint(10, 20))):
            pub_time = datetime.now() - timedelta(hours=random.randint(1, 72))
            
            item = {
                "title": f"Feed Item #{i+1}: {random.choice(['Notizia importante', 'Aggiornamento', 'Breaking news', 'Reportage'])}",
                "link": f"https://feed.example.com/item/{random.randint(1000, 9999)}",
                "published": pub_time.isoformat(),
                "author": random.choice(["Redazione", "Staff", "Editor"]),
                "categories": random.sample(["News", "Tech", "Business", "Sport", "Cultura"], 2),
                "guid": f"item-{random.randint(100000, 999999)}"
            }
            
            if include_content:
                item["content"] = f"<p>Contenuto completo dell'articolo. Lorem ipsum dolor sit amet, consectetur adipiscing elit. {random.choice(['Importante sviluppo', 'Nuova analisi', 'Ultimi dati'])}...</p>"
            
            items.append(item)
        
        return {
            "feed": {
                "title": f"Feed - {feed_url.split('/')[2] if '/' in feed_url else 'Unknown'}",
                "description": "RSS Feed automatico",
                "link": feed_url,
                "last_updated": datetime.now().isoformat()
            },
            "items": items,
            "item_count": len(items)
        }
    
    elif tool_name == "subscribe_news_alert":
        keywords = args.get("keywords", [])
        frequency = args.get("frequency", "daily")
        delivery = args.get("delivery_method", "email")
        
        alert_id = f"ALERT{random.randint(10000, 99999)}"
        
        return {
            "status": "subscribed",
            "alert": {
                "id": alert_id,
                "keywords": keywords,
                "frequency": frequency,
                "delivery_method": delivery,
                "sources": args.get("sources", ["all"]),
                "created_at": datetime.now().isoformat(),
                "next_delivery": {
                    "instant": "Quando disponibile",
                    "daily": (datetime.now() + timedelta(days=1)).replace(hour=8, minute=0).isoformat(),
                    "weekly": (datetime.now() + timedelta(days=7)).isoformat()
                }[frequency]
            },
            "message": f"Alert attivo per: {', '.join(keywords)}"
        }
    
    elif tool_name == "get_article_summary":
        article_url = args.get("article_url", "")
        summary_length = args.get("summary_length", "medium")
        include_key_points = args.get("include_key_points", True)
        
        lengths = {"short": 50, "medium": 150, "long": 300}
        
        summary = {
            "article_url": article_url,
            "title": f"Articolo: {random.choice(['Analisi importante', 'Sviluppi recenti', 'Novità significative'])}",
            "summary": f"L'articolo tratta di {'sviluppi importanti' if summary_length != 'short' else 'notizie'}. " * (lengths[summary_length] // 50),
            "original_length_words": random.randint(500, 3000),
            "summary_length_words": lengths[summary_length],
            "reading_time_saved_minutes": random.randint(3, 15)
        }
        
        if include_key_points:
            summary["key_points"] = [
                "Punto chiave 1: sviluppo principale della notizia",
                "Punto chiave 2: implicazioni e conseguenze",
                "Punto chiave 3: commenti degli esperti",
                "Punto chiave 4: prospettive future"
            ][:random.randint(2, 4)]
        
        if args.get("translate_to"):
            summary["translated_to"] = args["translate_to"]
            summary["note"] = "Contenuto tradotto automaticamente"
        
        return summary
    
    elif tool_name == "get_trending_news":
        region = args.get("region", "IT")
        timeframe = args.get("timeframe", "24h")
        
        trending = []
        for i in range(random.randint(8, 15)):
            trending.append({
                "rank": i + 1,
                "title": random.choice([
                    "Governo: nuova manovra economica",
                    "Serie A: sorpresa in classifica",
                    "Tech: lancio nuovo prodotto Apple",
                    "Sanità: novità sui vaccini",
                    "Economia: dati PIL migliori del previsto",
                    "Meteo: ondata di maltempo in arrivo",
                    "Spettacolo: vincitore di X Factor"
                ]),
                "trend_score": random.randint(1000, 100000),
                "articles_count": random.randint(10, 500),
                "trend_direction": random.choice(["rising", "stable", "declining"]),
                "related_queries": random.sample(["governo", "economia", "sport", "tech", "meteo"], 2)
            })
        
        return {
            "region": region,
            "timeframe": timeframe,
            "trending_stories": trending,
            "updated_at": datetime.now().isoformat()
        }
    
    return {"error": f"Unknown news tool: {tool_name}"}
