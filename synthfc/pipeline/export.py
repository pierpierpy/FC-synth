#!/usr/bin/env python3
"""
Export an FC batch in a simple training format.

Output: only {"messages": [...], "tools": [...]} per example.
"""

import json
import sys
import random
import argparse
from pathlib import Path
from tqdm import tqdm

from ..config import data_dir


def load_batch(batch_name: str, use_postprocessed: bool = False) -> list:
    """Load examples from a batch."""
    batch_dir = data_dir() / batch_name

    if not batch_dir.exists():
        print(f"Batch not found: {batch_dir}")
        sys.exit(1)

    # Choose the file
    if use_postprocessed:
        jsonl_file = batch_dir / "examples_postprocessed.jsonl"
        if not jsonl_file.exists():
            print("Postprocessed file not found, using the original")
            jsonl_file = batch_dir / "examples.jsonl"
    else:
        jsonl_file = batch_dir / "examples.jsonl"

    if not jsonl_file.exists():
        print(f"File not found: {jsonl_file}")
        sys.exit(1)

    print(f"Loading: {jsonl_file}")

    examples = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            # Skip metadata
            if data.get("_metadata"):
                continue
            # Skip errors
            if data.get("error"):
                continue
            examples.append(data)

    return examples


def convert_example(ex: dict) -> dict:
    """Convert an example to the simple format."""
    messages = ex.get("messages", [])

    # Add system_prompt as the first message if present
    system_prompt = ex.get("system_prompt")
    if system_prompt:
        system_msg = {"role": "system", "content": system_prompt}
        messages = [system_msg] + messages

    return {
        "messages": messages,
        "tools": ex.get("tools", [])
    }


def has_parallel_tool_calls(ex: dict) -> bool:
    """Check whether an example has parallel tool calls (>1 tool_call per message)."""
    for m in ex.get("messages", []):
        if m.get("role") == "assistant" and m.get("tool_calls"):
            if len(m["tool_calls"]) > 1:
                return True
    return False


def is_failed(ex: dict) -> bool:
    """
    Check whether an example is FAILED.

    An example is failed ONLY if it has a FAIL in:
    - consecutive_roles
    - parallel_tool_calls

    The other checks (call_type, num_tool_calls, etc.) are treated as warnings.
    """
    # Fail criteria
    FAIL_CHECKS = ['consecutive_roles', 'parallel_tool_calls']
    
    validation = ex.get('validation', {})
    results = validation.get('results', [])
    
    for r in results:
        if r.get('param') in FAIL_CHECKS and r.get('status') == '❌':
            return True
    
    return False


def export_dataset(
    batch_name: str,
    output_name: str,
    test_split: float = 0.1,
    use_postprocessed: bool = False,
    seed: int = 42,
    filter_failed: bool = False
):
    """Export the dataset to train.jsonl and test.jsonl."""

    # Load
    examples = load_batch(batch_name, use_postprocessed)
    print(f"Loaded {len(examples):,} examples")

    # Filter failed examples (consecutive_roles or parallel_tool_calls)
    if filter_failed:
        original_count = len(examples)
        examples = [ex for ex in examples if not is_failed(ex)]
        filtered = original_count - len(examples)
        if filtered > 0:
            print(f"Filtered {filtered:,} FAILED examples (consecutive_roles or parallel_tool_calls)")
            print(f"   Remaining: {len(examples):,} examples")

    # Convert
    converted = [convert_example(ex) for ex in tqdm(examples, desc="Converting")]

    # Train/test split
    random.seed(seed)
    random.shuffle(converted)

    test_size = int(len(converted) * test_split)
    train_size = len(converted) - test_size

    train_data = converted[:train_size]
    test_data = converted[train_size:]

    print(f"Split: {len(train_data):,} train, {len(test_data):,} test ({test_split*100:.0f}%)")

    # Create the output directory inside the batch
    output_dir = data_dir() / batch_name / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save train
    train_path = output_dir / "train.jsonl"
    with open(train_path, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Saved: {train_path}")

    # Save test
    test_path = output_dir / "test.jsonl"
    with open(test_path, 'w', encoding='utf-8') as f:
        for item in test_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Saved: {test_path}")

    # Save all (full dataset)
    all_path = output_dir / "all.jsonl"
    with open(all_path, 'w', encoding='utf-8') as f:
        for item in converted:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Saved: {all_path}")

    # Save info
    info = {
        "source_batch": batch_name,
        "postprocessed": use_postprocessed,
        "total_examples": len(converted),
        "train_size": len(train_data),
        "test_size": len(test_data),
        "test_split": test_split,
        "seed": seed
    }
    info_path = output_dir / "info.json"
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"\nExport completed in: {output_dir}")
    return output_dir


def list_batches():
    """List available batches."""
    print("\nAvailable batches:")
    for d in sorted(data_dir().iterdir()):
        if d.is_dir():
            examples_file = d / "examples.jsonl"
            postproc_file = d / "examples_postprocessed.jsonl"

            # Count examples
            count = 0
            if examples_file.exists():
                with open(examples_file) as f:
                    count = sum(1 for line in f if line.strip() and '"_metadata"' not in line)

            postproc = " [postprocessed]" if postproc_file.exists() else ""
            print(f"  - {d.name} ({count:,} examples){postproc}")


def main():
    parser = argparse.ArgumentParser(
        description="Export an FC batch in a simple training format"
    )
    parser.add_argument(
        "batch_name",
        nargs="?",
        help="Name of the batch to export"
    )
    parser.add_argument(
        "--name", "-n",
        help="Output folder name (default: same as the batch name)"
    )
    parser.add_argument(
        "--test-split", "-t",
        type=float,
        default=0.1,
        help="Test set percentage (default: 0.1)"
    )
    parser.add_argument(
        "--postprocessed", "-p",
        action="store_true",
        default=True,
        help="Use the postprocessed file if available (default: True)"
    )
    parser.add_argument(
        "--raw", "-r",
        action="store_true",
        help="Use the original file instead of the postprocessed one"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed for the split (default: 42)"
    )
    parser.add_argument(
        "--no-failed", "-nf",
        action="store_true",
        help="Remove FAILED examples (consecutive_roles or parallel_tool_calls)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available batches"
    )

    args = parser.parse_args()

    if args.list or not args.batch_name:
        list_batches()
        if not args.batch_name:
            print("\nUsage: synthfc build <batch>")
        return

    output_name = args.name or args.batch_name

    use_postprocessed = not args.raw  # Default True, --raw disables it
    
    export_dataset(
        batch_name=args.batch_name,
        output_name=output_name,
        test_split=args.test_split,
        use_postprocessed=use_postprocessed,
        seed=args.seed,
        filter_failed=args.no_failed
    )


if __name__ == "__main__":
    main()
