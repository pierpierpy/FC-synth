"""FC Dataset Viewer - FastAPI Web App.

View and validate generated conversations.

Run with:
    synthfc serve

Then open: http://localhost:8000
"""

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import yaml

from ..config import data_dir, DEFAULT_CONFIG_PATH

# Paths
BASE_DIR = Path(__file__).parent
# Templates and static assets moved alongside this file, so they stay relative.
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
# Generated batches live in the repo-root data dir, not inside the package.
DATA_DIR = data_dir()

# App
app = FastAPI(title="FC Dataset Viewer")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def parse_jsonl(filepath: Path) -> dict:
    """Parse a JSONL file with metadata line + examples."""
    metadata = None
    examples = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("_metadata"):
                    metadata = data
                else:
                    examples.append(data)
            except json.JSONDecodeError:
                continue
    
    return {"metadata": metadata, "examples": examples}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/datasets", response_class=HTMLResponse)
async def datasets_page(request: Request):
    """Datasets list page."""
    return templates.TemplateResponse("datasets.html", {"request": request})


@app.get("/api/datasets")
async def list_datasets():
    """Full list of datasets with detailed statistics."""
    DATA_DIR.mkdir(exist_ok=True)
    
    datasets = []
    
    for batch_dir in sorted(DATA_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if not batch_dir.is_dir() or not batch_dir.name.startswith("batch_"):
            continue
            
        examples_file = batch_dir / "examples.jsonl"
        postprocessed_file = batch_dir / "examples_postprocessed.jsonl"
        validation_file = batch_dir / "validation_results.json"
        summary_file = batch_dir / "summary.json"
        exported_dir = batch_dir / "data"
        
        ds = {
            "name": batch_dir.name,
            "batch_name": batch_dir.name,
            "file_path": f"{batch_dir.name}/examples.jsonl",
            "modified": batch_dir.stat().st_mtime,
            "has_postprocessed": postprocessed_file.exists(),
            "has_exported": exported_dir.exists() and (exported_dir / "train.jsonl").exists(),
        }
        
        # Read the exported dataset's info.json
        exported_info = exported_dir / "info.json"
        if exported_info.exists():
            try:
                with open(exported_info) as f:
                    info = json.load(f)
                ds["exported"] = {
                    "total": info.get("total_examples", 0),
                    "train": info.get("train_size", 0),
                    "test": info.get("test_size", 0),
                    "test_split": info.get("test_split", 0.1),
                    "postprocessed": info.get("postprocessed", False),
                    "seed": info.get("seed", 42)
                }
                # File sizes
                train_file = exported_dir / "train.jsonl"
                test_file = exported_dir / "test.jsonl"
                all_file = exported_dir / "all.jsonl"
                if train_file.exists():
                    ds["exported"]["train_size_mb"] = round(train_file.stat().st_size / 1024 / 1024, 2)
                if test_file.exists():
                    ds["exported"]["test_size_mb"] = round(test_file.stat().st_size / 1024 / 1024, 2)
                if all_file.exists():
                    ds["exported"]["all_size_mb"] = round(all_file.stat().st_size / 1024 / 1024, 2)
            except Exception as e:
                print(f"Error reading export info for {batch_dir.name}: {e}")
        
        # Read validation_results.json for detailed stats
        if validation_file.exists():
            try:
                with open(validation_file) as f:
                    val = json.load(f)
                ds["count"] = val.get("summary", {}).get("total_examples", 0)
                ds["avg_score"] = val.get("summary", {}).get("average_score", 0)
                ds["total_pass"] = val.get("summary", {}).get("total_pass", 0)
                ds["total_fail"] = val.get("summary", {}).get("total_fail", 0)
                ds["total_warn"] = val.get("summary", {}).get("total_warn", 0)
                
                # Compute per-conversation pass/fail/warn from by_parameter
                by_param = val.get("by_parameter", {})
                ds["by_check"] = by_param

                # Estimate pass_convo, fail_convo, warn_convo from the data.
                # consecutive_roles and parallel_tool_calls are the real FAILs.
                consec = by_param.get("consecutive_roles", {})
                parallel = by_param.get("parallel_tool_calls", {})

                ds["fail_convo"] = consec.get("fail", 0) + parallel.get("fail", 0)
                ds["pass_convo"] = ds["count"] - ds["fail_convo"]
                ds["warn_convo"] = 0  # Warnings are non-blocking
                
            except Exception as e:
                print(f"Error reading validation for {batch_dir.name}: {e}")
        
        # Fallback: read summary.json
        if "count" not in ds and summary_file.exists():
            try:
                with open(summary_file) as f:
                    summary = json.load(f)
                ds["count"] = summary.get("total_examples", 0)
                ds["model"] = summary.get("model", "unknown")
                ds["avg_score"] = summary.get("validation", {}).get("avg_score", 0)
            except:
                pass
        
        # Fallback: count examples
        if "count" not in ds and examples_file.exists():
            try:
                count = sum(1 for line in open(examples_file) if line.strip() and not '"_metadata"' in line)
                ds["count"] = count
            except:
                ds["count"] = 0
        
        datasets.append(ds)
    
    return {"datasets": datasets}


@app.get("/api/files")
async def list_files():
    """List batches (directories) and files in the data directory."""
    DATA_DIR.mkdir(exist_ok=True)

    file_info = []

    # 1. Look for batch directories (new layout)
    for batch_dir in sorted(DATA_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if batch_dir.is_dir() and batch_dir.name.startswith("batch_"):
            examples_file = batch_dir / "examples.jsonl"
            summary_file = batch_dir / "summary.json"

            info = {
                "name": f"{batch_dir.name}/examples.jsonl",
                "batch_name": batch_dir.name,
                "modified": batch_dir.stat().st_mtime,
                "type": "batch",
                "has_postprocessed": (batch_dir / "examples_postprocessed.jsonl").exists()
            }

            # Read the summary if present
            if summary_file.exists():
                try:
                    with open(summary_file) as f:
                        summary = json.load(f)
                    info["count"] = summary.get("total_examples", "?")
                    info["model"] = summary.get("model", "unknown")
                    info["errors"] = summary.get("errors", 0)
                    info["avg_score"] = summary.get("validation", {}).get("avg_score", 0)
                except:
                    pass
            
            # Fallback: count from the file
            if "count" not in info and examples_file.exists():
                try:
                    parsed = parse_jsonl(examples_file)
                    info["count"] = len(parsed["examples"])
                except:
                    info["count"] = "?"

            file_info.append(info)

    # 2. Also look for .jsonl files directly under data/ (old layout)
    for f in sorted(DATA_DIR.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True):
        # Skip checkpoint and summary files
        if "checkpoint" in f.name or "summary" in f.name:
            continue
        
        info = {
            "name": f.name,
            "batch_name": None,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
            "type": "jsonl"
        }
        
        try:
            parsed = parse_jsonl(f)
            info["count"] = len(parsed["examples"])
            if parsed["metadata"]:
                info["model"] = parsed["metadata"].get("model", "unknown")
                info["errors"] = parsed["metadata"].get("errors", 0)
        except:
            info["count"] = "?"
        
        file_info.append(info)
    
    return {"files": file_info}


@app.get("/api/load/{filename:path}")
async def load_file(
    filename: str, 
    page: int = 1, 
    per_page: int = 50,
    status: str = None,
    fail_category: str = None
):
    """
    Load a specific JSONL or JSON file.

    - Returns ALL statistics computed over the whole dataset
    - Returns only the paginated examples for display
    - Supports filtering by status (pass/fail/warn/error)
    - Supports filtering by FAIL category (consecutive_roles, parallel_tool_calls)

    Args:
        filename: path of the file
        page: current page (1-indexed)
        per_page: examples per page
        status: filter by status (pass, fail, warn, error)
        fail_category: filter by a specific FAIL category
    """
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    
    try:
        if filepath.suffix == ".jsonl":
            parsed = parse_jsonl(filepath)
            all_examples = parsed["examples"]
        else:
            with open(filepath) as f:
                content = json.load(f)
            all_examples = content if isinstance(content, list) else content.get('examples', [])
            parsed = {"metadata": None}
        
        # Compute statistics over the WHOLE dataset (before filtering)
        stats = calculate_full_stats(all_examples)

        # Filter by status if requested
        if status:
            all_examples = filter_by_status(all_examples, status, fail_category)

        # Paginate only for display
        total_count = len(all_examples)
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged_examples = all_examples[start_idx:end_idx]
        
        return {
            "file": filename,
            "metadata": parsed.get("metadata"),
            "count": total_count,
            "stats": stats,  # Statistics over EVERYTHING (unfiltered)
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "total_count": total_count
            },
            "examples": paged_examples  # Current page only (filtered)
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


def filter_by_status(examples: list, status: str, fail_category: str = None) -> list:
    """Filter examples by status and optionally by FAIL category."""
    filtered = []

    for ex in examples:
        ex_status = get_example_status(ex)

        if ex_status != status:
            continue

        # If status=fail and a fail_category is given, filter further
        if status == "fail" and fail_category:
            validation = ex.get("validation", {})
            results = validation.get("results", [])

            # Check whether this example has a FAIL in the given category
            has_category_fail = any(
                r.get("param") == fail_category and r.get("status") == "❌"
                for r in results
            )
            
            if not has_category_fail:
                continue
        
        filtered.append(ex)
    
    return filtered


def get_example_status(ex: dict) -> str:
    """Determine the status of an example."""
    if ex.get("error"):
        return "error"
    
    validation = ex.get("validation")
    if validation:
        if validation.get("failed", 0) > 0:
            return "fail"
        if validation.get("warnings", 0) > 0:
            return "warn"
        return "pass"
    
    return "unknown"


def calculate_full_stats(examples: list) -> dict:
    """Compute statistics over ALL examples."""
    pass_convo = 0
    fail_convo = 0
    warn_convo = 0
    errors = 0
    total_score = 0
    validated_count = 0
    by_check = {}
    
    for ex in examples:
        if ex.get("error"):
            errors += 1
            continue
        
        validation = ex.get("validation")
        if validation:
            score = validation.get("score", 0)
            total_score += score
            validated_count += 1
            
            if validation.get("failed", 0) > 0:
                fail_convo += 1
            elif validation.get("warnings", 0) > 0:
                warn_convo += 1
            else:
                pass_convo += 1
            
            # Per-check stats
            for r in validation.get("results", []):
                check_name = r.get("param", "unknown")
                if check_name not in by_check:
                    by_check[check_name] = {"pass": 0, "fail": 0, "warn": 0}
                
                status = r.get("status", "")
                if status == "✅":
                    by_check[check_name]["pass"] += 1
                elif status == "❌":
                    by_check[check_name]["fail"] += 1
                elif status == "⚠️":
                    by_check[check_name]["warn"] += 1
    
    avg_score = round((total_score / validated_count) * 100) if validated_count > 0 else 0
    
    return {
        "total": len(examples),
        "pass_convo": pass_convo,
        "fail_convo": fail_convo,
        "warn_convo": warn_convo,
        "errors": errors,
        "avg_score": avg_score,
        "by_check": by_check
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a JSONL or JSON file."""
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Detect JSONL vs JSON
        if file.filename.endswith('.jsonl'):
            metadata = None
            examples = []
            for line in content_str.split('\n'):
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if data.get("_metadata"):
                    metadata = data
                else:
                    examples.append(data)
            
            return {
                "file": file.filename,
                "metadata": metadata,
                "count": len(examples),
                "examples": examples
            }
        else:
            data = json.loads(content_str)
            examples = data if isinstance(data, list) else data.get('examples', [])
            return {
                "file": file.filename,
                "metadata": None,
                "count": len(examples),
                "examples": examples
            }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/stats")
async def get_all_stats():
    """Get aggregate stats for all files in data/."""
    DATA_DIR.mkdir(exist_ok=True)
    
    total_examples = 0
    total_errors = 0
    total_pass = 0
    total_fail = 0
    total_warn = 0
    
    files = list(DATA_DIR.glob("*.jsonl"))
    
    for f in files:
        if "_summary" in f.name or "_checkpoint" in f.name:
            continue
        
        try:
            parsed = parse_jsonl(f)
            for ex in parsed["examples"]:
                total_examples += 1
                if ex.get("error"):
                    total_errors += 1
                elif ex.get("validation"):
                    v = ex["validation"]
                    total_pass += v.get("passed", 0)
                    total_fail += v.get("failed", 0)
                    total_warn += v.get("warnings", 0)
        except:
            continue
    
    return {
        "total_examples": total_examples,
        "total_errors": total_errors,
        "validation": {
            "pass": total_pass,
            "fail": total_fail,
            "warn": total_warn
        }
    }


@app.post("/api/postprocess/{batch_name}")
async def run_postprocess(batch_name: str):
    """Run post-processing on a batch."""
    batch_dir = DATA_DIR / batch_name
    examples_file = batch_dir / "examples.jsonl"

    if not examples_file.exists():
        return JSONResponse({"error": "Batch not found"}, status_code=404)

    try:
        from ..pipeline.postprocess import postprocess_batch
        stats = postprocess_batch(batch_dir, dry_run=False)
        return {
            "success": True,
            "stats": {
                "total_examples": stats.total_examples,
                "examples_modified": stats.examples_modified,
                "user_merged": stats.user_user_merged,
                "reflections_removed": stats.reflections_removed
            }
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """Dataset statistics page."""
    return templates.TemplateResponse("stats.html", {"request": request})


@app.get("/api/dataset_stats/{batch_name}")
async def get_dataset_stats(batch_name: str):
    """Detailed statistics for a single dataset."""
    batch_dir = DATA_DIR / batch_name

    # Prefer the postprocessed file, fall back to the original
    pp_file = batch_dir / "examples_postprocessed.jsonl"
    orig_file = batch_dir / "examples.jsonl"

    filepath = pp_file if pp_file.exists() else orig_file

    if not filepath.exists():
        return JSONResponse({"error": "Dataset not found"}, status_code=404)

    try:
        parsed = parse_jsonl(filepath)
        examples = parsed["examples"]

        # Basic statistics
        total = len(examples)
        errors = sum(1 for e in examples if e.get("error"))
        valid = total - errors

        # Validation
        pass_count = sum(1 for e in examples if not e.get("error") and e.get("validation", {}).get("failed", 1) == 0)
        fail_count = sum(1 for e in examples if not e.get("error") and e.get("validation", {}).get("failed", 0) > 0)

        # Per-parameter statistics
        param_stats = {}
        for ex in examples:
            if ex.get("error"):
                continue
            for r in ex.get("validation", {}).get("results", []):
                param = r.get("param", "unknown")
                if param not in param_stats:
                    param_stats[param] = {"pass": 0, "fail": 0, "warn": 0}
                
                status = r.get("status", "")
                if "✅" in status:
                    param_stats[param]["pass"] += 1
                elif "❌" in status:
                    param_stats[param]["fail"] += 1
                elif "⚠️" in status:
                    param_stats[param]["warn"] += 1
        
        # call_type distribution
        call_type_dist = {}
        for ex in examples:
            if ex.get("error"):
                continue
            ct = ex.get("params", {}).get("call_type", "unknown")
            call_type_dist[ct] = call_type_dist.get(ct, 0) + 1

        # num_tool_calls distribution (only over positives, where it is meaningful)
        tool_calls_dist = {}
        for ex in examples:
            if ex.get("error"):
                continue
            # Only positives have an expected num_tool_calls
            if ex.get("params", {}).get("call_type") != "positive":
                continue
            ntc = ex.get("observed", {}).get("num_tool_calls", 0)
            tool_calls_dist[str(ntc)] = tool_calls_dist.get(str(ntc), 0) + 1

        # conversation_length distribution
        conv_length_dist = {}
        for ex in examples:
            if ex.get("error"):
                continue
            nm = ex.get("observed", {}).get("num_messages", 0)
            bucket = f"{(nm // 5) * 5}-{(nm // 5) * 5 + 4}"
            conv_length_dist[bucket] = conv_length_dist.get(bucket, 0) + 1

        # Language distribution (tool_lang,conv_lang combo)
        lang_dist = {}
        for ex in examples:
            if ex.get("error"):
                continue
            tool_lang = ex.get("params", {}).get("tool_language", "unknown")
            conv_lang = ex.get("params", {}).get("conversation_language", "unknown")
            combo = f"{tool_lang},{conv_lang}"
            lang_dist[combo] = lang_dist.get(combo, 0) + 1

        # Detailed distributions per subcategory
        positive_examples = [e for e in examples if not e.get("error") and e.get("params", {}).get("call_type") == "positive"]
        negative_examples = [e for e in examples if not e.get("error") and e.get("params", {}).get("call_type") == "negative"]
        clarification_examples = [e for e in examples if not e.get("error") and e.get("params", {}).get("call_type") == "clarification"]
        
        # Positive type distribution
        positive_type_dist = {}
        for ex in positive_examples:
            pt = ex.get("params", {}).get("positive_type", "unknown")
            positive_type_dist[pt] = positive_type_dist.get(pt, 0) + 1
        
        # Negative reason distribution
        negative_reason_dist = {}
        for ex in negative_examples:
            nr = ex.get("params", {}).get("negative_reason", "unknown")
            negative_reason_dist[nr] = negative_reason_dist.get(nr, 0) + 1
        
        # Clarification outcome distribution
        clarification_outcome_dist = {}
        for ex in clarification_examples:
            co = ex.get("params", {}).get("clarification_outcome", "unknown")
            clarification_outcome_dist[co] = clarification_outcome_dist.get(co, 0) + 1
        
        # Out-of-scope requests distribution
        out_of_scope_dist = {}
        for ex in examples:
            if ex.get("error"):
                continue
            oos = ex.get("params", {}).get("out_of_scope_requests", 0)
            out_of_scope_dist[str(oos)] = out_of_scope_dist.get(str(oos), 0) + 1
        
        return {
            "batch_name": batch_name,
            "source_file": filepath.name,
            "summary": {
                "total": total,
                "valid": valid,
                "errors": errors,
                "pass": pass_count,
                "fail": fail_count,
                "pass_rate": round(pass_count / valid * 100, 1) if valid > 0 else 0
            },
            "param_stats": param_stats,
            "distributions": {
                "call_type": call_type_dist,
                "num_tool_calls": tool_calls_dist,
                "conversation_length": conv_length_dist,
                "language": lang_dist,
                "positive_type": positive_type_dist,
                "negative_reason": negative_reason_dist,
                "clarification_outcome": clarification_outcome_dist,
                "out_of_scope_requests": out_of_scope_dist
            },
            "subcounts": {
                "positive": len(positive_examples),
                "negative": len(negative_examples),
                "clarification": len(clarification_examples)
            }
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/sampling_config")
async def get_sampling_config():
    """Return the expected sampling configuration from the default config."""
    config_path = DEFAULT_CONFIG_PATH

    if not config_path.exists():
        return {"error": "default config not found"}

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        sampling = config.get("sampling", {})
        
        return {
            "call_type": sampling.get("call_type", {}),
            "num_tool_calls": {str(k): v for k, v in sampling.get("num_tool_calls", {}).items()},
            "language_combo": sampling.get("language_combo", {}),
            "positive_type": sampling.get("positive_type", {}),
            "negative_reason": sampling.get("negative_reason", {}),
            "clarification_outcome": sampling.get("clarification_outcome", {}),
            "out_of_scope_requests": {str(k): v for k, v in sampling.get("out_of_scope_requests", {}).items()}
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/batch_config/{batch_name}")
async def get_batch_config(batch_name: str):
    """Return the configuration used for a specific batch (from its directory)."""
    batch_dir = DATA_DIR / batch_name
    config_path = batch_dir / "config.yaml"

    if not config_path.exists():
        # Fall back to the global config if the batch has no saved config
        return await get_sampling_config()
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        sampling = config.get("sampling", {})
        
        return {
            "source": "batch",
            "batch_name": batch_name,
            "call_type": sampling.get("call_type", {}),
            "num_tool_calls": {str(k): v for k, v in sampling.get("num_tool_calls", {}).items()},
            "language_combo": sampling.get("language_combo", {}),
            "positive_type": sampling.get("positive_type", {}),
            "negative_reason": sampling.get("negative_reason", {}),
            "clarification_outcome": sampling.get("clarification_outcome", {}),
            "out_of_scope_requests": {str(k): v for k, v in sampling.get("out_of_scope_requests", {}).items()}
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/download/{batch_name}/{file_type}")
async def download_exported(batch_name: str, file_type: str = "all"):
    """Download an exported file (train, test, all)."""
    from fastapi.responses import FileResponse
    
    valid_types = ["train", "test", "all"]
    if file_type not in valid_types:
        return JSONResponse({"error": f"file_type must be one of: {valid_types}"}, status_code=400)
    
    file_path = DATA_DIR / batch_name / "data" / f"{file_type}.jsonl"
    
    if not file_path.exists():
        return JSONResponse({"error": f"File not found: {file_path}"}, status_code=404)
    
    return FileResponse(
        path=file_path,
        filename=f"{batch_name}_{file_type}.jsonl",
        media_type="application/jsonl"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
