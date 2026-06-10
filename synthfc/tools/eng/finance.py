"""Finance-related mock tools."""

import random
from datetime import datetime, timedelta

FINANCE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get current stock price and basic info for a ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, MSFT)"},
                    "include_history": {"type": "boolean", "default": False}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get currency exchange rate between two currencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string", "description": "Source currency code (e.g., EUR, USD)"},
                    "to_currency": {"type": "string", "description": "Target currency code"},
                    "amount": {"type": "number", "default": 1}
                },
                "required": ["from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crypto_price",
            "description": "Get cryptocurrency price and market data",
            "parameters": {
                "type": "object",
                "properties": {
                    "coin": {"type": "string", "description": "Cryptocurrency name or symbol (e.g., bitcoin, BTC)"},
                    "currency": {"type": "string", "default": "EUR"}
                },
                "required": ["coin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bank_balance",
            "description": "Get current bank account balance and recent transactions",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "Account identifier"},
                    "include_transactions": {"type": "boolean", "default": True}
                },
                "required": ["account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_money",
            "description": "Transfer money between accounts or to another person",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_account": {"type": "string"},
                    "to_account": {"type": "string", "description": "Destination account or IBAN"},
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "default": "EUR"},
                    "description": {"type": "string"}
                },
                "required": ["from_account", "to_account", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_news",
            "description": "Get latest financial market news and analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["stocks", "crypto", "forex", "commodities", "general"]},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": []
            }
        }
    },
]

# Mock data
STOCKS = {
    "AAPL": ("Apple Inc.", 175.50),
    "MSFT": ("Microsoft Corporation", 378.90),
    "GOOGL": ("Alphabet Inc.", 141.25),
    "AMZN": ("Amazon.com Inc.", 178.30),
    "TSLA": ("Tesla Inc.", 248.50),
    "META": ("Meta Platforms Inc.", 505.75),
    "NVDA": ("NVIDIA Corporation", 875.40),
    "ENI": ("Eni S.p.A.", 14.85),
    "ISP": ("Intesa Sanpaolo", 3.42),
    "UCG": ("UniCredit", 28.75),
}

CRYPTOS = {
    "bitcoin": ("BTC", 42500),
    "ethereum": ("ETH", 2250),
    "solana": ("SOL", 98),
    "cardano": ("ADA", 0.52),
    "ripple": ("XRP", 0.58),
}

EXCHANGE_RATES = {
    ("EUR", "USD"): 1.09,
    ("USD", "EUR"): 0.92,
    ("EUR", "GBP"): 0.86,
    ("GBP", "EUR"): 1.16,
    ("EUR", "CHF"): 0.95,
    ("USD", "JPY"): 148.5,
}


def execute_finance_tool(tool_name: str, args: dict) -> dict:
    """Execute finance mock tool."""
    
    if tool_name == "get_stock_price":
        symbol = args.get("symbol", "AAPL").upper()
        if symbol in STOCKS:
            name, base_price = STOCKS[symbol]
        else:
            name = f"{symbol} Corp."
            base_price = random.uniform(10, 500)
        
        price = round(base_price * random.uniform(0.97, 1.03), 2)
        change = round(random.uniform(-5, 5), 2)
        
        result = {
            "symbol": symbol,
            "name": name,
            "price": price,
            "currency": "USD",
            "change": change,
            "change_percent": round(change / price * 100, 2),
            "volume": random.randint(1000000, 50000000),
            "market_cap": f"{random.randint(10, 3000)}B",
            "timestamp": datetime.now().isoformat()
        }
        
        if args.get("include_history", False):
            result["history_7d"] = [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "close": round(base_price * random.uniform(0.95, 1.05), 2)}
                for i in range(7, 0, -1)
            ]
        return result
    
    elif tool_name == "get_exchange_rate":
        from_curr = args.get("from_currency", "EUR").upper()
        to_curr = args.get("to_currency", "USD").upper()
        amount = args.get("amount", 1)
        
        rate = EXCHANGE_RATES.get((from_curr, to_curr), random.uniform(0.5, 2.0))
        rate = round(rate * random.uniform(0.99, 1.01), 4)
        
        return {
            "from": from_curr,
            "to": to_curr,
            "rate": rate,
            "amount": amount,
            "converted": round(amount * rate, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "get_crypto_price":
        coin = args.get("coin", "bitcoin").lower()
        currency = args.get("currency", "EUR").upper()
        
        if coin in CRYPTOS or coin in [v[0].lower() for v in CRYPTOS.values()]:
            if coin in CRYPTOS:
                symbol, base_price = CRYPTOS[coin]
            else:
                for k, v in CRYPTOS.items():
                    if v[0].lower() == coin:
                        coin = k
                        symbol, base_price = v
                        break
        else:
            symbol = coin.upper()[:4]
            base_price = random.uniform(0.1, 1000)
        
        price = round(base_price * random.uniform(0.95, 1.05), 2)
        
        return {
            "coin": coin,
            "symbol": symbol,
            "price": price,
            "currency": currency,
            "change_24h": round(random.uniform(-10, 10), 2),
            "volume_24h": f"${random.randint(100, 5000)}M",
            "market_cap": f"${random.randint(1, 800)}B",
            "circulating_supply": f"{random.randint(10, 500)}M",
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "get_bank_balance":
        account_id = args.get("account_id", "main")
        balance = round(random.uniform(500, 25000), 2)
        
        result = {
            "account_id": account_id,
            "account_type": random.choice(["Conto corrente", "Conto deposito", "Conto business"]),
            "balance": balance,
            "currency": "EUR",
            "available": round(balance * 0.95, 2),
            "iban": f"IT60X0542811101000000{random.randint(100000, 999999)}",
            "last_update": datetime.now().isoformat()
        }
        
        if args.get("include_transactions", True):
            transactions = []
            for i in range(5):
                is_income = random.random() > 0.6
                transactions.append({
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "description": random.choice([
                        "Stipendio", "Bonifico ricevuto", "Pagamento bolletta", 
                        "Acquisto online", "Prelievo ATM", "Addebito carta"
                    ]) if not is_income else random.choice(["Stipendio", "Bonifico ricevuto", "Rimborso"]),
                    "amount": round(random.uniform(10, 500) * (1 if is_income else -1), 2),
                    "type": "credit" if is_income else "debit"
                })
            result["recent_transactions"] = transactions
        
        return result
    
    elif tool_name == "transfer_money":
        amount = args.get("amount", 0)
        return {
            "status": "completed",
            "transaction_id": f"TXN{random.randint(100000000, 999999999)}",
            "from_account": args.get("from_account"),
            "to_account": args.get("to_account"),
            "amount": amount,
            "currency": args.get("currency", "EUR"),
            "description": args.get("description", ""),
            "fee": round(min(amount * 0.001, 2.50), 2),
            "execution_date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }
    
    elif tool_name == "get_market_news":
        category = args.get("category", "general")
        limit = args.get("limit", 5)
        
        headlines = {
            "stocks": [
                "FTSE MIB chiude in rialzo trainato dal settore bancario",
                "Wall Street: record storico per l'S&P 500",
                "Stellantis annuncia investimenti in Italia",
                "Enel: trimestrale sopra le attese, titolo in rally",
                "Ferrari supera i 400€ per azione"
            ],
            "crypto": [
                "Bitcoin supera i 45.000$: nuovo massimo annuale",
                "Ethereum si prepara all'aggiornamento Dencun",
                "La SEC approva gli ETF spot su Bitcoin",
                "Solana guida il rally delle altcoin",
                "Regolamentazione crypto: nuove norme UE in arrivo"
            ],
            "general": [
                "BCE mantiene i tassi invariati, mercati in attesa",
                "Inflazione in calo nell'Eurozona",
                "Mercati asiatici in rialzo dopo dati cinesi",
                "Petrolio in calo su timori domanda globale",
                "Spread BTP-Bund stabile a 165 punti"
            ]
        }
        
        news_pool = headlines.get(category, headlines["general"])
        
        return {
            "category": category,
            "news": [
                {
                    "title": random.choice(news_pool),
                    "source": random.choice(["Il Sole 24 Ore", "Milano Finanza", "Reuters", "Bloomberg", "ANSA"]),
                    "time": f"{random.randint(1, 12)}h fa",
                    "url": f"https://news.example.com/{random.randint(1000, 9999)}"
                }
                for _ in range(min(limit, len(news_pool)))
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    return {"error": f"Unknown finance tool: {tool_name}"}
