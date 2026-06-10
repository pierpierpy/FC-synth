"""Government services and public administration mock tools."""

import random
from datetime import datetime, timedelta
from .utils import parse_date_flexible

GOVERNMENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_tax_status",
            "description": "Check tax payment status and deadlines",
            "parameters": {
                "type": "object",
                "properties": {
                    "fiscal_code": {"type": "string", "description": "Codice fiscale"},
                    "tax_year": {"type": "integer"},
                    "tax_type": {"type": "string", "enum": ["IRPEF", "IVA", "IMU", "TARI", "all"]}
                },
                "required": ["fiscal_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_public_office_appointment",
            "description": "Book an appointment at public offices (Comune, ASL, INPS, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "office_type": {"type": "string", "enum": ["comune", "anagrafe", "asl", "inps", "agenzia_entrate", "motorizzazione", "prefettura"]},
                    "service": {"type": "string", "description": "Specific service needed"},
                    "city": {"type": "string"},
                    "preferred_date": {"type": "string"},
                    "preferred_time": {"type": "string", "enum": ["morning", "afternoon", "any"]}
                },
                "required": ["office_type", "service", "city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_document_status",
            "description": "Check status of document requests (passport, ID, permits)",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_type": {"type": "string", "enum": ["passaporto", "carta_identita", "patente", "permesso_soggiorno", "certificato"]},
                    "request_id": {"type": "string"},
                    "fiscal_code": {"type": "string"}
                },
                "required": ["document_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_public_transport_info",
            "description": "Get public transport information (subscriptions, fines, schedules)",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "info_type": {"type": "string", "enum": ["subscriptions", "fines", "schedules", "disruptions", "prices"]},
                    "transport_type": {"type": "string", "enum": ["metro", "bus", "tram", "train", "all"]}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_certificate",
            "description": "Request official certificates online",
            "parameters": {
                "type": "object",
                "properties": {
                    "certificate_type": {"type": "string", "enum": ["nascita", "residenza", "stato_famiglia", "matrimonio", "esistenza_in_vita", "carichi_pendenti", "casellario_giudiziale"]},
                    "delivery_method": {"type": "string", "enum": ["digital", "postal", "pickup"]},
                    "urgency": {"type": "string", "enum": ["standard", "urgent"]},
                    "copies": {"type": "integer", "default": 1}
                },
                "required": ["certificate_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_pension_status",
            "description": "Check pension contributions and estimated retirement",
            "parameters": {
                "type": "object",
                "properties": {
                    "fiscal_code": {"type": "string"},
                    "include_simulation": {"type": "boolean", "default": True, "description": "Include retirement simulation"},
                    "retirement_age": {"type": "integer", "description": "Age for simulation"}
                },
                "required": ["fiscal_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pay_government_fee",
            "description": "Pay government fees and taxes online",
            "parameters": {
                "type": "object",
                "properties": {
                    "fee_type": {"type": "string", "enum": ["bollo_auto", "multa", "tassa_rifiuti", "contributi", "marca_bollo"]},
                    "amount": {"type": "number"},
                    "reference_number": {"type": "string"},
                    "payment_method": {"type": "string", "enum": ["carta", "bonifico", "pagoPA"]}
                },
                "required": ["fee_type", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_vehicle_status",
            "description": "Check vehicle registration, taxes, and insurance status",
            "parameters": {
                "type": "object",
                "properties": {
                    "plate_number": {"type": "string"},
                    "check_type": {"type": "string", "enum": ["bollo", "revisione", "assicurazione", "proprietario", "all"]}
                },
                "required": ["plate_number"]
            }
        }
    },
]

# Mock data
PUBLIC_OFFICES = {
    "comune": {"name": "Comune", "services": ["Certificati", "Anagrafe", "Stato Civile", "Tributi"]},
    "anagrafe": {"name": "Anagrafe", "services": ["Cambio residenza", "Carta identità", "Certificati"]},
    "asl": {"name": "ASL", "services": ["Prenotazione visite", "Vaccinazioni", "Scelta medico"]},
    "inps": {"name": "INPS", "services": ["Pensione", "Disoccupazione", "Bonus", "Contributi"]},
    "agenzia_entrate": {"name": "Agenzia delle Entrate", "services": ["Dichiarazioni", "Rimborsi", "Codice fiscale"]},
}


def execute_government_tool(tool_name: str, args: dict) -> dict:
    """Execute government services mock tool."""
    
    if tool_name == "check_tax_status":
        fiscal_code = args.get("fiscal_code", "")
        tax_year = args.get("tax_year", datetime.now().year)
        tax_type = args.get("tax_type", "all")
        
        taxes = {}
        tax_types = ["IRPEF", "IVA", "IMU", "TARI"] if tax_type == "all" else [tax_type]
        
        for tax in tax_types:
            paid = random.random() > 0.3
            amount = random.randint(100, 5000)
            taxes[tax] = {
                "year": tax_year,
                "amount_due": amount,
                "amount_paid": amount if paid else random.randint(0, amount - 1),
                "status": "pagato" if paid else random.choice(["da_pagare", "scaduto", "rateizzato"]),
                "next_deadline": (datetime.now() + timedelta(days=random.randint(10, 90))).strftime("%Y-%m-%d"),
                "installments": random.randint(1, 4) if not paid else None
            }
        
        return {
            "fiscal_code": fiscal_code[:6] + "****" + fiscal_code[-4:] if len(fiscal_code) >= 10 else "****",
            "tax_year": tax_year,
            "taxes": taxes,
            "total_due": sum(t["amount_due"] for t in taxes.values()),
            "total_paid": sum(t["amount_paid"] for t in taxes.values()),
            "alerts": [
                "Scadenza IMU: " + (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
            ] if random.random() > 0.5 else []
        }
    
    elif tool_name == "book_public_office_appointment":
        office_type = args.get("office_type", "comune")
        service = args.get("service", "")
        city = args.get("city", "Milano")
        preferred_date_str = args.get("preferred_date", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        
        booking_id = f"PA{random.randint(100000, 999999)}"
        
        # Generate available slots
        available_dates = []
        base_date = parse_date_flexible(preferred_date_str)
        for i in range(5):
            slot_date = base_date + timedelta(days=i)
            if slot_date.weekday() < 5:  # Weekdays only
                available_dates.append({
                    "date": slot_date.strftime("%Y-%m-%d"),
                    "slots": [f"{h}:{m:02d}" for h in range(9, 13) for m in [0, 30] if random.random() > 0.4]
                })
        
        # Assign first available slot
        assigned_slot = None
        for date_info in available_dates:
            if date_info["slots"]:
                assigned_slot = {"date": date_info["date"], "time": date_info["slots"][0]}
                break
        
        office_info = PUBLIC_OFFICES.get(office_type, {"name": office_type.title(), "services": [service]})
        
        return {
            "status": "confermato" if assigned_slot else "in_attesa",
            "booking": {
                "id": booking_id,
                "office": office_info["name"],
                "office_type": office_type,
                "service": service,
                "date": assigned_slot["date"] if assigned_slot else "Da assegnare",
                "time": assigned_slot["time"] if assigned_slot else "Da assegnare",
                "ticket_number": f"{office_type.upper()[:3]}{random.randint(100, 999)}"
            },
            "location": {
                "address": f"Via {random.choice(['Roma', 'Milano', 'Garibaldi', 'Mazzini'])}, {random.randint(1, 100)}, {city}",
                "floor": random.choice(["Piano terra", "1° piano", "2° piano"]),
                "room": f"Sportello {random.randint(1, 20)}"
            },
            "required_documents": [
                "Documento di identità",
                "Codice fiscale",
                "Modulo di richiesta compilato"
            ],
            "qr_code": f"https://pa.gov.it/booking/{booking_id}/qr",
            "cancellation_allowed_until": (parse_date_flexible(assigned_slot["date"]) - timedelta(days=1)).strftime("%Y-%m-%d") if assigned_slot else None
        }
    
    elif tool_name == "check_document_status":
        document_type = args.get("document_type", "passaporto")
        request_id = args.get("request_id", f"REQ{random.randint(100000, 999999)}")
        
        statuses = ["in_lavorazione", "pronto_ritiro", "spedito", "consegnato", "in_attesa_documenti"]
        status = random.choice(statuses)
        
        doc_names = {
            "passaporto": "Passaporto",
            "carta_identita": "Carta d'Identità Elettronica",
            "patente": "Patente di Guida",
            "permesso_soggiorno": "Permesso di Soggiorno",
            "certificato": "Certificato"
        }
        
        result = {
            "document_type": doc_names.get(document_type, document_type),
            "request_id": request_id,
            "status": status,
            "status_description": {
                "in_lavorazione": "Pratica in fase di elaborazione",
                "pronto_ritiro": "Documento pronto per il ritiro",
                "spedito": "Documento spedito",
                "consegnato": "Documento consegnato",
                "in_attesa_documenti": "In attesa di documentazione integrativa"
            }[status],
            "request_date": (datetime.now() - timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
            "estimated_completion": (datetime.now() + timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d") if status in ["in_lavorazione", "in_attesa_documenti"] else None,
            "last_update": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat()
        }
        
        if status == "pronto_ritiro":
            result["pickup_location"] = f"Ufficio {doc_names.get(document_type, 'Documenti')}, Via Roma 123"
            result["pickup_deadline"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        elif status == "spedito":
            result["tracking_number"] = f"IT{random.randint(1000000000, 9999999999)}IT"
            result["carrier"] = "Poste Italiane"
        
        return result
    
    elif tool_name == "get_public_transport_info":
        city = args.get("city", "Milano")
        info_type = args.get("info_type", "prices")
        transport_type = args.get("transport_type", "all")
        
        if info_type == "subscriptions":
            return {
                "city": city,
                "subscriptions": [
                    {"name": "Abbonamento Mensile", "price": 39.00, "validity": "30 giorni", "zones": "Urbano"},
                    {"name": "Abbonamento Annuale", "price": 330.00, "validity": "365 giorni", "zones": "Urbano"},
                    {"name": "Abbonamento Studenti", "price": 22.00, "validity": "30 giorni", "zones": "Urbano", "requirements": "Iscrizione universitaria"},
                    {"name": "Over 65", "price": 20.00, "validity": "30 giorni", "zones": "Urbano", "requirements": "Età > 65 anni"},
                ],
                "payment_methods": ["Carta di credito", "Bonifico", "App mobile"],
                "purchase_locations": ["Edicole", "Stazioni metro", "App ufficiale"]
            }
        elif info_type == "fines":
            return {
                "city": city,
                "pending_fines": [
                    {
                        "id": f"MULTA{random.randint(10000, 99999)}",
                        "date": (datetime.now() - timedelta(days=random.randint(5, 60))).strftime("%Y-%m-%d"),
                        "reason": random.choice(["Mancanza titolo di viaggio", "Titolo non valido", "Zona non coperta"]),
                        "amount": random.choice([50.00, 75.00, 100.00]),
                        "reduced_amount": random.choice([35.00, 50.00, 75.00]),
                        "payment_deadline": (datetime.now() + timedelta(days=random.randint(10, 30))).strftime("%Y-%m-%d"),
                        "status": random.choice(["da_pagare", "in_scadenza"])
                    }
                ] if random.random() > 0.6 else [],
                "total_pending": random.choice([0, 50.00, 100.00, 150.00])
            }
        elif info_type == "disruptions":
            return {
                "city": city,
                "active_disruptions": [
                    {
                        "line": random.choice(["M1", "M2", "M3", "Tram 15", "Bus 54"]),
                        "type": random.choice(["Lavori in corso", "Guasto tecnico", "Sciopero parziale"]),
                        "affected_stations": [f"Stazione {i}" for i in range(random.randint(2, 5))],
                        "alternative": "Utilizzare bus sostitutivi",
                        "estimated_end": (datetime.now() + timedelta(hours=random.randint(2, 48))).isoformat()
                    }
                ] if random.random() > 0.5 else [],
                "planned_works": [
                    {
                        "line": "M2",
                        "dates": f"{(datetime.now() + timedelta(days=7)).strftime('%d/%m')} - {(datetime.now() + timedelta(days=14)).strftime('%d/%m')}",
                        "description": "Lavori di manutenzione straordinaria"
                    }
                ] if random.random() > 0.7 else []
            }
        else:  # prices
            return {
                "city": city,
                "tickets": [
                    {"name": "Biglietto singolo", "price": 2.20, "validity": "90 minuti"},
                    {"name": "Biglietto giornaliero", "price": 7.60, "validity": "24 ore"},
                    {"name": "Carnet 10 viaggi", "price": 18.00, "validity": "90 minuti ciascuno"},
                ],
                "last_update": datetime.now().isoformat()
            }
    
    elif tool_name == "request_certificate":
        certificate_type = args.get("certificate_type", "residenza")
        delivery_method = args.get("delivery_method", "digital")
        urgency = args.get("urgency", "standard")
        copies = args.get("copies", 1)
        
        request_id = f"CERT{random.randint(100000, 999999)}"
        
        cert_names = {
            "nascita": "Certificato di Nascita",
            "residenza": "Certificato di Residenza",
            "stato_famiglia": "Stato di Famiglia",
            "matrimonio": "Certificato di Matrimonio",
            "esistenza_in_vita": "Certificato di Esistenza in Vita",
            "carichi_pendenti": "Certificato Carichi Pendenti",
            "casellario_giudiziale": "Casellario Giudiziale"
        }
        
        base_price = random.uniform(5, 20)
        urgency_fee = 10 if urgency == "urgent" else 0
        
        return {
            "status": "richiesta_accettata",
            "request": {
                "id": request_id,
                "certificate": cert_names.get(certificate_type, certificate_type),
                "copies": copies,
                "delivery_method": delivery_method,
                "urgency": urgency
            },
            "costs": {
                "certificate_fee": round(base_price, 2),
                "stamp_duty": 16.00 if certificate_type in ["carichi_pendenti", "casellario_giudiziale"] else 0,
                "urgency_fee": urgency_fee,
                "postal_fee": 5.00 if delivery_method == "postal" else 0,
                "total": round(base_price + urgency_fee + (16.00 if certificate_type in ["carichi_pendenti", "casellario_giudiziale"] else 0) + (5.00 if delivery_method == "postal" else 0), 2)
            },
            "estimated_delivery": {
                "digital": "2-5 giorni lavorativi",
                "postal": "7-10 giorni lavorativi",
                "pickup": "3-7 giorni lavorativi"
            }[delivery_method],
            "tracking_url": f"https://comune.gov.it/certificati/{request_id}"
        }
    
    elif tool_name == "check_pension_status":
        fiscal_code = args.get("fiscal_code", "")
        include_simulation = args.get("include_simulation", True)
        
        years_contributed = random.randint(10, 35)
        
        result = {
            "fiscal_code": fiscal_code[:6] + "****" + fiscal_code[-4:] if len(fiscal_code) >= 10 else "****",
            "contributions": {
                "total_years": years_contributed,
                "total_weeks": years_contributed * 52,
                "total_amount_contributed": round(years_contributed * random.uniform(3000, 8000), 2),
                "last_contribution_date": (datetime.now() - timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d"),
                "employer": "Ultimo datore di lavoro S.r.l."
            },
            "pension_eligibility": {
                "old_age_pension": {
                    "eligible": years_contributed >= 20,
                    "minimum_age": 67,
                    "years_remaining": max(0, 67 - random.randint(40, 60))
                },
                "early_retirement": {
                    "eligible": years_contributed >= 42,
                    "years_contributed_required": 42 if random.random() > 0.5 else 41,
                    "months_remaining": max(0, (42 - years_contributed) * 12)
                }
            }
        }
        
        if include_simulation:
            retirement_age = args.get("retirement_age", 67)
            result["simulation"] = {
                "retirement_age": retirement_age,
                "estimated_monthly_gross": round(random.uniform(1200, 3500), 2),
                "estimated_monthly_net": round(random.uniform(1000, 2800), 2),
                "replacement_rate": f"{random.randint(60, 85)}%",
                "note": "Simulazione indicativa basata sulla normativa vigente"
            }
        
        return result
    
    elif tool_name == "pay_government_fee":
        fee_type = args.get("fee_type", "bollo_auto")
        amount = args.get("amount", random.uniform(50, 500))
        payment_method = args.get("payment_method", "carta")
        
        payment_id = f"PAY{random.randint(100000, 999999)}"
        
        return {
            "status": "completato",
            "payment": {
                "id": payment_id,
                "fee_type": fee_type,
                "amount": round(amount, 2),
                "commission": round(amount * 0.015, 2) if payment_method == "carta" else 0,
                "total_charged": round(amount + (amount * 0.015 if payment_method == "carta" else 0), 2),
                "payment_method": payment_method,
                "reference_number": args.get("reference_number", f"REF{random.randint(10000, 99999)}"),
                "timestamp": datetime.now().isoformat()
            },
            "receipt": {
                "number": f"RIC{random.randint(1000000, 9999999)}",
                "download_url": f"https://pa.gov.it/ricevute/{payment_id}.pdf",
                "valid_for_tax_purposes": True
            },
            "iuv": f"RF{random.randint(10, 99)}{random.randint(10000000000, 99999999999)}"
        }
    
    elif tool_name == "check_vehicle_status":
        plate_number = args.get("plate_number", "")
        check_type = args.get("check_type", "all")
        
        checks = {}
        check_types = ["bollo", "revisione", "assicurazione", "proprietario"] if check_type == "all" else [check_type]
        
        for check in check_types:
            if check == "bollo":
                expiry = datetime.now() + timedelta(days=random.randint(-30, 365))
                checks["bollo"] = {
                    "status": "valido" if expiry > datetime.now() else "scaduto",
                    "scadenza": expiry.strftime("%Y-%m-%d"),
                    "importo_annuale": round(random.uniform(150, 800), 2),
                    "regione": "Lombardia"
                }
            elif check == "revisione":
                expiry = datetime.now() + timedelta(days=random.randint(-60, 365))
                checks["revisione"] = {
                    "status": "valida" if expiry > datetime.now() else "scaduta",
                    "ultima_revisione": (datetime.now() - timedelta(days=random.randint(30, 700))).strftime("%Y-%m-%d"),
                    "prossima_scadenza": expiry.strftime("%Y-%m-%d"),
                    "esito_ultima": random.choice(["regolare", "ripetere"])
                }
            elif check == "assicurazione":
                expiry = datetime.now() + timedelta(days=random.randint(-10, 365))
                checks["assicurazione"] = {
                    "status": "attiva" if expiry > datetime.now() else "scaduta",
                    "compagnia": random.choice(["Generali", "Allianz", "UnipolSai", "AXA"]),
                    "scadenza": expiry.strftime("%Y-%m-%d"),
                    "tipo_copertura": random.choice(["RCA base", "RCA + Furto", "Kasko"])
                }
            elif check == "proprietario":
                checks["proprietario"] = {
                    "nome": "Mario Rossi",
                    "data_immatricolazione": (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d"),
                    "passaggi_proprieta": random.randint(0, 3)
                }
        
        return {
            "plate_number": plate_number.upper(),
            "vehicle_type": random.choice(["Autovettura", "Motociclo", "Autocarro"]),
            "checks": checks,
            "alerts": [
                f"Attenzione: {k} in scadenza" for k, v in checks.items() 
                if isinstance(v, dict) and v.get("status") in ["scaduto", "scaduta"]
            ]
        }
    
    return {"error": f"Unknown government tool: {tool_name}"}
