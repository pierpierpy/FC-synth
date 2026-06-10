"""CRM and customer management mock tools."""

import random
from datetime import datetime, timedelta

CRM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_customers",
            "description": "Search for customers in CRM",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Name, email, phone, or company"},
                    "filters": {"type": "object", "properties": {
                        "status": {"type": "string", "enum": ["active", "inactive", "prospect", "churned"]},
                        "segment": {"type": "string"},
                        "created_after": {"type": "string"}
                    }},
                    "limit": {"type": "integer", "default": 20}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_details",
            "description": "Get detailed information about a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "include_orders": {"type": "boolean", "default": True},
                    "include_interactions": {"type": "boolean", "default": True},
                    "include_tickets": {"type": "boolean", "default": False}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_customer",
            "description": "Create a new customer record",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "company": {"type": "string"},
                    "segment": {"type": "string", "enum": ["individual", "small_business", "enterprise"]},
                    "source": {"type": "string", "enum": ["website", "referral", "advertising", "event", "cold_call"]},
                    "notes": {"type": "string"}
                },
                "required": ["name", "email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_interaction",
            "description": "Log a customer interaction (call, email, meeting)",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "interaction_type": {"type": "string", "enum": ["call", "email", "meeting", "chat", "social", "support_ticket"]},
                    "subject": {"type": "string"},
                    "notes": {"type": "string"},
                    "outcome": {"type": "string", "enum": ["positive", "neutral", "negative", "follow_up_needed"]},
                    "next_action_date": {"type": "string"}
                },
                "required": ["customer_id", "interaction_type", "subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_deal",
            "description": "Create a sales deal/opportunity",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "title": {"type": "string"},
                    "value": {"type": "number"},
                    "currency": {"type": "string", "default": "EUR"},
                    "stage": {"type": "string", "enum": ["lead", "qualified", "proposal", "negotiation", "won", "lost"]},
                    "expected_close_date": {"type": "string"},
                    "probability": {"type": "integer", "minimum": 0, "maximum": 100},
                    "products": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["customer_id", "title", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_pipeline",
            "description": "Get sales pipeline overview",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner_id": {"type": "string", "description": "Filter by sales rep"},
                    "period": {"type": "string", "enum": ["current_month", "current_quarter", "current_year"]},
                    "include_forecast": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_campaign",
            "description": "Send marketing campaign to customer segment",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string"},
                    "segment": {"type": "string", "description": "Target customer segment"},
                    "channel": {"type": "string", "enum": ["email", "sms", "push", "whatsapp"]},
                    "template_id": {"type": "string"},
                    "schedule_time": {"type": "string", "description": "ISO datetime or 'now'"},
                    "personalization": {"type": "boolean", "default": True}
                },
                "required": ["campaign_name", "segment", "channel"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_health_score",
            "description": "Get customer health and churn risk score",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "include_factors": {"type": "boolean", "default": True}
                },
                "required": ["customer_id"]
            }
        }
    },
]

# Mock data
ITALIAN_NAMES = [
    "Mario Rossi", "Giulia Bianchi", "Marco Verdi", "Sara Ferrari",
    "Andrea Russo", "Francesca Romano", "Luca Gallo", "Elena Conti",
    "Alessandro Ricci", "Chiara Marino"
]

COMPANIES = [
    "Acme S.r.l.", "Tech Solutions S.p.A.", "Innovate Lab", "Digital Services",
    "Global Trading", "Smart Systems", "Creative Studio", "Data Dynamics"
]

PRODUCTS = [
    "Piano Base", "Piano Pro", "Piano Enterprise", "Addon Analytics",
    "Supporto Premium", "Formazione", "Consulenza", "Sviluppo Custom"
]


def execute_crm_tool(tool_name: str, args: dict) -> dict:
    """Execute CRM mock tool."""
    
    if tool_name == "search_customers":
        query = args.get("query", "")
        limit = args.get("limit", 20)
        filters = args.get("filters", {})
        
        customers = []
        for i in range(min(limit, random.randint(3, 12))):
            name = random.choice(ITALIAN_NAMES)
            customers.append({
                "id": f"CUST{random.randint(10000, 99999)}",
                "name": name,
                "email": f"{name.lower().replace(' ', '.')}@{random.choice(['email.com', 'azienda.it', 'company.com'])}",
                "phone": f"+39 3{random.randint(20, 99)} {random.randint(1000000, 9999999)}",
                "company": random.choice(COMPANIES) if random.random() > 0.4 else None,
                "status": filters.get("status") or random.choice(["active", "active", "prospect", "inactive"]),
                "segment": filters.get("segment") or random.choice(["individual", "small_business", "enterprise"]),
                "lifetime_value": round(random.uniform(100, 50000), 2),
                "last_interaction": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d")
            })
        
        return {
            "query": query,
            "filters": filters,
            "results": customers,
            "total": len(customers),
            "has_more": random.random() > 0.7
        }
    
    elif tool_name == "get_customer_details":
        customer_id = args.get("customer_id")
        
        name = random.choice(ITALIAN_NAMES)
        
        customer = {
            "id": customer_id,
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@email.com",
            "phone": f"+39 3{random.randint(20, 99)} {random.randint(1000000, 9999999)}",
            "company": random.choice(COMPANIES) if random.random() > 0.3 else None,
            "status": random.choice(["active", "prospect"]),
            "segment": random.choice(["individual", "small_business", "enterprise"]),
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "address": {
                "street": f"Via {random.choice(['Roma', 'Milano', 'Torino', 'Dante'])}, {random.randint(1, 200)}",
                "city": random.choice(["Milano", "Roma", "Torino", "Bologna", "Firenze"]),
                "postal_code": f"{random.randint(10, 99)}{random.randint(100, 999)}",
                "country": "Italia"
            },
            "tags": random.sample(["VIP", "Early Adopter", "Referral", "Newsletter", "Premium"], random.randint(1, 3)),
            "custom_fields": {
                "industry": random.choice(["Tech", "Finance", "Retail", "Manufacturing"]),
                "company_size": random.choice(["1-10", "11-50", "51-200", "200+"])
            }
        }
        
        if args.get("include_orders", True):
            customer["orders"] = {
                "total_orders": random.randint(1, 50),
                "total_value": round(random.uniform(100, 50000), 2),
                "avg_order_value": round(random.uniform(50, 500), 2),
                "last_order_date": (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d"),
                "recent_orders": [
                    {
                        "id": f"ORD{random.randint(10000, 99999)}",
                        "date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                        "amount": round(random.uniform(50, 1000), 2),
                        "status": random.choice(["completed", "shipped", "pending"])
                    } for _ in range(random.randint(1, 5))
                ]
            }
        
        if args.get("include_interactions", True):
            customer["interactions"] = {
                "total_count": random.randint(3, 50),
                "recent": [
                    {
                        "type": random.choice(["call", "email", "meeting", "chat"]),
                        "date": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                        "subject": random.choice(["Follow-up commerciale", "Supporto tecnico", "Rinnovo contratto", "Richiesta informazioni"]),
                        "outcome": random.choice(["positive", "neutral", "follow_up_needed"])
                    } for _ in range(random.randint(2, 5))
                ]
            }
        
        if args.get("include_tickets", False):
            customer["support_tickets"] = {
                "open": random.randint(0, 3),
                "total": random.randint(1, 20),
                "avg_resolution_hours": random.randint(2, 48)
            }
        
        return customer
    
    elif tool_name == "create_customer":
        customer_id = f"CUST{random.randint(10000, 99999)}"
        
        return {
            "status": "created",
            "customer": {
                "id": customer_id,
                "name": args.get("name"),
                "email": args.get("email"),
                "phone": args.get("phone"),
                "company": args.get("company"),
                "segment": args.get("segment", "individual"),
                "source": args.get("source", "website"),
                "notes": args.get("notes"),
                "created_at": datetime.now().isoformat(),
                "status": "prospect"
            },
            "message": f"Cliente {args.get('name')} creato con successo"
        }
    
    elif tool_name == "log_interaction":
        interaction_id = f"INT{random.randint(100000, 999999)}"
        
        return {
            "status": "logged",
            "interaction": {
                "id": interaction_id,
                "customer_id": args.get("customer_id"),
                "type": args.get("interaction_type"),
                "subject": args.get("subject"),
                "notes": args.get("notes"),
                "outcome": args.get("outcome", "neutral"),
                "next_action_date": args.get("next_action_date"),
                "logged_by": "current_user",
                "logged_at": datetime.now().isoformat()
            },
            "reminder_set": bool(args.get("next_action_date"))
        }
    
    elif tool_name == "create_deal":
        deal_id = f"DEAL{random.randint(10000, 99999)}"
        
        value = args.get("value", 1000)
        probability = args.get("probability", 50)
        
        return {
            "status": "created",
            "deal": {
                "id": deal_id,
                "customer_id": args.get("customer_id"),
                "title": args.get("title"),
                "value": value,
                "currency": args.get("currency", "EUR"),
                "stage": args.get("stage", "lead"),
                "probability": probability,
                "weighted_value": round(value * probability / 100, 2),
                "expected_close_date": args.get("expected_close_date"),
                "products": args.get("products", []),
                "created_at": datetime.now().isoformat(),
                "owner": "current_user"
            }
        }
    
    elif tool_name == "get_sales_pipeline":
        period = args.get("period", "current_month")
        include_forecast = args.get("include_forecast", True)
        
        stages = {
            "lead": {"count": random.randint(10, 30), "value": random.randint(50000, 200000)},
            "qualified": {"count": random.randint(5, 20), "value": random.randint(30000, 150000)},
            "proposal": {"count": random.randint(3, 15), "value": random.randint(20000, 100000)},
            "negotiation": {"count": random.randint(2, 10), "value": random.randint(15000, 80000)},
            "won": {"count": random.randint(1, 8), "value": random.randint(10000, 60000)},
            "lost": {"count": random.randint(1, 5), "value": random.randint(5000, 30000)}
        }
        
        total_value = sum(s["value"] for s in stages.values())
        
        result = {
            "period": period,
            "stages": stages,
            "summary": {
                "total_deals": sum(s["count"] for s in stages.values()),
                "total_value": total_value,
                "win_rate": f"{random.randint(15, 35)}%",
                "avg_deal_size": round(total_value / max(1, sum(s["count"] for s in stages.values())), 2),
                "avg_sales_cycle_days": random.randint(15, 60)
            }
        }
        
        if include_forecast:
            result["forecast"] = {
                "best_case": round(total_value * 0.8, 2),
                "most_likely": round(total_value * 0.5, 2),
                "worst_case": round(total_value * 0.3, 2),
                "target": round(total_value * 0.6, 2),
                "target_achievement": f"{random.randint(70, 120)}%"
            }
        
        return result
    
    elif tool_name == "send_campaign":
        campaign_id = f"CAMP{random.randint(10000, 99999)}"
        
        target_count = random.randint(100, 10000)
        
        return {
            "status": "scheduled" if args.get("schedule_time") != "now" else "sending",
            "campaign": {
                "id": campaign_id,
                "name": args.get("campaign_name"),
                "segment": args.get("segment"),
                "channel": args.get("channel"),
                "template_id": args.get("template_id"),
                "personalization": args.get("personalization", True),
                "scheduled_time": args.get("schedule_time", "now"),
                "target_recipients": target_count,
                "estimated_cost": round(target_count * 0.02, 2) if args.get("channel") in ["sms", "whatsapp"] else 0
            },
            "preview_url": f"https://crm.example.com/campaigns/{campaign_id}/preview"
        }
    
    elif tool_name == "get_customer_health_score":
        customer_id = args.get("customer_id")
        include_factors = args.get("include_factors", True)
        
        health_score = random.randint(30, 100)
        
        result = {
            "customer_id": customer_id,
            "health_score": health_score,
            "health_label": "Eccellente" if health_score >= 80 else "Buono" if health_score >= 60 else "A rischio" if health_score >= 40 else "Critico",
            "churn_risk": "Basso" if health_score >= 70 else "Medio" if health_score >= 50 else "Alto",
            "churn_probability": f"{100 - health_score}%",
            "last_updated": datetime.now().isoformat()
        }
        
        if include_factors:
            result["factors"] = {
                "positive": random.sample([
                    "Utilizzo regolare del prodotto",
                    "Feedback positivi recenti",
                    "Pagamenti puntuali",
                    "Espansione del contratto",
                    "Alto engagement email"
                ], random.randint(1, 3)),
                "negative": random.sample([
                    "Diminuzione dell'utilizzo",
                    "Ticket di supporto non risolti",
                    "Mancata risposta alle comunicazioni",
                    "Nessun rinnovo automatico",
                    "Lamentele recenti"
                ], random.randint(0, 2)),
                "recommendations": [
                    "Programmare chiamata di check-in",
                    "Offrire sessione di formazione",
                    "Proporre upgrade con sconto"
                ][:random.randint(1, 3)]
            }
        
        return result
    
    return {"error": f"Unknown CRM tool: {tool_name}"}
