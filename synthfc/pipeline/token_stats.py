"""Token / length statistics for an exported dataset.

If a Hugging Face tokenizer is provided, counts are computed after applying its
chat template (the realistic training-time token count). Otherwise a rough
whitespace word count is used so the command works without ``transformers``.
"""

from __future__ import annotations

import json
from typing import List, Optional


def _load_jsonl(path: str) -> List[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def report(dataset: str, tokenizer: Optional[str] = None) -> None:
    """Print length statistics for ``dataset``.

    Args:
        dataset: path to a JSONL file with ``messages`` (+ optional ``tools``).
        tokenizer: optional HF tokenizer name/path. When given, lengths are real
            token counts after applying the chat template; otherwise word counts.
    """
    convos = _load_jsonl(dataset)
    print(f"Conversations: {len(convos)}")

    counts: List[int] = []
    errors = 0

    if tokenizer:
        from transformers import AutoTokenizer

        print(f"Loading tokenizer: {tokenizer}")
        tok = AutoTokenizer.from_pretrained(tokenizer, trust_remote_code=True)
        for i, c in enumerate(convos):
            try:
                messages = c.get("messages", [])
                tools = c.get("tools", [])
                if tools:
                    text = tok.apply_chat_template(messages, tools=tools, tokenize=False)
                else:
                    text = tok.apply_chat_template(messages, tokenize=False)
                counts.append(len(tok.encode(text)))
            except Exception as e:  # noqa: BLE001
                errors += 1
                if errors <= 3:
                    print(f"  error on conversation {i}: {e}")
        unit = "tokens"
    else:
        print("No tokenizer given — reporting whitespace word counts.")
        for c in convos:
            text = " ".join(
                (m.get("content") or "") for m in c.get("messages", [])
            )
            counts.append(len(text.split()))
        unit = "words"

    if not counts:
        print("No measurable conversations.")
        return

    counts.sort()
    n = len(counts)

    def pct(p: float) -> int:
        idx = min(n - 1, int(p / 100 * n))
        return counts[idx]

    total = sum(counts)
    print(f"\nLength statistics ({unit}):")
    print(f"  count:   {n}")
    print(f"  errors:  {errors}")
    print(f"  min:     {counts[0]:,}")
    print(f"  max:     {counts[-1]:,}")
    print(f"  mean:    {total / n:,.1f}")
    print(f"  median:  {pct(50):,}")
    print("  percentiles:")
    for p in (90, 95, 99):
        print(f"    P{p}: {pct(p):,}")
    print(f"  total:   {total:,}")
