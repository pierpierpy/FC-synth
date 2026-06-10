#!/usr/bin/env python3
"""Enriched export.

Unlike the minimal training export (``export.py``, which writes only
``{messages, tools}``), this produces a self-describing row per example that
keeps *everything* used to create the text:

- ``sampler``    — every sampled parameter that shaped the conversation
- ``model``      — the teacher model that generated it
- ``tools``      — the tool definitions, kept separate from the text
- ``context``    — system prompt + all turns up to and including the last user turn
- ``answer``     — the final assistant turn (the gold response, with its tool_calls)

The split is "last assistant turn = answer": ``context`` is everything before
it, ``answer`` is that final assistant message.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Optional

from ..config import data_dir

# Fields on each example that come straight from the sampler.
_SAMPLER_FIELDS = [
    "call_type", "positive_type", "negative_reason", "clarification_outcome",
    "num_tool_calls", "first_tool_position", "param_complexity",
    "conversation_length", "history_type", "user_style", "domain",
    "system_prompt_type", "edge_case", "out_of_scope_requests",
    "num_tools_available", "tool_categories",
]


def _read_jsonl(path: Path):
    """Yield (metadata, examples) — metadata is the first ``_metadata`` line if present."""
    metadata = {}
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            if data.get("_metadata"):
                metadata = data
                continue
            if data.get("error"):
                continue
            examples.append(data)
    return metadata, examples


def _split_context_answer(messages: list, system_prompt: Optional[str]):
    """Split into (context, answer) with answer = the final assistant turn.

    ``context`` = system prompt (as a system message, if present) + every message
    before the final assistant turn. ``answer`` = that final assistant message.
    Returns (context, answer) or (None, None) if there is no trailing assistant turn.
    """
    if not messages:
        return None, None

    # Find the last assistant message.
    last_assistant_idx = None
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "assistant":
            last_assistant_idx = i
            break
    if last_assistant_idx is None:
        return None, None

    context = messages[:last_assistant_idx]
    answer = messages[last_assistant_idx]

    if system_prompt:
        context = [{"role": "system", "content": system_prompt}] + context

    return context, answer


def enrich_example(ex: dict, model: str) -> Optional[dict]:
    """Turn a raw generated example into one enriched, self-describing row."""
    params = ex.get("params", {})
    context, answer = _split_context_answer(ex.get("messages", []), ex.get("system_prompt"))
    if answer is None:
        return None

    validation = ex.get("validation") or {}

    return {
        "id": ex.get("id"),
        "model": model,
        "language": {
            "tool": params.get("tool_language"),
            "conversation": params.get("conversation_language"),
        },
        # All sampler information used to create this row.
        "sampler": {k: params.get(k) for k in _SAMPLER_FIELDS},
        # What the model actually did (measured post-hoc).
        "observed": ex.get("observed", {}),
        # Validation summary (full per-check results stay in the batch file).
        "validation": {
            "score": validation.get("score"),
            "passed": validation.get("passed"),
            "failed": validation.get("failed"),
            "warnings": validation.get("warnings"),
        },
        # Tools kept separate from the conversation text.
        "tools": ex.get("tools", []),
        # Conversation split: everything up to & including the last user turn …
        "context": context,
        # … and the final assistant turn (the gold answer, with tool_calls if any).
        "answer": answer,
    }


def export_enriched(
    batch_name: str,
    model: Optional[str] = None,
    use_postprocessed: bool = True,
    filter_failed: bool = True,
    test_split: float = 0.1,
    seed: int = 42,
) -> Path:
    """Write the enriched dataset under ``data/<batch>/data/enriched_*.jsonl``.

    Args:
        batch_name: batch directory name under the data dir.
        model: teacher model name to stamp on every row. Falls back to the batch
            metadata's ``model`` field, else "unknown".
        use_postprocessed: prefer ``examples_postprocessed.jsonl``.
        filter_failed: drop examples with a FAIL (parallel_tool_calls / consecutive_roles).
        test_split: fraction held out for the test split.
        seed: shuffle seed.
    """
    batch_dir = data_dir() / batch_name
    src = batch_dir / "examples_postprocessed.jsonl"
    if not (use_postprocessed and src.exists()):
        src = batch_dir / "examples.jsonl"
    if not src.exists():
        raise FileNotFoundError(f"No examples file in {batch_dir}")

    metadata, examples = _read_jsonl(src)
    model = model or metadata.get("model") or "unknown"
    print(f"Loaded {len(examples)} examples from {src.name}; model = {model}")

    FAIL = {"parallel_tool_calls", "consecutive_roles"}

    def is_failed(ex: dict) -> bool:
        for r in (ex.get("validation") or {}).get("results", []):
            if r.get("param") in FAIL and r.get("status") == "❌":
                return True
        return False

    rows = []
    skipped_failed = skipped_noanswer = 0
    for ex in examples:
        if filter_failed and is_failed(ex):
            skipped_failed += 1
            continue
        row = enrich_example(ex, model)
        if row is None:
            skipped_noanswer += 1
            continue
        rows.append(row)

    if skipped_failed:
        print(f"Filtered {skipped_failed} FAILED examples")
    if skipped_noanswer:
        print(f"Skipped {skipped_noanswer} examples with no trailing assistant turn")

    random.seed(seed)
    random.shuffle(rows)
    test_size = int(len(rows) * test_split)
    train, test = rows[: len(rows) - test_size], rows[len(rows) - test_size :]

    out_dir = batch_dir / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    def _write(name: str, items: list):
        path = out_dir / name
        with open(path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Saved {len(items):,} rows -> {path}")
        return path

    _write("enriched_all.jsonl", rows)
    _write("enriched_train.jsonl", train)
    _write("enriched_test.jsonl", test)

    info = {
        "source_batch": batch_name,
        "model": model,
        "format": "enriched",
        "total": len(rows),
        "train": len(train),
        "test": len(test),
        "test_split": test_split,
        "seed": seed,
        "answer_split": "last_assistant_turn",
    }
    with open(out_dir / "enriched_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    print(f"\nEnriched export complete: {out_dir}")
    return out_dir
