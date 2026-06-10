"""Developer and code assistance mock tools."""

import random
from datetime import datetime, timedelta

CODE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_code",
            "description": "Execute code in a sandbox environment",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "enum": ["python", "javascript", "typescript", "bash", "sql", "rust", "go"]},
                    "code": {"type": "string", "description": "Code to execute"},
                    "timeout": {"type": "integer", "default": 30, "description": "Timeout in seconds"},
                    "stdin": {"type": "string", "description": "Standard input"}
                },
                "required": ["language", "code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_github",
            "description": "Search for code, repositories, or issues on GitHub",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "type": {"type": "string", "enum": ["repositories", "code", "issues", "users"]},
                    "language": {"type": "string"},
                    "sort": {"type": "string", "enum": ["stars", "forks", "updated", "best-match"]},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_package_info",
            "description": "Get information about a package from npm, PyPI, or other registries",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_name": {"type": "string"},
                    "registry": {"type": "string", "enum": ["npm", "pypi", "crates", "maven", "rubygems"]},
                    "version": {"type": "string", "description": "Specific version, or 'latest'"}
                },
                "required": ["package_name", "registry"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lint_code",
            "description": "Run linter/static analysis on code",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string", "enum": ["python", "javascript", "typescript", "go", "rust"]},
                    "rules": {"type": "array", "items": {"type": "string"}, "description": "Specific rules to check"}
                },
                "required": ["code", "language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "format_code",
            "description": "Format code according to style guidelines",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string", "enum": ["python", "javascript", "typescript", "json", "yaml", "sql", "html", "css"]},
                    "style": {"type": "string", "description": "Style guide (e.g., 'black', 'prettier', 'google')"}
                },
                "required": ["code", "language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "explain_error",
            "description": "Get explanation and fix suggestions for an error message",
            "parameters": {
                "type": "object",
                "properties": {
                    "error_message": {"type": "string"},
                    "language": {"type": "string"},
                    "context_code": {"type": "string", "description": "Surrounding code context"}
                },
                "required": ["error_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_api_docs",
            "description": "Retrieve API documentation for a library or service",
            "parameters": {
                "type": "object",
                "properties": {
                    "library": {"type": "string"},
                    "method": {"type": "string", "description": "Specific method or endpoint"},
                    "version": {"type": "string"}
                },
                "required": ["library"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Execute test suite and return results",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_code": {"type": "string"},
                    "language": {"type": "string", "enum": ["python", "javascript", "typescript"]},
                    "framework": {"type": "string", "enum": ["pytest", "jest", "mocha", "unittest"]},
                    "coverage": {"type": "boolean", "default": False}
                },
                "required": ["test_code", "language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_regex",
            "description": "Generate a regular expression pattern for a description",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "What the regex should match"},
                    "test_strings": {"type": "array", "items": {"type": "string"}, "description": "Strings to test against"},
                    "flavor": {"type": "string", "enum": ["python", "javascript", "pcre"]}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_code",
            "description": "Convert code from one language to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "from_language": {"type": "string"},
                    "to_language": {"type": "string"},
                    "preserve_comments": {"type": "boolean", "default": True}
                },
                "required": ["code", "from_language", "to_language"]
            }
        }
    },
]

# Mock data
ERROR_EXPLANATIONS = {
    "TypeError": "Indica un'operazione applicata a un tipo di dato non appropriato",
    "ValueError": "Il valore passato è corretto come tipo ma non valido",
    "KeyError": "La chiave richiesta non esiste nel dizionario",
    "IndexError": "L'indice è fuori dai limiti della sequenza",
    "SyntaxError": "Errore di sintassi nel codice",
    "ImportError": "Impossibile importare il modulo specificato",
    "AttributeError": "L'oggetto non ha l'attributo richiesto"
}

LINT_RULES = {
    "python": ["E501", "W293", "F401", "E302", "E303", "W291", "E225", "E231"],
    "javascript": ["no-unused-vars", "semi", "quotes", "indent", "no-console", "eqeqeq"],
    "typescript": ["@typescript-eslint/no-explicit-any", "no-unused-vars", "prefer-const"]
}


def execute_code_tool(tool_name: str, args: dict) -> dict:
    """Execute code/developer mock tool."""
    
    if tool_name == "run_code":
        language = args.get("language", "python")
        code = args.get("code", "")
        timeout = args.get("timeout", 30)
        
        # Simulate execution
        success = random.random() > 0.15  # 85% success rate
        
        if success:
            # Generate mock output based on code patterns
            if "print" in code or "console.log" in code:
                stdout = "Hello, World!\n" + "\n".join([f"Output line {i}" for i in range(1, random.randint(2, 5))])
            elif "range" in code or "for" in code:
                stdout = "\n".join([str(i) for i in range(random.randint(5, 10))])
            else:
                stdout = f"Execution completed successfully.\nResult: {random.randint(1, 100)}"
            
            return {
                "status": "success",
                "language": language,
                "execution_time_ms": random.randint(5, 500),
                "stdout": stdout,
                "stderr": "",
                "exit_code": 0,
                "memory_used_mb": round(random.uniform(5, 50), 2)
            }
        else:
            errors = {
                "python": "Traceback (most recent call last):\n  File \"<stdin>\", line 3\n    result = undefined_var\nNameError: name 'undefined_var' is not defined",
                "javascript": "ReferenceError: undefined_var is not defined\n    at <anonymous>:3:12"
            }
            return {
                "status": "error",
                "language": language,
                "execution_time_ms": random.randint(5, 100),
                "stdout": "",
                "stderr": errors.get(language, "Error: execution failed"),
                "exit_code": 1
            }
    
    elif tool_name == "search_github":
        query = args.get("query", "")
        search_type = args.get("type", "repositories")
        limit = args.get("limit", 10)
        
        if search_type == "repositories":
            results = []
            for i in range(min(limit, random.randint(5, 10))):
                results.append({
                    "name": f"{query.split()[0] if query.split() else 'repo'}-{random.choice(['lib', 'api', 'sdk', 'tool', 'app'])}-{random.randint(1, 100)}",
                    "full_name": f"developer{random.randint(1, 999)}/{query.replace(' ', '-')}-{i}",
                    "description": f"A library for {query} - {random.choice(['Fast', 'Modern', 'Lightweight', 'Powerful'])} implementation",
                    "stars": random.randint(10, 50000),
                    "forks": random.randint(5, 5000),
                    "language": args.get("language", random.choice(["Python", "JavaScript", "TypeScript", "Go", "Rust"])),
                    "updated_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                    "url": f"https://github.com/user/repo-{i}",
                    "topics": random.sample([query.split()[0], "opensource", "library", "api", "tool"], min(3, 5))
                })
            results.sort(key=lambda x: x["stars"], reverse=True)
            
        elif search_type == "code":
            results = []
            for i in range(min(limit, random.randint(3, 8))):
                results.append({
                    "repository": f"org-{random.randint(1, 100)}/project-{random.randint(1, 50)}",
                    "path": f"src/{random.choice(['utils', 'lib', 'core', 'helpers'])}/{query.replace(' ', '_')}.py",
                    "snippet": f"def {query.replace(' ', '_')}(param):\n    '''Implementation for {query}'''\n    return result",
                    "url": f"https://github.com/org/project/blob/main/src/file.py#L{random.randint(10, 200)}"
                })
        else:
            results = []
        
        return {
            "query": query,
            "type": search_type,
            "total_count": random.randint(len(results), len(results) * 100),
            "results": results
        }
    
    elif tool_name == "get_package_info":
        package_name = args.get("package_name", "")
        registry = args.get("registry", "pypi")
        
        versions = [f"{random.randint(1, 5)}.{random.randint(0, 20)}.{random.randint(0, 10)}" for _ in range(5)]
        latest = max(versions)
        
        return {
            "name": package_name,
            "registry": registry,
            "version": args.get("version", latest),
            "latest_version": latest,
            "description": f"A {random.choice(['popular', 'lightweight', 'powerful'])} {package_name} library",
            "author": f"developer{random.randint(1, 999)}",
            "license": random.choice(["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0"]),
            "homepage": f"https://github.com/author/{package_name}",
            "downloads_last_month": random.randint(1000, 10000000),
            "dependencies": {
                f"dep-{i}": f"^{random.randint(1, 5)}.0.0" for i in range(random.randint(2, 8))
            },
            "available_versions": sorted(versions, reverse=True),
            "published_at": (datetime.now() - timedelta(days=random.randint(1, 1000))).isoformat(),
            "python_requires": ">=3.8" if registry == "pypi" else None,
            "node_version": ">=16.0.0" if registry == "npm" else None
        }
    
    elif tool_name == "lint_code":
        language = args.get("language", "python")
        code = args.get("code", "")
        
        issues = []
        rules = LINT_RULES.get(language, ["style-issue"])
        
        for i in range(random.randint(0, 5)):
            issues.append({
                "line": random.randint(1, max(1, code.count('\n') + 1)),
                "column": random.randint(1, 80),
                "rule": random.choice(rules),
                "severity": random.choice(["error", "warning", "info"]),
                "message": random.choice([
                    "Line too long",
                    "Unused import",
                    "Missing whitespace",
                    "Trailing whitespace",
                    "Expected indentation"
                ])
            })
        
        return {
            "language": language,
            "issues": issues,
            "total_issues": len(issues),
            "errors": sum(1 for i in issues if i["severity"] == "error"),
            "warnings": sum(1 for i in issues if i["severity"] == "warning"),
            "passed": len(issues) == 0,
            "score": round(100 - (len(issues) * 5), 1)
        }
    
    elif tool_name == "format_code":
        code = args.get("code", "")
        language = args.get("language", "python")
        
        # Simulate formatting
        return {
            "language": language,
            "style": args.get("style", "default"),
            "formatted_code": code.strip(),  # In real case would be properly formatted
            "changes_made": random.randint(0, 10),
            "lines_modified": random.randint(0, max(1, code.count('\n'))),
            "success": True
        }
    
    elif tool_name == "explain_error":
        error_message = args.get("error_message", "")
        
        # Try to identify error type
        error_type = None
        for err_type in ERROR_EXPLANATIONS:
            if err_type.lower() in error_message.lower():
                error_type = err_type
                break
        
        return {
            "error_type": error_type or "Unknown",
            "explanation": ERROR_EXPLANATIONS.get(error_type, "Errore non riconosciuto. Verifica la sintassi e i tipi di dato."),
            "common_causes": [
                "Variabile non definita prima dell'uso",
                "Tipo di dato errato passato alla funzione",
                "Indice fuori dai limiti",
                "Import mancante"
            ][:random.randint(2, 4)],
            "suggested_fixes": [
                "Verifica che tutte le variabili siano definite",
                "Controlla i tipi di dato",
                "Aggiungi gestione delle eccezioni",
                "Verifica gli import necessari"
            ][:random.randint(2, 4)],
            "related_docs": [
                f"https://docs.python.org/3/library/exceptions.html#{error_type}" if error_type else "https://docs.python.org/3/tutorial/errors.html"
            ]
        }
    
    elif tool_name == "get_api_docs":
        library = args.get("library", "")
        method = args.get("method")
        
        return {
            "library": library,
            "version": args.get("version", "latest"),
            "method": method,
            "documentation": {
                "signature": f"{method or library}.method(param1, param2, **kwargs)" if method else f"import {library}",
                "description": f"{'Metodo' if method else 'Libreria'} per {library}" + (f".{method}" if method else ""),
                "parameters": [
                    {"name": "param1", "type": "str", "required": True, "description": "First parameter"},
                    {"name": "param2", "type": "int", "required": False, "default": 0, "description": "Second parameter"}
                ],
                "returns": {"type": "dict", "description": "Result dictionary"},
                "example": f"from {library} import {method or 'main'}\nresult = {method or 'main'}('test')",
                "see_also": [f"{library}.related_method", f"{library}.other_method"]
            },
            "url": f"https://docs.library.io/{library}/{method or 'index'}"
        }
    
    elif tool_name == "run_tests":
        framework = args.get("framework", "pytest")
        coverage = args.get("coverage", False)
        
        total_tests = random.randint(5, 20)
        passed = random.randint(int(total_tests * 0.7), total_tests)
        failed = total_tests - passed
        
        result = {
            "framework": framework,
            "status": "passed" if failed == 0 else "failed",
            "summary": {
                "total": total_tests,
                "passed": passed,
                "failed": failed,
                "skipped": random.randint(0, 2),
                "duration_ms": random.randint(100, 5000)
            },
            "failed_tests": [
                {
                    "name": f"test_function_{i}",
                    "error": "AssertionError: expected True, got False",
                    "line": random.randint(10, 100)
                } for i in range(failed)
            ] if failed > 0 else []
        }
        
        if coverage:
            result["coverage"] = {
                "total_percent": round(random.uniform(60, 95), 1),
                "lines_covered": random.randint(100, 1000),
                "lines_total": random.randint(150, 1200),
                "branches_covered": round(random.uniform(50, 90), 1)
            }
        
        return result
    
    elif tool_name == "generate_regex":
        description = args.get("description", "")
        test_strings = args.get("test_strings", [])
        
        # Generate plausible regex based on description keywords
        patterns = {
            "email": r"^[\w\.-]+@[\w\.-]+\.\w+$",
            "phone": r"^\+?[\d\s\-]{10,15}$",
            "url": r"^https?://[\w\.-]+\.[a-z]{2,}(/\S*)?$",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "ip": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        }
        
        matched_pattern = None
        for key, pattern in patterns.items():
            if key in description.lower():
                matched_pattern = pattern
                break
        
        if not matched_pattern:
            matched_pattern = r"^[\w\s]+$"
        
        return {
            "pattern": matched_pattern,
            "description": description,
            "flavor": args.get("flavor", "python"),
            "explanation": "Pattern che matcha la descrizione fornita",
            "test_results": [
                {"string": s, "matches": random.random() > 0.3}
                for s in test_strings
            ] if test_strings else [],
            "flags_suggested": ["IGNORECASE"] if "case" in description.lower() else []
        }
    
    elif tool_name == "convert_code":
        from_lang = args.get("from_language", "python")
        to_lang = args.get("to_language", "javascript")
        
        return {
            "from_language": from_lang,
            "to_language": to_lang,
            "converted_code": f"// Converted from {from_lang} to {to_lang}\n{args.get('code', '')}",
            "warnings": [
                f"Some {from_lang}-specific features may not have direct equivalents in {to_lang}"
            ] if random.random() > 0.5 else [],
            "notes": f"Code converted with basic syntax transformation. Manual review recommended."
        }
    
    return {"error": f"Unknown code tool: {tool_name}"}
