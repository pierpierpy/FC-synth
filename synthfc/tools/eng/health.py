"""Health and fitness mock tools."""

import random
from datetime import datetime, timedelta

HEALTH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "log_workout",
            "description": "Log a workout or exercise session",
            "parameters": {
                "type": "object",
                "properties": {
                    "activity": {"type": "string", "description": "Type of workout (running, gym, yoga, etc.)"},
                    "duration_minutes": {"type": "integer"},
                    "calories": {"type": "integer"},
                    "notes": {"type": "string"}
                },
                "required": ["activity", "duration_minutes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fitness_stats",
            "description": "Get fitness statistics and activity summary",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "enum": ["today", "week", "month"], "default": "week"},
                    "include_heart_rate": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_meal",
            "description": "Log food intake and nutrition",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "snack"]},
                    "description": {"type": "string", "description": "Food description"},
                    "calories": {"type": "integer"},
                    "macros": {
                        "type": "object",
                        "properties": {
                            "protein": {"type": "number"},
                            "carbs": {"type": "number"},
                            "fat": {"type": "number"}
                        }
                    }
                },
                "required": ["meal_type", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_nutrition_summary",
            "description": "Get nutrition and calorie summary",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date (YYYY-MM-DD)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_water_intake",
            "description": "Log water consumption",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount_ml": {"type": "integer", "description": "Amount in milliliters"}
                },
                "required": ["amount_ml"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sleep_data",
            "description": "Get sleep tracking data",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "period": {"type": "string", "enum": ["night", "week", "month"], "default": "night"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_health_goal",
            "description": "Set a health or fitness goal",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_type": {"type": "string", "enum": ["steps", "calories", "weight", "water", "sleep", "workout"]},
                    "target": {"type": "number"},
                    "deadline": {"type": "string", "description": "Target date (YYYY-MM-DD)"}
                },
                "required": ["goal_type", "target"]
            }
        }
    },
]

# Mock data
WORKOUT_TYPES = ["Corsa", "Palestra", "Yoga", "Nuoto", "Ciclismo", "Camminata", "HIIT", "Pilates"]


def execute_health_tool(tool_name: str, args: dict) -> dict:
    """Execute health mock tool."""
    
    if tool_name == "log_workout":
        activity = args.get("activity", "Allenamento")
        duration = args.get("duration_minutes", 30)
        calories = args.get("calories", int(duration * random.uniform(5, 12)))
        
        return {
            "status": "logged",
            "workout": {
                "id": f"workout_{random.randint(10000, 99999)}",
                "activity": activity,
                "duration_minutes": duration,
                "calories_burned": calories,
                "heart_rate_avg": random.randint(100, 160),
                "heart_rate_max": random.randint(150, 190),
                "notes": args.get("notes", ""),
                "timestamp": datetime.now().isoformat()
            },
            "message": f"Allenamento registrato: {activity} per {duration} minuti ({calories} kcal)"
        }
    
    elif tool_name == "get_fitness_stats":
        period = args.get("period", "week")
        include_hr = args.get("include_heart_rate", True)
        
        multiplier = {"today": 1, "week": 7, "month": 30}.get(period, 7)
        
        result = {
            "period": period,
            "steps": {
                "total": random.randint(5000, 15000) * multiplier,
                "daily_average": random.randint(5000, 15000),
                "goal": 10000,
                "best_day": random.randint(12000, 25000)
            },
            "calories": {
                "burned": random.randint(1500, 3000) * multiplier,
                "daily_average": random.randint(1500, 3000)
            },
            "workouts": {
                "count": random.randint(1, 3) * multiplier // 7 + 1,
                "total_duration_minutes": random.randint(30, 90) * (multiplier // 7 + 1),
                "types": random.sample(WORKOUT_TYPES, min(3, random.randint(1, 5)))
            },
            "distance_km": round(random.uniform(20, 80) * (multiplier / 7), 1),
            "active_minutes": random.randint(30, 90) * multiplier
        }
        
        if include_hr:
            result["heart_rate"] = {
                "resting_avg": random.randint(55, 75),
                "max_recorded": random.randint(150, 190),
                "zones": {
                    "fat_burn": f"{random.randint(10, 30)}%",
                    "cardio": f"{random.randint(5, 20)}%",
                    "peak": f"{random.randint(0, 10)}%"
                }
            }
        
        return result
    
    elif tool_name == "log_meal":
        meal_type = args.get("meal_type", "lunch")
        description = args.get("description", "Pasto")
        calories = args.get("calories", random.randint(200, 800))
        
        meal_names = {"breakfast": "Colazione", "lunch": "Pranzo", "dinner": "Cena", "snack": "Spuntino"}
        
        return {
            "status": "logged",
            "meal": {
                "id": f"meal_{random.randint(10000, 99999)}",
                "type": meal_names.get(meal_type, meal_type),
                "description": description,
                "calories": calories,
                "macros": args.get("macros", {
                    "protein": round(random.uniform(10, 40), 1),
                    "carbs": round(random.uniform(20, 80), 1),
                    "fat": round(random.uniform(5, 30), 1)
                }),
                "timestamp": datetime.now().isoformat()
            },
            "message": f"{meal_names.get(meal_type, meal_type)} registrato: {calories} kcal"
        }
    
    elif tool_name == "get_nutrition_summary":
        date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        meals_logged = random.randint(2, 4)
        total_calories = random.randint(1200, 2500)
        
        return {
            "date": date,
            "summary": {
                "total_calories": total_calories,
                "goal_calories": 2000,
                "remaining": max(0, 2000 - total_calories),
                "macros": {
                    "protein": {"amount": random.randint(50, 120), "goal": 100, "unit": "g"},
                    "carbs": {"amount": random.randint(150, 300), "goal": 250, "unit": "g"},
                    "fat": {"amount": random.randint(40, 80), "goal": 65, "unit": "g"},
                    "fiber": {"amount": random.randint(15, 35), "goal": 30, "unit": "g"}
                },
                "meals_logged": meals_logged
            },
            "meals": [
                {"type": "Colazione", "calories": random.randint(200, 400), "time": "08:00"},
                {"type": "Pranzo", "calories": random.randint(400, 700), "time": "13:00"},
                {"type": "Cena", "calories": random.randint(400, 700), "time": "20:00"}
            ][:meals_logged]
        }
    
    elif tool_name == "log_water_intake":
        amount = args.get("amount_ml", 250)
        
        # Simulate daily total
        previous_total = random.randint(500, 2000)
        new_total = previous_total + amount
        goal = 2500
        
        return {
            "status": "logged",
            "entry": {
                "amount_ml": amount,
                "timestamp": datetime.now().isoformat()
            },
            "daily_total_ml": new_total,
            "goal_ml": goal,
            "remaining_ml": max(0, goal - new_total),
            "percentage": min(100, round(new_total / goal * 100)),
            "message": f"Acqua registrata: {amount}ml. Totale oggi: {new_total}ml ({round(new_total / goal * 100)}%)"
        }
    
    elif tool_name == "get_sleep_data":
        period = args.get("period", "night")
        
        if period == "night":
            bedtime = datetime.now().replace(hour=23, minute=random.randint(0, 59))
            wake_time = datetime.now().replace(hour=7, minute=random.randint(0, 59))
            duration = random.uniform(6, 9)
            
            return {
                "date": args.get("date", datetime.now().strftime("%Y-%m-%d")),
                "bedtime": bedtime.strftime("%H:%M"),
                "wake_time": wake_time.strftime("%H:%M"),
                "duration_hours": round(duration, 1),
                "quality_score": random.randint(60, 95),
                "stages": {
                    "deep": f"{random.randint(15, 25)}%",
                    "light": f"{random.randint(40, 55)}%",
                    "rem": f"{random.randint(15, 25)}%",
                    "awake": f"{random.randint(2, 10)}%"
                },
                "interruptions": random.randint(0, 3),
                "heart_rate_avg": random.randint(50, 65),
                "snoring_minutes": random.randint(0, 30)
            }
        else:
            days = 7 if period == "week" else 30
            return {
                "period": period,
                "average_duration_hours": round(random.uniform(6.5, 8), 1),
                "average_quality_score": random.randint(65, 85),
                "average_bedtime": "23:30",
                "average_wake_time": "07:15",
                "consistency_score": random.randint(50, 90),
                "best_night": (datetime.now() - timedelta(days=random.randint(1, days))).strftime("%Y-%m-%d"),
                "worst_night": (datetime.now() - timedelta(days=random.randint(1, days))).strftime("%Y-%m-%d"),
                "total_nights_tracked": days
            }
    
    elif tool_name == "set_health_goal":
        goal_type = args.get("goal_type", "steps")
        target = args.get("target", 10000)
        deadline = args.get("deadline")
        
        goal_units = {
            "steps": "passi/giorno",
            "calories": "kcal/giorno",
            "weight": "kg",
            "water": "ml/giorno",
            "sleep": "ore/notte",
            "workout": "sessioni/settimana"
        }
        
        return {
            "status": "created",
            "goal": {
                "id": f"goal_{random.randint(1000, 9999)}",
                "type": goal_type,
                "target": target,
                "unit": goal_units.get(goal_type, ""),
                "deadline": deadline,
                "created_at": datetime.now().isoformat(),
                "current_progress": random.randint(0, int(target * 0.7))
            },
            "message": f"Obiettivo impostato: {target} {goal_units.get(goal_type, '')}"
        }
    
    return {"error": f"Unknown health tool: {tool_name}"}
