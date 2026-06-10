"""Knowledge-base / document-assistant tools - English version."""

KNOWLEDGE_BASE_TOOLS = [
    # ==================== DOCUMENT SUMMARY VARIATIONS ====================
    {
        "type": "function",
        "function": {
            "name": "document_summary",
            "description": "Generate a comprehensive summary of the entire uploaded document using the user's instructions. Useful whenever the user asks for a summary of their uploaded document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_name": {"type": "string", "description": "Name of the document to summarize"}
                },
                "required": ["document_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": "Create a summary of the specified document based on user requirements. Use this when the user wants an overview of the document content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "The name of the file to be summarized"}
                },
                "required": ["file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_doc_summary",
            "description": "Produces a complete summary of the uploaded file following the user's guidelines. Ideal for getting an overview of lengthy documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {"type": "string", "description": "Document filename to process"}
                },
                "required": ["doc_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_document_overview",
            "description": "Extracts and provides a high-level overview of the entire document. Best used when the user needs a quick understanding of the document's main points.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the uploaded file"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file_summary",
            "description": "Analyzes the document and generates a condensed summary capturing the key information. Perfect for lengthy reports or documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The file to summarize"}
                },
                "required": ["file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_document_summary",
            "description": "Reads through the entire document and extracts a comprehensive summary. Use when the user wants to understand the document without reading it fully.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_document": {"type": "string", "description": "Source document name"}
                },
                "required": ["source_document"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "produce_summary",
            "description": "Creates an informative summary from the uploaded document content. Helpful when users request a recap or brief of their file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document": {"type": "string", "description": "Document to be processed"}
                },
                "required": ["document"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "doc_overview",
            "description": "Provides a summarized view of the document highlighting main topics and conclusions. Suitable for any document summary request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_file": {"type": "string", "description": "File name of the document"}
                },
                "required": ["doc_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_summary_generator",
            "description": "Automatically generates a summary based on the full content of the specified document. Great for understanding documents quickly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Input file name to summarize"}
                },
                "required": ["input_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_uploaded_doc",
            "description": "Takes the uploaded document and produces a detailed yet concise summary following user instructions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uploaded_document": {"type": "string", "description": "Name of the uploaded document"}
                },
                "required": ["uploaded_document"]
            }
        }
    },
    # ==================== GET PAGE CONTENT VARIATIONS ====================
    {
        "type": "function",
        "function": {
            "name": "get_page_content",
            "description": "Returns the content of a specific page from the document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_name": {"type": "string", "description": "Name of the document"},
                    "page_number": {"type": "integer", "description": "Page number requested by the user", "minimum": 1}
                },
                "required": ["document_name", "page_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_page",
            "description": "Reads and returns the text content from a specified page in the document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "The document file name"},
                    "page": {"type": "integer", "description": "The page number to read", "minimum": 1}
                },
                "required": ["file_name", "page"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page_content",
            "description": "Fetches the content of a particular page from the uploaded document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_name": {"type": "string", "description": "Document name"},
                    "page_num": {"type": "integer", "description": "Number of the page to fetch", "minimum": 1}
                },
                "required": ["doc_name", "page_num"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_page",
            "description": "Extracts and returns the content from a single page of the document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file"},
                    "page_index": {"type": "integer", "description": "Index of the page (1-based)", "minimum": 1}
                },
                "required": ["filename", "page_index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_specific_page",
            "description": "Retrieves the text of a specific page from the document. Useful when the user wants to see a particular page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The document file"},
                    "target_page": {"type": "integer", "description": "The target page number", "minimum": 1}
                },
                "required": ["file", "target_page"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_page_text",
            "description": "Retrieves the textual content from the specified page number in the document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_document": {"type": "string", "description": "Source document name"},
                    "page_no": {"type": "integer", "description": "Page number to retrieve", "minimum": 1}
                },
                "required": ["source_document", "page_no"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "show_page",
            "description": "Displays the content of a requested page from the document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document": {"type": "string", "description": "The document to read from"},
                    "page_to_show": {"type": "integer", "description": "Page number to display", "minimum": 1}
                },
                "required": ["document", "page_to_show"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "page_content_reader",
            "description": "Reads a specific page and returns its full content. Use when user asks about a particular page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_file": {"type": "string", "description": "Document file name"},
                    "requested_page": {"type": "integer", "description": "The requested page number", "minimum": 1}
                },
                "required": ["doc_file", "requested_page"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_doc_page",
            "description": "Gets the content of a single page from the specified document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Input document file"},
                    "pg_number": {"type": "integer", "description": "Page number (starting from 1)", "minimum": 1}
                },
                "required": ["input_file", "pg_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_page_content",
            "description": "Loads and returns the content from a designated page in the uploaded document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uploaded_document": {"type": "string", "description": "Uploaded document name"},
                    "page_id": {"type": "integer", "description": "Page identifier (number)", "minimum": 1}
                },
                "required": ["uploaded_document", "page_id"]
            }
        }
    },
]
