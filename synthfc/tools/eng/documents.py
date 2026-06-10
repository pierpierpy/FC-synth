"""Document and File Management mock tools."""

import random
from datetime import datetime, timedelta

DOCUMENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search through documents in cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "file_type": {"type": "string", "enum": ["all", "pdf", "docx", "xlsx", "pptx", "txt", "image"]},
                    "folder": {"type": "string", "description": "Folder path to search in"},
                    "modified_after": {"type": "string", "description": "Filter by modification date"},
                    "owner": {"type": "string", "description": "Filter by owner email"},
                    "shared_with_me": {"type": "boolean", "default": False}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_document",
            "description": "Create a new document in cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Document name"},
                    "type": {"type": "string", "enum": ["document", "spreadsheet", "presentation", "form"]},
                    "folder": {"type": "string"},
                    "template": {"type": "string", "description": "Template to use"},
                    "content": {"type": "string", "description": "Initial content"}
                },
                "required": ["name", "type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "share_document",
            "description": "Share a document with specific users or groups",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string"},
                    "share_with": {"type": "array", "items": {"type": "string"}, "description": "Email addresses"},
                    "permission": {"type": "string", "enum": ["view", "comment", "edit"]},
                    "notify": {"type": "boolean", "default": True},
                    "message": {"type": "string", "description": "Optional message to include"}
                },
                "required": ["document_id", "share_with", "permission"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_document_info",
            "description": "Get detailed information about a document",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string"},
                    "include_history": {"type": "boolean", "default": False},
                    "include_permissions": {"type": "boolean", "default": False}
                },
                "required": ["document_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_document",
            "description": "Convert document to different format",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string"},
                    "target_format": {"type": "string", "enum": ["pdf", "docx", "html", "txt", "epub"]},
                    "options": {
                        "type": "object",
                        "properties": {
                            "include_comments": {"type": "boolean"},
                            "include_images": {"type": "boolean"},
                            "page_range": {"type": "string"}
                        }
                    }
                },
                "required": ["document_id", "target_format"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_file",
            "description": "Upload a file to cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Local file path"},
                    "destination_folder": {"type": "string"},
                    "rename_to": {"type": "string"},
                    "convert_to_native": {"type": "boolean", "default": False}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Create a new folder in cloud storage",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "parent_folder": {"type": "string"},
                    "color": {"type": "string", "enum": ["blue", "red", "green", "yellow", "purple", "gray"]}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_storage_quota",
            "description": "Get cloud storage usage and quota information",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_breakdown": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
]

# Mock data
DOC_NAMES = [
    "Report Q4 2024", "Piano Marketing", "Budget Annuale", "Meeting Notes", "Proposta Progetto",
    "Contratto Servizi", "Presentazione Cliente", "Analisi Competitor", "Roadmap Prodotto",
    "Specifica Tecnica", "Manuale Utente", "Policy Aziendale", "Onboarding Guide"
]

FOLDERS = ["Documenti", "Progetti", "Condivisi", "Archivio", "Template", "HR", "Finance", "Marketing"]

USERS = [
    "mario.rossi@company.it", "laura.bianchi@company.it", "giuseppe.verdi@company.it",
    "team-marketing@company.it", "direzione@company.it"
]


def execute_document_tool(tool_name: str, args: dict) -> dict:
    """Execute document management mock tool."""
    
    if tool_name == "search_documents":
        query = args.get("query", "")
        file_type = args.get("file_type", "all")
        
        results = []
        for i in range(random.randint(3, 10)):
            doc_type = random.choice(["pdf", "docx", "xlsx", "pptx"]) if file_type == "all" else file_type
            name = random.choice(DOC_NAMES)
            
            results.append({
                "id": f"doc_{random.randint(100000, 999999)}",
                "name": f"{name}.{doc_type}",
                "type": doc_type,
                "folder": f"/{random.choice(FOLDERS)}",
                "size_bytes": random.randint(10000, 5000000),
                "size_human": f"{random.randint(10, 5000)} KB",
                "owner": random.choice(USERS),
                "modified": (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
                "shared": random.random() > 0.5,
                "starred": random.random() > 0.8,
                "match_snippet": f"...{query}... trovato nel documento..."
            })
        
        return {
            "query": query,
            "filters": {"file_type": file_type, "folder": args.get("folder")},
            "results": results,
            "total_found": len(results),
            "search_time_ms": random.randint(50, 300)
        }
    
    elif tool_name == "create_document":
        doc_id = f"doc_{random.randint(100000, 999999)}"
        doc_type = args.get("type", "document")
        
        type_extensions = {"document": "docx", "spreadsheet": "xlsx", "presentation": "pptx", "form": "form"}
        
        return {
            "status": "created",
            "document": {
                "id": doc_id,
                "name": args.get("name"),
                "type": doc_type,
                "extension": type_extensions.get(doc_type, "docx"),
                "folder": args.get("folder", "/Documenti"),
                "url": f"https://docs.example.com/d/{doc_id}",
                "edit_url": f"https://docs.example.com/d/{doc_id}/edit",
                "created_at": datetime.now().isoformat()
            },
            "message": f"Documento '{args.get('name')}' creato con successo"
        }
    
    elif tool_name == "share_document":
        doc_id = args.get("document_id")
        share_with = args.get("share_with", [])
        permission = args.get("permission", "view")
        
        return {
            "status": "shared",
            "document_id": doc_id,
            "shared_with": [
                {"email": email, "permission": permission, "status": "invited"}
                for email in share_with
            ],
            "notification_sent": args.get("notify", True),
            "share_link": f"https://docs.example.com/d/{doc_id}?share=true" if permission == "view" else None,
            "message": f"Documento condiviso con {len(share_with)} utenti"
        }
    
    elif tool_name == "get_document_info":
        doc_id = args.get("document_id")
        
        result = {
            "id": doc_id,
            "name": f"{random.choice(DOC_NAMES)}.docx",
            "type": "document",
            "folder": f"/{random.choice(FOLDERS)}",
            "size_bytes": random.randint(50000, 2000000),
            "owner": random.choice(USERS),
            "created": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            "modified": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "url": f"https://docs.example.com/d/{doc_id}",
            "starred": random.random() > 0.7,
            "trashed": False
        }
        
        if args.get("include_history", False):
            result["history"] = [
                {
                    "version": i + 1,
                    "modified_by": random.choice(USERS),
                    "modified_at": (datetime.now() - timedelta(days=i * 3)).isoformat(),
                    "changes": random.choice(["Modifiche testo", "Aggiunta immagini", "Formattazione", "Revisione"])
                }
                for i in range(random.randint(3, 8))
            ]
        
        if args.get("include_permissions", False):
            result["permissions"] = {
                "owner": random.choice(USERS),
                "editors": random.sample(USERS, random.randint(1, 3)),
                "viewers": random.sample(USERS, random.randint(0, 2)),
                "link_sharing": random.choice(["off", "anyone_with_link", "organization"])
            }
        
        return result
    
    elif tool_name == "convert_document":
        doc_id = args.get("document_id")
        target = args.get("target_format", "pdf")
        
        return {
            "status": "converted",
            "source_document_id": doc_id,
            "target_format": target,
            "converted_file": {
                "id": f"doc_{random.randint(100000, 999999)}",
                "name": f"converted_document.{target}",
                "size_bytes": random.randint(50000, 3000000),
                "download_url": f"https://docs.example.com/download/{doc_id}.{target}",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            },
            "conversion_time_ms": random.randint(500, 5000)
        }
    
    elif tool_name == "upload_file":
        file_id = f"file_{random.randint(100000, 999999)}"
        file_path = args.get("file_path", "document.pdf")
        file_name = args.get("rename_to") or file_path.split("/")[-1]
        
        return {
            "status": "uploaded",
            "file": {
                "id": file_id,
                "name": file_name,
                "folder": args.get("destination_folder", "/Uploads"),
                "size_bytes": random.randint(10000, 10000000),
                "mime_type": "application/pdf",
                "url": f"https://drive.example.com/file/{file_id}",
                "converted": args.get("convert_to_native", False)
            },
            "upload_time_ms": random.randint(500, 5000),
            "message": f"File '{file_name}' caricato con successo"
        }
    
    elif tool_name == "create_folder":
        folder_id = f"folder_{random.randint(10000, 99999)}"
        
        return {
            "status": "created",
            "folder": {
                "id": folder_id,
                "name": args.get("name"),
                "parent": args.get("parent_folder", "/"),
                "path": f"{args.get('parent_folder', '')}/{args.get('name')}",
                "color": args.get("color", "gray"),
                "url": f"https://drive.example.com/folder/{folder_id}",
                "created_at": datetime.now().isoformat()
            }
        }
    
    elif tool_name == "get_storage_quota":
        total_gb = random.choice([15, 100, 200, 2000])
        used_gb = round(random.uniform(1, total_gb * 0.8), 2)
        
        result = {
            "total_bytes": total_gb * 1024 * 1024 * 1024,
            "used_bytes": int(used_gb * 1024 * 1024 * 1024),
            "available_bytes": int((total_gb - used_gb) * 1024 * 1024 * 1024),
            "total_human": f"{total_gb} GB",
            "used_human": f"{used_gb} GB",
            "available_human": f"{round(total_gb - used_gb, 2)} GB",
            "usage_percent": round(used_gb / total_gb * 100, 1),
            "plan": "Business" if total_gb > 100 else "Personal"
        }
        
        if args.get("include_breakdown", False):
            result["breakdown"] = {
                "documents": f"{round(used_gb * 0.3, 2)} GB",
                "images": f"{round(used_gb * 0.25, 2)} GB",
                "videos": f"{round(used_gb * 0.35, 2)} GB",
                "other": f"{round(used_gb * 0.1, 2)} GB"
            }
        
        return result
    
    return {"error": f"Unknown document tool: {tool_name}"}
