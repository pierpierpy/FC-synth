#!/usr/bin/env python3
"""Synthetic FC dataset generation via the offline Batch API.

The Batch API is cheaper than the synchronous API but can take up to 24 hours
to complete. The flow implemented here:

1. Build the requests and upload them to the provider.
2. Create the batch job.
3. Wait for completion (polling every 60s; safe to interrupt and resume).
4. Download the results and convert them to the standard format.
5. Validate and post-process the examples.

The output layout matches the synchronous generation path:

    data/<batch_name>/
    ├── examples.jsonl
    ├── examples_postprocessed.jsonl
    └── summary.json
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional

from ..config import get_config, data_dir
from .sampler import sample_params, SampledParams
from .prompt_builder import generate_api_request
from .generator import GeneratedExample, extract_observed_metrics
from .validator import validate_example
from .client import select_tools_for_params, convert_result
from ..tools.ita import TOOLS_BY_CATEGORY as TOOLS_IT
from ..tools.eng import TOOLS_BY_CATEGORY as TOOLS_EN


def get_batch_client():
    """Create a client for the Batch API for the configured provider.

    Works for both providers, selected by ``cfg.provider``:

    - ``"azure"``: an :class:`AzureOpenAI` client built from the endpoint,
      API key and API version.
    - anything else (OpenAI-compatible): an :class:`openai.OpenAI` client.

    Credentials are read from the environment via the config layer only.
    """
    cfg = get_config().model

    if not cfg.api_key:
        raise RuntimeError(
            "No API key found. Set SYNTHFC_API_KEY (or OPENAI_API_KEY) in your "
            "environment. See .env.example."
        )

    if cfg.provider == "azure":
        from openai import AzureOpenAI

        if not cfg.endpoint:
            raise RuntimeError(
                "provider='azure' requires SYNTHFC_ENDPOINT to be set to your "
                "Azure OpenAI resource endpoint."
            )
        return AzureOpenAI(
            api_key=cfg.api_key,
            api_version=cfg.api_version,
            azure_endpoint=cfg.endpoint,
        )

    import openai

    return openai.OpenAI(
        api_key=cfg.api_key,
        base_url=cfg.endpoint or None,
    )


def prepare_batch_requests(n: int, batch_dir: Path) -> tuple[Path, List[Dict]]:
    """Build the request file for the Batch API.

    Returns:
        ``(path to the JSONL file, list of metadata to reconstruct examples)``.
    """
    cfg = get_config()
    requests_file = batch_dir / "batch_requests.jsonl"
    metadata_list = []

    print(f"Preparing {n} requests...")

    with open(requests_file, 'w', encoding='utf-8') as f:
        for i in range(n):
            # Sample parameters.
            params = sample_params()
            example_id = str(uuid.uuid4())[:8]

            # Select tools.
            tools = select_tools_for_params(
                tool_language=params.tool_language,
                categories=params.tool_categories,
                num_tools=params.num_tools_available,
                tools_it=TOOLS_IT,
                tools_en=TOOLS_EN
            )

            # Build the API request.
            api_request = generate_api_request(params, tools)

            # Add the model field (required by the Batch API).
            api_request["model"] = cfg.model.model

            # Batch API request format. The URL is /chat/completions.
            batch_request = {
                "custom_id": example_id,
                "method": "POST",
                "url": "/chat/completions",
                "body": api_request
            }

            f.write(json.dumps(batch_request, ensure_ascii=False) + "\n")

            # Save metadata so we can reconstruct the example later.
            metadata_list.append({
                "id": example_id,
                "params": params.to_dict(),
                "tools": tools,
                "timestamp": datetime.now().isoformat()
            })

            if (i + 1) % 500 == 0:
                print(f"   Prepared {i + 1}/{n}...")

    # Save metadata.
    metadata_file = batch_dir / "batch_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False)

    print(f"Requests saved to {requests_file}")
    print(f"   Metadata saved to {metadata_file}")

    return requests_file, metadata_list


def upload_batch_file(client, requests_file: Path) -> str:
    """Upload the request file for the Batch API."""
    print(f"\nUploading batch file...")

    with open(requests_file, 'rb') as f:
        file_response = client.files.create(
            file=f,
            purpose="batch"
        )

    file_id = file_response.id
    print(f"File uploaded: {file_id}")
    return file_id


def create_batch_job(client, file_id: str) -> str:
    """Create the batch job."""
    print(f"\nCreating batch job...")

    batch = client.batches.create(
        input_file_id=file_id,
        endpoint="/chat/completions",
        completion_window="24h"
    )

    batch_id = batch.id
    print(f"Batch created: {batch_id}")
    print(f"   Status: {batch.status}")

    return batch_id


def wait_for_batch(client, batch_id: str, poll_interval: int = 60) -> Dict:
    """Wait for the batch to complete, polling at a fixed interval."""
    print(f"\nWaiting for batch completion (polling every {poll_interval}s)...")
    print(f"   This can take up to 24 hours. You can safely Ctrl+C and resume later.")
    print(f"   Batch ID: {batch_id}")
    print()

    start_time = time.time()
    last_status = None

    while True:
        try:
            batch = client.batches.retrieve(batch_id)
            status = batch.status

            if status != last_status:
                elapsed = time.time() - start_time
                elapsed_str = f"{int(elapsed // 3600)}h {int((elapsed % 3600) // 60)}m"
                print(f"   [{elapsed_str}] Status: {status}")

                if hasattr(batch, 'request_counts') and batch.request_counts:
                    rc = batch.request_counts
                    print(f"            Completed: {rc.completed}/{rc.total}, Failed: {rc.failed}")

                last_status = status

            if status == "completed":
                print(f"\nBatch completed!")
                return {
                    "status": "completed",
                    "output_file_id": batch.output_file_id,
                    "error_file_id": batch.error_file_id,
                    "request_counts": batch.request_counts
                }

            elif status in ["failed", "expired", "cancelled"]:
                print(f"\nBatch {status}")
                if hasattr(batch, 'errors') and batch.errors:
                    print(f"   Errors: {batch.errors}")
                return {"status": status, "error": str(batch.errors) if hasattr(batch, 'errors') else None}

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            print(f"\n\nInterrupted! To resume, run:")
            print(f"   synthfc batch-api --resume {batch_id}")
            return {"status": "interrupted", "batch_id": batch_id}


def download_results(client, output_file_id: str, batch_dir: Path) -> Path:
    """Download the batch results."""
    print(f"\nDownloading results...")

    results_file = batch_dir / "batch_results.jsonl"

    content = client.files.content(output_file_id)

    with open(results_file, 'wb') as f:
        f.write(content.read())

    print(f"Results saved to {results_file}")
    return results_file


def convert_results_to_examples(
    results_file: Path,
    metadata_list: List[Dict],
    batch_dir: Path
) -> List[GeneratedExample]:
    """Convert Batch API results into the standard ``GeneratedExample`` format."""
    print(f"\nConverting results to standard format...")

    # Build an id -> metadata mapping.
    metadata_by_id = {m["id"]: m for m in metadata_list}

    examples = []
    errors = 0

    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line.strip())
            custom_id = result.get("custom_id")
            meta = metadata_by_id.get(custom_id, {})

            # Check for errors.
            if result.get("error"):
                examples.append(GeneratedExample(
                    id=custom_id,
                    timestamp=meta.get("timestamp", datetime.now().isoformat()),
                    system_prompt="",
                    messages=[],
                    tools=meta.get("tools", []),
                    params=meta.get("params", {}),
                    observed={},
                    validation=None,
                    generation_time_ms=0,
                    error=str(result["error"])
                ))
                errors += 1
                continue

            # Extract the response.
            response = result.get("response", {})
            body = response.get("body", {})

            if response.get("status_code") != 200:
                examples.append(GeneratedExample(
                    id=custom_id,
                    timestamp=meta.get("timestamp", datetime.now().isoformat()),
                    system_prompt="",
                    messages=[],
                    tools=meta.get("tools", []),
                    params=meta.get("params", {}),
                    observed={},
                    validation=None,
                    generation_time_ms=0,
                    error=f"HTTP {response.get('status_code')}: {body}"
                ))
                errors += 1
                continue

            # Parse the response (same as the synchronous path).
            try:
                # Convert the API result into the standard format.
                raw_result = {
                    "choices": body.get("choices", []),
                    "model": body.get("model"),
                    "usage": body.get("usage")
                }

                final = convert_result(raw_result, meta.get("tools", []))
                observed = extract_observed_metrics(final)

                # Validate.
                example_for_validation = {
                    'id': custom_id,
                    'params': meta.get("params", {}),
                    'observed': observed,
                    'messages': final.get('messages', []),
                    'system_prompt': final.get('system_prompt', '')
                }
                validation_result = validate_example(example_for_validation)

                examples.append(GeneratedExample(
                    id=custom_id,
                    timestamp=meta.get("timestamp", datetime.now().isoformat()),
                    system_prompt=final.get('system_prompt', ''),
                    messages=final.get('messages', []),
                    tools=final.get('tools', meta.get("tools", [])),
                    params=meta.get("params", {}),
                    observed=observed,
                    validation={
                        'example_id': validation_result.example_id,
                        'score': validation_result.score,
                        'passed': validation_result.passed,
                        'failed': validation_result.failed,
                        'warnings': validation_result.warnings,
                        'results': [
                            {
                                'param': r.param_name,
                                'expected': r.expected,
                                'observed': r.observed,
                                'status': r.status.value,
                                'message': r.message
                            }
                            for r in validation_result.results
                        ]
                    },
                    generation_time_ms=0,
                    error=None
                ))

            except Exception as e:
                examples.append(GeneratedExample(
                    id=custom_id,
                    timestamp=meta.get("timestamp", datetime.now().isoformat()),
                    system_prompt="",
                    messages=[],
                    tools=meta.get("tools", []),
                    params=meta.get("params", {}),
                    observed={},
                    validation=None,
                    generation_time_ms=0,
                    error=f"Parse error: {str(e)}"
                ))
                errors += 1

    print(f"Converted {len(examples)} examples ({errors} errors)")
    return examples


def save_examples(examples: List[GeneratedExample], batch_dir: Path, cfg) -> Path:
    """Save the examples in the standard JSONL format."""
    output_file = batch_dir / "examples.jsonl"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Metadata.
        metadata = {
            "_metadata": True,
            "generated_at": datetime.now().isoformat(),
            "count": len(examples),
            "errors": sum(1 for e in examples if e.error),
            "version": "1.0",
            "model": cfg.model.model,
            "temperature": cfg.model.temperature,
            "api_type": "batch"
        }
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")

        for ex in examples:
            f.write(json.dumps(ex.to_dict(), ensure_ascii=False) + "\n")

    print(f"Saved to {output_file}")
    return output_file


def print_validation_summary(examples: List[GeneratedExample]):
    """Print a validation summary (same logic as the synchronous path)."""
    valid_examples = [e for e in examples if e.validation]

    if not valid_examples:
        print("   No validation results available")
        return

    total_pass = 0
    total_fail = 0
    total_warn = 0
    param_stats = defaultdict(lambda: {'pass': 0, 'fail': 0, 'warn': 0})

    scores = []
    for ex in valid_examples:
        v = ex.validation
        scores.append(v.get('score', 0))
        total_pass += v.get('passed', 0)
        total_fail += v.get('failed', 0)
        total_warn += v.get('warnings', 0)

        for r in v.get('results', []):
            status = r.get('status', '')
            param = r.get('param', 'unknown')
            if '✅' in status:
                param_stats[param]['pass'] += 1
            elif '❌' in status:
                param_stats[param]['fail'] += 1
            elif '⚠️' in status:
                param_stats[param]['warn'] += 1

    avg_score = sum(scores) / len(scores) if scores else 0

    print(f"   Validated: {len(valid_examples)}")
    print(f"   Avg score: {avg_score:.1f}%")
    print(f"   Total: pass {total_pass} | fail {total_fail} | warn {total_warn}")

    print(f"\nBy parameter:")
    for param, stats in sorted(param_stats.items()):
        total = stats['pass'] + stats['fail'] + stats['warn']
        pct = (stats['pass'] / total * 100) if total > 0 else 0
        print(f"   {param:25} | pass {stats['pass']:3} fail {stats['fail']:3} warn {stats['warn']:3} | {pct:5.1f}%")


def resume_batch(batch_id: str):
    """Resume an in-progress batch job."""
    client = get_batch_client()

    # Look for the batch folder.
    base_dir = data_dir()
    batch_dirs = list(base_dir.glob("batch_*"))

    # Find the folder for this batch_id.
    target_dir = None
    for bd in batch_dirs:
        status_file = bd / "batch_status.json"
        if status_file.exists():
            with open(status_file) as f:
                status = json.load(f)
                if status.get("batch_id") == batch_id:
                    target_dir = bd
                    break

    if not target_dir:
        # Create a new directory for the resume.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = base_dir / f"batch_resume_{timestamp}"
        target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Resuming batch: {batch_id}")
    print(f"   Output dir: {target_dir}")

    # Wait for completion.
    result = wait_for_batch(client, batch_id)

    if result["status"] != "completed":
        print(f"Batch did not complete (status: {result['status']})")
        return

    # The rest of the pipeline (download, convert, post-process) requires the
    # original metadata file to reconstruct the examples.
    print(f"Batch completed! Output file ID: {result.get('output_file_id')}")
    print(f"   To download results, you need the original metadata file.")


def run(n: int = 5000, resume: Optional[str] = None) -> None:
    """Generate ``n`` examples through the offline Batch API.

    Args:
        n: number of examples to request.
        resume: if set, resume the batch job with this id instead of creating
            a new one.
    """
    if resume:
        resume_batch(resume)
        return

    cfg = get_config()

    # Create a folder for this batch.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_name = f"batch_{n}_{timestamp}"
    batch_dir = data_dir() / batch_name
    batch_dir.mkdir(parents=True, exist_ok=True)

    print(f"Synthetic FC dataset generation - Batch API")
    print(f"   Model: {cfg.model.model}")
    print(f"   Temperature: {cfg.model.temperature}")
    print(f"   Target examples: {n}")
    print(f"   Output dir: {batch_dir}")
    print(f"   Using the Batch API (cheaper, up to 24h)")
    print()

    # 1. Prepare the requests.
    requests_file, metadata_list = prepare_batch_requests(n, batch_dir)

    # 2. Initialize the client.
    client = get_batch_client()

    # 3. Upload the file.
    file_id = upload_batch_file(client, requests_file)

    # 4. Create the batch job.
    batch_id = create_batch_job(client, file_id)

    # Save state so the batch can be resumed.
    status_file = batch_dir / "batch_status.json"
    with open(status_file, 'w') as f:
        json.dump({
            "batch_id": batch_id,
            "file_id": file_id,
            "n": n,
            "created_at": datetime.now().isoformat()
        }, f, indent=2)

    # 5. Wait for completion.
    result = wait_for_batch(client, batch_id)

    if result["status"] != "completed":
        print(f"\nBatch did not complete: {result}")
        return

    # 6. Download the results.
    results_file = download_results(client, result["output_file_id"], batch_dir)

    # 7. Convert to the standard format.
    examples = convert_results_to_examples(results_file, metadata_list, batch_dir)

    # 8. Save in the standard JSONL format.
    save_examples(examples, batch_dir, cfg)

    # Generation stats.
    errors = sum(1 for e in examples if e.error)
    print(f"\nGeneration summary:")
    print(f"   Total: {len(examples)}")
    print(f"   Errors: {errors}")
    if examples:
        print(f"   Success: {(len(examples)-errors)/len(examples)*100:.1f}%")

    # Validation stats.
    print(f"\nValidation summary:")
    print_validation_summary(examples)

    # 9. Post-processing (same logic as the synchronous path).
    print(f"\nPost-processing...")
    from ..pipeline.postprocess import postprocess_batch
    pp_stats = postprocess_batch(batch_dir, dry_run=False)

    print(f"   Modified: {pp_stats.examples_modified}/{pp_stats.total_examples}")
    print(f"   User merged: {pp_stats.user_user_merged}")
    print(f"   Reflections removed: {pp_stats.reflections_removed}")

    # 10. Save the summary.
    summary_file = batch_dir / "summary.json"
    valid_examples = [e for e in examples if e.validation]
    summary = {
        "batch_name": batch_name,
        "generated_at": timestamp,
        "model": cfg.model.model,
        "temperature": cfg.model.temperature,
        "api_type": "batch",
        "total_examples": len(examples),
        "errors": errors,
        "batch_id": batch_id,
        "validation": {
            "validated": len(valid_examples),
            "avg_score": sum(e.validation.get('score', 0) for e in valid_examples) / len(valid_examples) * 100 if valid_examples else 0
        },
        "postprocess": {
            "examples_modified": pp_stats.examples_modified,
            "user_merged": pp_stats.user_user_merged,
            "reflections_removed": pp_stats.reflections_removed
        },
        "files": {
            "examples": "examples.jsonl",
            "examples_postprocessed": "examples_postprocessed.jsonl",
            "batch_requests": "batch_requests.jsonl",
            "batch_results": "batch_results.jsonl"
        }
    }
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Final stats.
    print(f"\nFinal stats (post-processed):")
    with open(batch_dir / "examples_postprocessed.jsonl") as f:
        pp_examples = [json.loads(l) for l in f if l.strip() and '_metadata' not in l]

    pp_valid = [e for e in pp_examples if not e.get('error')]
    pp_pass = sum(1 for e in pp_valid if e.get('validation', {}).get('failed', 0) == 0)
    pp_fail = sum(1 for e in pp_valid if e.get('validation', {}).get('failed', 0) > 0)
    pp_err = sum(1 for e in pp_examples if e.get('error'))

    total_valid = len(pp_valid)
    print(f"   Pass: {pp_pass}/{total_valid} ({pp_pass/total_valid*100:.1f}%)" if total_valid > 0 else "   Pass: 0")
    print(f"   Fail: {pp_fail}/{total_valid} ({pp_fail/total_valid*100:.1f}%)" if total_valid > 0 else "   Fail: 0")
    print(f"   Errors: {pp_err}")

    print(f"\nBatch saved to {batch_dir}/")
    print(f"   examples.jsonl (original)")
    print(f"   examples_postprocessed.jsonl (cleaned)")
    print(f"   summary.json")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate an FC dataset via the offline Batch API.")
    parser.add_argument("n", type=int, nargs="?", default=5000, help="Number of examples to request.")
    parser.add_argument("--resume", type=str, default=None, help="Resume an existing batch job id.")
    args = parser.parse_args()

    run(n=args.n, resume=args.resume)
