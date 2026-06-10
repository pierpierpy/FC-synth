#!/usr/bin/env python3
"""
Revalidate script - revalidate existing batches with the current validator.
"""

import sys
import json
import argparse
from pathlib import Path

from ..core.validator import validate_batch, print_validation_summary


def parse_jsonl(file_path: Path) -> list:
    """Parse a JSONL file and return a list of examples."""
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARNING: error parsing line {line_num}: {e}")
    return examples


def validate_path(path: Path) -> dict:
    """
    Validate a batch folder or a .jsonl file.

    If given a folder, validate its examples_postprocessed.jsonl if present,
    otherwise examples.jsonl. The examples are parsed, validated with
    validate_batch, summarized, and the results are written to
    validation_results.json next to the input.

    Returns:
        The validation result dict.
    """
    path = Path(path)

    # Find the JSONL file
    if path.is_dir():
        jsonl_file = path / "examples_postprocessed.jsonl"
        if not jsonl_file.exists():
            jsonl_file = path / "examples.jsonl"
        if not jsonl_file.exists():
            # Fall back to any jsonl file in the folder
            jsonl_files = list(path.glob("*.jsonl"))
            if jsonl_files:
                jsonl_file = jsonl_files[0]
            else:
                print(f"ERROR: no JSONL file found in {path}")
                sys.exit(1)
    else:
        jsonl_file = path

    print(f"Revalidating: {jsonl_file}")

    # Load examples
    examples = parse_jsonl(jsonl_file)
    print(f"Loaded {len(examples)} examples")

    if not examples:
        print("No examples to validate")
        sys.exit(1)

    # Validate
    result = validate_batch(examples)

    # Print summary
    print_validation_summary(result)

    # Save result
    output_path = jsonl_file.parent / "validation_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {output_path}")

    # Update the JSONL file with the new validations
    validation_by_id = {v['example_id']: v for v in result['validations']}

    updated_examples = []
    for ex in examples:
        ex_id = ex.get('id', 'unknown')
        if ex_id in validation_by_id:
            ex['validation'] = validation_by_id[ex_id]
        updated_examples.append(ex)

    # Overwrite the file
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for ex in updated_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    print(f"Updated JSONL: {jsonl_file}")

    # If a postprocessed file also exists, update it too
    postproc_file = jsonl_file.parent / "examples_postprocessed.jsonl"
    if postproc_file.exists() and postproc_file != jsonl_file:
        postproc_examples = parse_jsonl(postproc_file)
        updated_postproc = []
        for ex in postproc_examples:
            ex_id = ex.get('id', 'unknown')
            if ex_id in validation_by_id:
                ex['validation'] = validation_by_id[ex_id]
            updated_postproc.append(ex)

        with open(postproc_file, 'w', encoding='utf-8') as f:
            for ex in updated_postproc:
                f.write(json.dumps(ex, ensure_ascii=False) + '\n')
        print(f"Updated postprocessed: {postproc_file}")

    # Specific report for consecutive_roles
    consecutive_fails = 0
    for v in result['validations']:
        for r in v['results']:
            if r['param'] == 'consecutive_roles' and r['status'] == '❌':
                consecutive_fails += 1
                print(f"  {v['example_id']}: {r['message']}")

    if consecutive_fails > 0:
        print(f"\nWARNING: {consecutive_fails} examples have consecutive assistant messages")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Revalidate an existing batch with the current validator"
    )
    parser.add_argument(
        "path",
        help="Path to the batch folder or a .jsonl file"
    )
    args = parser.parse_args()

    validate_path(Path(args.path))


if __name__ == "__main__":
    main()
