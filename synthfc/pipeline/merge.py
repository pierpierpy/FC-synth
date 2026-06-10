"""Merge several exported JSONL datasets into one.

Ensures every conversation ends with an assistant turn (a trailing ``user``
message is dropped) and optionally removes duplicate conversations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


def _load_jsonl(path: str) -> List[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _fix_ending(sample: dict) -> dict:
    """Drop a trailing ``user`` message so the conversation ends with assistant."""
    messages = sample.get("messages")
    if messages and messages[-1].get("role") == "user":
        sample["messages"] = messages[:-1]
    return sample


def _key(sample: dict) -> str:
    return json.dumps(sample.get("messages", []), ensure_ascii=False, sort_keys=True)


def merge_datasets(inputs: List[str], output: str, dedup: bool = True) -> int:
    """Merge ``inputs`` into ``output``.

    Args:
        inputs: paths to JSONL dataset files.
        output: destination JSONL path.
        dedup: drop duplicate conversations (by message content).

    Returns:
        Number of conversations written.
    """
    merged: List[dict] = []
    seen = set()

    for path in inputs:
        for sample in _load_jsonl(path):
            sample = _fix_ending(sample)
            # Require at least a system/user turn plus an assistant turn.
            if len(sample.get("messages", [])) < 2:
                continue
            if dedup:
                k = _key(sample)
                if k in seen:
                    continue
                seen.add(k)
            merged.append(sample)

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for sample in merged:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    return len(merged)
