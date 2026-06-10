"""E-commerce and shopping mock tools."""

import random
from datetime import datetime, timedelta

ECOMMERCE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products in online stores",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product search query"},
                    "category": {"type": "string"},
                    "min_price": {"type": "number"},
                    "max_price": {"type": "number"},
                    "sort_by": {"type": "string", "enum": ["relevance", "price_low", "price_high", "rating", "newest"]},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get detailed information about a specific product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add a product to shopping cart",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "quantity": {"type": "integer", "default": 1}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cart",
            "description": "View current shopping cart contents",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Track the status of an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_history",
            "description": "Retrieve past orders",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                    "status": {"type": "string", "enum": ["all", "pending", "shipped", "delivered", "cancelled"]}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_coupon",
            "description": "Apply a discount coupon to the cart",
            "parameters": {
                "type": "object",
                "properties": {
                    "coupon_code": {"type": "string"}
                },
                "required": ["coupon_code"]
            }
        }
    },
]

# Mock data
PRODUCT_CATEGORIES = ["Elettronica", "Abbigliamento", "Casa", "Sport", "Libri", "Bellezza", "Giochi"]

PRODUCTS = {
    "elettronica": [
        ("iPhone 15 Pro", 1199, "Smartphone Apple di ultima generazione"),
        ("Samsung Galaxy S24", 899, "Smartphone Samsung con AI"),
        ("MacBook Air M3", 1299, "Laptop Apple leggero e potente"),
        ("AirPods Pro 2", 279, "Auricolari wireless con cancellazione rumore"),
        ("iPad Pro 12.9", 1329, "Tablet professionale Apple"),
    ],
    "abbigliamento": [
        ("Giacca invernale North Face", 199, "Giacca impermeabile da montagna"),
        ("Sneakers Nike Air Max", 159, "Scarpe sportive iconiche"),
        ("Jeans Levi's 501", 99, "Jeans classici straight fit"),
        ("Felpa Adidas Originals", 79, "Felpa con cappuccio sportiva"),
    ],
    "casa": [
        ("Robot aspirapolvere Roomba", 449, "Pulizia automatica intelligente"),
        ("Friggitrice ad aria Philips", 129, "Cottura sana e veloce"),
        ("Macchina caffè De'Longhi", 299, "Espresso automatica"),
        ("Smart TV LG 55 OLED", 1199, "TV 4K con tecnologia OLED"),
    ],
}

ORDER_STATUSES = ["In elaborazione", "Spedito", "In transito", "In consegna oggi", "Consegnato"]


def execute_ecommerce_tool(tool_name: str, args: dict) -> dict:
    """Execute ecommerce mock tool."""
    
    if tool_name == "search_products":
        query = args.get("query", "")
        limit = args.get("limit", 10)
        min_price = args.get("min_price", 0)
        max_price = args.get("max_price", 10000)
        
        products = []
        all_products = []
        for cat, prods in PRODUCTS.items():
            for name, price, desc in prods:
                all_products.append((name, price, desc, cat))
        
        # Filter by query (simple substring match)
        for name, price, desc, cat in all_products:
            if min_price <= price <= max_price:
                if query.lower() in name.lower() or query.lower() in cat.lower():
                    products.append({
                        "id": f"prod_{random.randint(10000, 99999)}",
                        "name": name,
                        "price": price,
                        "currency": "EUR",
                        "category": cat,
                        "rating": round(random.uniform(3.5, 5.0), 1),
                        "reviews_count": random.randint(10, 5000),
                        "in_stock": random.random() > 0.1,
                        "prime": random.random() > 0.3
                    })
        
        # Add some generic results if needed
        while len(products) < min(limit, 5):
            products.append({
                "id": f"prod_{random.randint(10000, 99999)}",
                "name": f"{query.title()} - {random.choice(['Premium', 'Pro', 'Base', 'Plus'])}",
                "price": random.randint(20, 500),
                "currency": "EUR",
                "category": random.choice(list(PRODUCTS.keys())),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews_count": random.randint(10, 5000),
                "in_stock": True,
                "prime": random.random() > 0.3
            })
        
        # Sort
        sort_by = args.get("sort_by", "relevance")
        if sort_by == "price_low":
            products.sort(key=lambda x: x["price"])
        elif sort_by == "price_high":
            products.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "rating":
            products.sort(key=lambda x: x["rating"], reverse=True)
        
        return {
            "query": query,
            "products": products[:limit],
            "total_found": len(products),
            "filters_applied": {
                "min_price": min_price,
                "max_price": max_price,
                "category": args.get("category")
            }
        }
    
    elif tool_name == "get_product_details":
        product_id = args.get("product_id", "")
        
        # Generate detailed product info
        all_products = []
        for cat, prods in PRODUCTS.items():
            for name, price, desc in prods:
                all_products.append((name, price, desc, cat))
        
        name, price, desc, cat = random.choice(all_products)
        
        return {
            "id": product_id,
            "name": name,
            "description": desc + ". Caratteristiche premium e design moderno. Garanzia 2 anni inclusa.",
            "price": price,
            "original_price": round(price * 1.2, 2) if random.random() > 0.5 else None,
            "currency": "EUR",
            "category": cat,
            "brand": random.choice(["Apple", "Samsung", "Sony", "Nike", "Adidas", "Philips", "De'Longhi"]),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "reviews_count": random.randint(100, 10000),
            "in_stock": True,
            "stock_quantity": random.randint(5, 100),
            "delivery_estimate": f"{random.randint(1, 5)} giorni lavorativi",
            "free_shipping": price > 50,
            "return_policy": "Reso gratuito entro 30 giorni",
            "specifications": {
                "Peso": f"{random.uniform(0.1, 5):.1f} kg",
                "Dimensioni": f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)} cm",
                "Colore": random.choice(["Nero", "Bianco", "Grigio", "Blu"])
            },
            "images": [f"https://images.store.com/{product_id}_{i}.jpg" for i in range(3)]
        }
    
    elif tool_name == "add_to_cart":
        product_id = args.get("product_id", "")
        quantity = args.get("quantity", 1)
        
        return {
            "status": "added",
            "product_id": product_id,
            "quantity": quantity,
            "cart_total_items": random.randint(1, 5) + quantity,
            "message": f"Prodotto aggiunto al carrello ({quantity} {'unità' if quantity > 1 else 'unità'})"
        }
    
    elif tool_name == "get_cart":
        # Generate random cart items
        items = []
        total = 0
        for i in range(random.randint(1, 4)):
            all_products = []
            for cat, prods in PRODUCTS.items():
                for name, price, desc in prods:
                    all_products.append((name, price, cat))
            
            name, price, cat = random.choice(all_products)
            qty = random.randint(1, 2)
            items.append({
                "id": f"prod_{random.randint(10000, 99999)}",
                "name": name,
                "price": price,
                "quantity": qty,
                "subtotal": price * qty
            })
            total += price * qty
        
        return {
            "items": items,
            "items_count": sum(i["quantity"] for i in items),
            "subtotal": round(total, 2),
            "shipping": 0 if total > 50 else 4.99,
            "total": round(total + (0 if total > 50 else 4.99), 2),
            "currency": "EUR",
            "free_shipping_threshold": 50
        }
    
    elif tool_name == "track_order":
        order_id = args.get("order_id", "")
        
        status_idx = random.randint(0, len(ORDER_STATUSES) - 1)
        
        history = []
        for i in range(status_idx + 1):
            history.append({
                "status": ORDER_STATUSES[i],
                "timestamp": (datetime.now() - timedelta(days=status_idx - i)).isoformat(),
                "location": random.choice(["Milano", "Bologna", "Roma", "Centro smistamento"]) if i > 0 else "Magazzino"
            })
        
        return {
            "order_id": order_id,
            "current_status": ORDER_STATUSES[status_idx],
            "carrier": random.choice(["DHL", "UPS", "BRT", "GLS", "Poste Italiane"]),
            "tracking_number": f"{random.choice(['DHL', 'UPS', 'BRT'])}{random.randint(100000000, 999999999)}",
            "estimated_delivery": (datetime.now() + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d"),
            "delivery_address": f"Via Roma {random.randint(1, 200)}, Milano",
            "history": history
        }
    
    elif tool_name == "get_order_history":
        limit = args.get("limit", 10)
        status_filter = args.get("status", "all")
        
        orders = []
        for i in range(min(limit, random.randint(3, 8))):
            status = random.choice(["delivered", "shipped", "pending"]) if status_filter == "all" else status_filter
            orders.append({
                "order_id": f"ORD{random.randint(10000000, 99999999)}",
                "date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "status": status,
                "total": round(random.uniform(20, 500), 2),
                "items_count": random.randint(1, 5),
                "tracking_available": status != "pending"
            })
        
        orders.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "orders": orders,
            "total_orders": len(orders)
        }
    
    elif tool_name == "apply_coupon":
        code = args.get("coupon_code", "").upper()
        
        # Simulate coupon validation
        if code in ["WELCOME10", "SCONTO20", "ESTATE25", "BLACKFRIDAY"]:
            discount = {"WELCOME10": 10, "SCONTO20": 20, "ESTATE25": 25, "BLACKFRIDAY": 30}.get(code, 10)
            return {
                "status": "applied",
                "coupon_code": code,
                "discount_percent": discount,
                "message": f"Coupon applicato! Sconto del {discount}% sul totale"
            }
        else:
            return {
                "status": "invalid",
                "coupon_code": code,
                "message": "Codice coupon non valido o scaduto"
            }
    
    return {"error": f"Unknown ecommerce tool: {tool_name}"}
