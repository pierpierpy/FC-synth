"""Database, Analytics and Business Intelligence mock tools."""

import random
from datetime import datetime, timedelta

DATABASE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Execute a read-only SQL query on the connected database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL SELECT query to execute"},
                    "database": {"type": "string", "description": "Database name", "enum": ["sales", "customers", "inventory", "analytics"]},
                    "limit": {"type": "integer", "default": 100}
                },
                "required": ["query", "database"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_report",
            "description": "Generate a sales report for a specific period",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "group_by": {"type": "string", "enum": ["day", "week", "month", "product", "region", "salesperson"]},
                    "filters": {
                        "type": "object",
                        "properties": {
                            "region": {"type": "string"},
                            "product_category": {"type": "string"},
                            "min_amount": {"type": "number"}
                        }
                    }
                },
                "required": ["start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_analytics",
            "description": "Get customer behavior analytics and segmentation data",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": ["churn_risk", "lifetime_value", "engagement", "satisfaction", "purchase_frequency"]},
                    "segment": {"type": "string", "description": "Customer segment to analyze"},
                    "period": {"type": "string", "enum": ["7d", "30d", "90d", "1y"]}
                },
                "required": ["metric"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_inventory_status",
            "description": "Check inventory levels and stock status",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "warehouse": {"type": "string"},
                    "include_forecast": {"type": "boolean", "default": False},
                    "low_stock_only": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_dashboard_widget",
            "description": "Create a new widget for the analytics dashboard",
            "parameters": {
                "type": "object",
                "properties": {
                    "widget_type": {"type": "string", "enum": ["line_chart", "bar_chart", "pie_chart", "kpi_card", "table", "heatmap"]},
                    "data_source": {"type": "string"},
                    "title": {"type": "string"},
                    "refresh_interval_minutes": {"type": "integer", "default": 60}
                },
                "required": ["widget_type", "data_source", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_report",
            "description": "Export data or report to various formats",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_type": {"type": "string", "enum": ["sales", "inventory", "customers", "financial", "custom"]},
                    "format": {"type": "string", "enum": ["csv", "xlsx", "pdf", "json"]},
                    "date_range": {"type": "object", "properties": {"start": {"type": "string"}, "end": {"type": "string"}}},
                    "email_to": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["report_type", "format"]
            }
        }
    },
]

# Mock data generators
REGIONS = ["Nord Italia", "Centro Italia", "Sud Italia", "Isole", "Lombardia", "Lazio", "Campania", "Veneto", "Piemonte", "Emilia-Romagna", "Abruzzo"]
PRODUCTS = ["Laptop Pro X1", "Smartphone Ultra", "Tablet Air", "Monitor 4K", "Tastiera Wireless", "Mouse Ergonomico", "Cuffie BT", "Webcam HD"]
SALESPEOPLE = ["Marco Rossi", "Laura Bianchi", "Giuseppe Verdi", "Anna Ferrari", "Luca Colombo"]


def execute_database_tool(tool_name: str, args: dict) -> dict:
    """Execute database/analytics mock tool."""
    
    if tool_name == "query_database":
        query = args.get("query", "").lower()
        database = args.get("database", "sales")
        limit = args.get("limit", 100)
        
        # Generate mock results based on query keywords
        if "count" in query:
            return {
                "status": "success",
                "database": database,
                "query": args.get("query"),
                "rows_returned": 1,
                "execution_time_ms": random.randint(10, 500),
                "results": [{"count": random.randint(100, 10000)}]
            }
        elif "sum" in query or "total" in query:
            return {
                "status": "success",
                "database": database,
                "query": args.get("query"),
                "rows_returned": 1,
                "execution_time_ms": random.randint(50, 800),
                "results": [{"total": round(random.uniform(10000, 500000), 2)}]
            }
        else:
            rows = []
            for i in range(min(limit, random.randint(5, 20))):
                rows.append({
                    "id": random.randint(1000, 99999),
                    "name": random.choice(PRODUCTS + SALESPEOPLE),
                    "value": round(random.uniform(100, 5000), 2),
                    "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                    "status": random.choice(["active", "pending", "completed"])
                })
            return {
                "status": "success",
                "database": database,
                "query": args.get("query"),
                "rows_returned": len(rows),
                "execution_time_ms": random.randint(20, 300),
                "results": rows
            }
    
    elif tool_name == "get_sales_report":
        start = args.get("start_date", "2024-01-01")
        end = args.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        group_by = args.get("group_by", "day")
        
        total_sales = round(random.uniform(50000, 500000), 2)
        total_orders = random.randint(500, 5000)
        
        breakdown = []
        if group_by == "product":
            for prod in random.sample(PRODUCTS, min(5, len(PRODUCTS))):
                breakdown.append({
                    "product": prod,
                    "revenue": round(random.uniform(5000, 50000), 2),
                    "units_sold": random.randint(50, 500),
                    "avg_price": round(random.uniform(100, 1000), 2)
                })
        elif group_by == "region":
            for reg in random.sample(REGIONS, min(5, len(REGIONS))):
                breakdown.append({
                    "region": reg,
                    "revenue": round(random.uniform(10000, 100000), 2),
                    "orders": random.randint(100, 1000),
                    "growth_percent": round(random.uniform(-10, 30), 1)
                })
        elif group_by == "salesperson":
            for sp in SALESPEOPLE:
                breakdown.append({
                    "salesperson": sp,
                    "revenue": round(random.uniform(20000, 80000), 2),
                    "deals_closed": random.randint(20, 100),
                    "conversion_rate": round(random.uniform(15, 45), 1)
                })
        else:
            # Daily/weekly/monthly
            for i in range(min(10, random.randint(5, 15))):
                breakdown.append({
                    "period": f"Periodo {i+1}",
                    "revenue": round(random.uniform(5000, 30000), 2),
                    "orders": random.randint(50, 300)
                })
        
        return {
            "report_type": "sales",
            "period": {"start": start, "end": end},
            "group_by": group_by,
            "summary": {
                "total_revenue": total_sales,
                "total_orders": total_orders,
                "average_order_value": round(total_sales / total_orders, 2),
                "growth_vs_previous": round(random.uniform(-5, 25), 1),
                "top_product": random.choice(PRODUCTS),
                "top_region": random.choice(REGIONS)
            },
            "breakdown": breakdown,
            "generated_at": datetime.now().isoformat()
        }
    
    elif tool_name == "get_customer_analytics":
        metric = args.get("metric", "engagement")
        segment = args.get("segment", "all")
        period = args.get("period", "30d")
        
        metrics_data = {
            "churn_risk": {
                "high_risk_customers": random.randint(50, 200),
                "medium_risk_customers": random.randint(200, 500),
                "low_risk_customers": random.randint(1000, 5000),
                "churn_rate_percent": round(random.uniform(2, 8), 2),
                "predicted_churn_next_month": random.randint(20, 100),
                "top_churn_factors": ["Inattività", "Supporto negativo", "Prezzo competitore"]
            },
            "lifetime_value": {
                "average_ltv": round(random.uniform(500, 3000), 2),
                "median_ltv": round(random.uniform(300, 2000), 2),
                "top_10_percent_ltv": round(random.uniform(5000, 15000), 2),
                "ltv_trend": round(random.uniform(-5, 15), 1),
                "segments": [
                    {"name": "VIP", "avg_ltv": round(random.uniform(8000, 15000), 2), "count": random.randint(100, 500)},
                    {"name": "Regular", "avg_ltv": round(random.uniform(1000, 3000), 2), "count": random.randint(1000, 5000)},
                    {"name": "Occasional", "avg_ltv": round(random.uniform(200, 800), 2), "count": random.randint(2000, 10000)}
                ]
            },
            "engagement": {
                "active_users": random.randint(5000, 20000),
                "daily_active_users": random.randint(500, 3000),
                "avg_session_duration_min": round(random.uniform(5, 25), 1),
                "pages_per_session": round(random.uniform(3, 12), 1),
                "bounce_rate_percent": round(random.uniform(20, 50), 1),
                "returning_visitors_percent": round(random.uniform(30, 60), 1)
            },
            "satisfaction": {
                "nps_score": random.randint(20, 80),
                "csat_score": round(random.uniform(3.5, 4.8), 1),
                "total_reviews": random.randint(500, 5000),
                "positive_reviews_percent": round(random.uniform(70, 95), 1),
                "avg_response_time_hours": round(random.uniform(1, 24), 1),
                "resolution_rate_percent": round(random.uniform(85, 99), 1)
            },
            "purchase_frequency": {
                "avg_orders_per_customer": round(random.uniform(1.5, 5), 2),
                "avg_days_between_orders": random.randint(15, 90),
                "repeat_purchase_rate": round(random.uniform(20, 60), 1),
                "one_time_buyers_percent": round(random.uniform(30, 60), 1)
            }
        }
        
        return {
            "metric": metric,
            "segment": segment,
            "period": period,
            "data": metrics_data.get(metric, metrics_data["engagement"]),
            "generated_at": datetime.now().isoformat()
        }
    
    elif tool_name == "get_inventory_status":
        product_id = args.get("product_id")
        warehouse = args.get("warehouse")
        low_stock = args.get("low_stock_only", False)
        include_forecast = args.get("include_forecast", False)
        
        items = []
        products_to_show = [product_id] if product_id else random.sample(PRODUCTS, random.randint(3, 8))
        warehouses = [warehouse] if warehouse else ["Milano", "Roma", "Napoli"]
        
        for prod in products_to_show:
            for wh in warehouses:
                stock = random.randint(0, 500)
                if low_stock and stock > 50:
                    continue
                    
                item = {
                    "product": prod,
                    "product_id": f"SKU{random.randint(10000, 99999)}",
                    "warehouse": wh,
                    "quantity_available": stock,
                    "quantity_reserved": random.randint(0, min(stock, 50)),
                    "reorder_point": random.randint(20, 100),
                    "status": "low_stock" if stock < 50 else "in_stock" if stock > 0 else "out_of_stock",
                    "last_restock": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                }
                
                if include_forecast:
                    item["forecast"] = {
                        "expected_demand_7d": random.randint(20, 100),
                        "expected_demand_30d": random.randint(80, 400),
                        "days_until_stockout": random.randint(5, 60) if stock > 0 else 0,
                        "recommended_reorder": random.randint(100, 500)
                    }
                
                items.append(item)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(items),
            "low_stock_count": sum(1 for i in items if i["status"] == "low_stock"),
            "out_of_stock_count": sum(1 for i in items if i["status"] == "out_of_stock"),
            "items": items
        }
    
    elif tool_name == "create_dashboard_widget":
        widget_id = f"widget_{random.randint(10000, 99999)}"
        return {
            "status": "created",
            "widget": {
                "id": widget_id,
                "type": args.get("widget_type"),
                "title": args.get("title"),
                "data_source": args.get("data_source"),
                "refresh_interval": args.get("refresh_interval_minutes", 60),
                "created_at": datetime.now().isoformat()
            },
            "preview_url": f"https://dashboard.example.com/widget/{widget_id}/preview",
            "message": f"Widget '{args.get('title')}' creato con successo"
        }
    
    elif tool_name == "export_report":
        export_id = f"export_{random.randint(10000, 99999)}"
        file_format = args.get("format", "xlsx")
        
        return {
            "status": "processing",
            "export_id": export_id,
            "report_type": args.get("report_type"),
            "format": file_format,
            "estimated_completion_seconds": random.randint(5, 60),
            "download_url": f"https://reports.example.com/download/{export_id}.{file_format}",
            "email_notification": args.get("email_to") is not None,
            "message": f"Report in elaborazione. Riceverai il link per il download a breve."
        }
    
    return {"error": f"Unknown database tool: {tool_name}"}
