"""Social Media management and monitoring mock tools."""

import random
from datetime import datetime, timedelta

SOCIAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "post_to_social",
            "description": "Create and publish a post to social media platforms",
            "parameters": {
                "type": "object",
                "properties": {
                    "platforms": {"type": "array", "items": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin", "tiktok"]}},
                    "content": {"type": "string", "description": "Post text content"},
                    "media_urls": {"type": "array", "items": {"type": "string"}, "description": "URLs of media to attach"},
                    "schedule_time": {"type": "string", "description": "ISO datetime to schedule post"},
                    "hashtags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["platforms", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_social_analytics",
            "description": "Get analytics data for social media accounts",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin", "tiktok", "all"]},
                    "metric": {"type": "string", "enum": ["engagement", "reach", "followers", "clicks", "impressions"]},
                    "period": {"type": "string", "enum": ["24h", "7d", "30d", "90d"]},
                    "compare_previous": {"type": "boolean", "default": False}
                },
                "required": ["platform"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_mentions",
            "description": "Get mentions and tags of your account or brand",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin", "all"]},
                    "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral", "all"]},
                    "limit": {"type": "integer", "default": 20},
                    "include_replies": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_post",
            "description": "Schedule a social media post for future publication",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "enum": ["twitter", "facebook", "instagram", "linkedin"]},
                    "content": {"type": "string"},
                    "scheduled_time": {"type": "string", "description": "ISO datetime"},
                    "media_urls": {"type": "array", "items": {"type": "string"}},
                    "first_comment": {"type": "string", "description": "Auto-post first comment (Instagram)"}
                },
                "required": ["platform", "content", "scheduled_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trending_topics",
            "description": "Get current trending topics and hashtags",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "enum": ["twitter", "tiktok", "instagram"]},
                    "location": {"type": "string", "description": "Country or city"},
                    "category": {"type": "string", "enum": ["all", "tech", "entertainment", "sports", "news", "business"]}
                },
                "required": ["platform"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reply_to_comment",
            "description": "Reply to a comment or message on social media",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string"},
                    "comment_id": {"type": "string"},
                    "reply_text": {"type": "string"},
                    "include_mention": {"type": "boolean", "default": True}
                },
                "required": ["platform", "comment_id", "reply_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_competitor_analysis",
            "description": "Analyze competitor social media performance",
            "parameters": {
                "type": "object",
                "properties": {
                    "competitor_handles": {"type": "array", "items": {"type": "string"}},
                    "platform": {"type": "string", "enum": ["twitter", "instagram", "linkedin"]},
                    "metrics": {"type": "array", "items": {"type": "string", "enum": ["followers", "engagement_rate", "post_frequency", "top_content"]}}
                },
                "required": ["competitor_handles", "platform"]
            }
        }
    },
]

# Mock data
TRENDING_IT = [
    "#SerieA", "#GFVip", "#Sanremo2024", "#Italia", "#Milano", "#Roma",
    "#Calcio", "#TechItalia", "#Lavoro", "#Politica"
]

TRENDING_TECH = [
    "#AI", "#MachineLearning", "#Startup", "#Innovation", "#Tech",
    "#Programming", "#DevOps", "#CloudComputing", "#Cybersecurity"
]

USERNAMES = ["@user_" + str(random.randint(1000, 9999)) for _ in range(20)]


def execute_social_tool(tool_name: str, args: dict) -> dict:
    """Execute social media mock tool."""
    
    if tool_name == "post_to_social":
        platforms = args.get("platforms", ["twitter"])
        content = args.get("content", "")
        
        results = []
        for platform in platforms:
            post_id = f"{platform}_{random.randint(1000000, 9999999)}"
            results.append({
                "platform": platform,
                "post_id": post_id,
                "status": "published" if not args.get("schedule_time") else "scheduled",
                "url": f"https://{platform}.com/post/{post_id}",
                "scheduled_for": args.get("schedule_time"),
                "character_count": len(content),
                "media_attached": len(args.get("media_urls", []))
            })
        
        return {
            "status": "success",
            "posts": results,
            "total_platforms": len(platforms),
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "get_social_analytics":
        platform = args.get("platform", "all")
        metric = args.get("metric", "engagement")
        period = args.get("period", "7d")
        
        multiplier = {"24h": 1, "7d": 7, "30d": 30, "90d": 90}.get(period, 7)
        
        data = {
            "engagement": {
                "total_engagements": random.randint(500, 10000) * multiplier // 7,
                "likes": random.randint(200, 5000) * multiplier // 7,
                "comments": random.randint(50, 500) * multiplier // 7,
                "shares": random.randint(20, 200) * multiplier // 7,
                "saves": random.randint(10, 100) * multiplier // 7,
                "engagement_rate": round(random.uniform(1, 8), 2),
                "best_performing_post": {
                    "id": f"post_{random.randint(10000, 99999)}",
                    "engagements": random.randint(500, 5000),
                    "content_preview": "Il nostro ultimo post ha ottenuto..."
                }
            },
            "reach": {
                "total_reach": random.randint(5000, 100000) * multiplier // 7,
                "unique_accounts_reached": random.randint(3000, 80000) * multiplier // 7,
                "impressions": random.randint(10000, 200000) * multiplier // 7,
                "profile_visits": random.randint(100, 2000) * multiplier // 7,
                "reach_rate": round(random.uniform(10, 40), 2)
            },
            "followers": {
                "total_followers": random.randint(1000, 100000),
                "new_followers": random.randint(10, 500) * multiplier // 7,
                "unfollows": random.randint(5, 50) * multiplier // 7,
                "net_change": random.randint(-20, 450) * multiplier // 7,
                "growth_rate": round(random.uniform(-2, 10), 2),
                "demographics": {
                    "top_countries": ["Italia", "USA", "UK"],
                    "age_groups": {"18-24": "25%", "25-34": "40%", "35-44": "20%", "45+": "15%"},
                    "gender": {"male": "45%", "female": "52%", "other": "3%"}
                }
            }
        }
        
        result = {
            "platform": platform,
            "metric": metric,
            "period": period,
            "data": data.get(metric, data["engagement"]),
            "generated_at": datetime.now().isoformat()
        }
        
        if args.get("compare_previous", False):
            result["comparison"] = {
                "previous_period": f"vs {period} precedente",
                "change_percent": round(random.uniform(-20, 50), 1),
                "trend": random.choice(["up", "down", "stable"])
            }
        
        return result
    
    elif tool_name == "get_mentions":
        platform = args.get("platform", "all")
        sentiment_filter = args.get("sentiment", "all")
        limit = args.get("limit", 20)
        
        mentions = []
        sentiments = ["positive", "negative", "neutral"]
        
        for i in range(min(limit, random.randint(5, 15))):
            sentiment = random.choice(sentiments) if sentiment_filter == "all" else sentiment_filter
            mentions.append({
                "id": f"mention_{random.randint(100000, 999999)}",
                "platform": platform if platform != "all" else random.choice(["twitter", "instagram", "facebook"]),
                "author": random.choice(USERNAMES),
                "content": random.choice([
                    "Ottimo servizio! @brand è il migliore",
                    "Ho avuto un problema con @brand, qualcuno può aiutarmi?",
                    "Qualcuno ha provato @brand? Opinioni?",
                    "Grazie @brand per il supporto veloce!",
                    "Non sono soddisfatto di @brand ultimamente..."
                ]),
                "sentiment": sentiment,
                "sentiment_score": round(random.uniform(-1, 1), 2),
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                "engagement": {
                    "likes": random.randint(0, 100),
                    "replies": random.randint(0, 20),
                    "shares": random.randint(0, 10)
                },
                "url": f"https://social.com/post/{random.randint(100000, 999999)}"
            })
        
        return {
            "platform": platform,
            "mentions": mentions,
            "total": len(mentions),
            "sentiment_breakdown": {
                "positive": sum(1 for m in mentions if m["sentiment"] == "positive"),
                "negative": sum(1 for m in mentions if m["sentiment"] == "negative"),
                "neutral": sum(1 for m in mentions if m["sentiment"] == "neutral")
            }
        }
    
    elif tool_name == "schedule_post":
        post_id = f"scheduled_{random.randint(100000, 999999)}"
        
        return {
            "status": "scheduled",
            "post": {
                "id": post_id,
                "platform": args.get("platform"),
                "content": args.get("content"),
                "scheduled_time": args.get("scheduled_time"),
                "media_count": len(args.get("media_urls", [])),
                "first_comment": args.get("first_comment")
            },
            "can_edit_until": (datetime.fromisoformat(args.get("scheduled_time", datetime.now().isoformat())) - timedelta(minutes=5)).isoformat(),
            "message": f"Post programmato per {args.get('scheduled_time')}"
        }
    
    elif tool_name == "get_trending_topics":
        platform = args.get("platform", "twitter")
        location = args.get("location", "Italia")
        category = args.get("category", "all")
        
        topics = []
        hashtags = TRENDING_IT if location == "Italia" else TRENDING_TECH
        
        for i, tag in enumerate(random.sample(hashtags, min(10, len(hashtags)))):
            topics.append({
                "rank": i + 1,
                "topic": tag,
                "tweet_volume": random.randint(5000, 500000),
                "trend_direction": random.choice(["rising", "stable", "declining"]),
                "category": random.choice(["news", "entertainment", "sports", "tech"]),
                "started_trending": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            })
        
        return {
            "platform": platform,
            "location": location,
            "category": category,
            "trending": topics,
            "updated_at": datetime.now().isoformat()
        }
    
    elif tool_name == "reply_to_comment":
        reply_id = f"reply_{random.randint(100000, 999999)}"
        
        return {
            "status": "replied",
            "reply": {
                "id": reply_id,
                "platform": args.get("platform"),
                "parent_comment_id": args.get("comment_id"),
                "text": args.get("reply_text"),
                "url": f"https://social.com/reply/{reply_id}"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "get_competitor_analysis":
        competitors = args.get("competitor_handles", [])
        platform = args.get("platform", "instagram")
        
        analysis = []
        for handle in competitors:
            analysis.append({
                "handle": handle,
                "platform": platform,
                "followers": random.randint(1000, 1000000),
                "following": random.randint(100, 5000),
                "posts_count": random.randint(100, 5000),
                "engagement_rate": round(random.uniform(0.5, 8), 2),
                "avg_likes_per_post": random.randint(50, 10000),
                "avg_comments_per_post": random.randint(5, 500),
                "post_frequency": f"{round(random.uniform(0.5, 3), 1)} posts/giorno",
                "top_hashtags": random.sample(TRENDING_IT + TRENDING_TECH, 5),
                "best_posting_times": ["09:00", "12:00", "18:00"],
                "content_types": {
                    "images": f"{random.randint(40, 70)}%",
                    "videos": f"{random.randint(20, 40)}%",
                    "carousels": f"{random.randint(5, 20)}%"
                }
            })
        
        return {
            "platform": platform,
            "competitors": analysis,
            "your_position": {
                "followers_rank": random.randint(1, len(competitors) + 1),
                "engagement_rank": random.randint(1, len(competitors) + 1)
            },
            "generated_at": datetime.now().isoformat()
        }
    
    return {"error": f"Unknown social tool: {tool_name}"}
