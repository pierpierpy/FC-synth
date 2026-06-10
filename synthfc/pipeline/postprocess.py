#!/usr/bin/env python3
"""
Post-processing for the FC dataset.
Fixes structural issues in generated messages:
1. Merge consecutive user messages
2. Remove assistant reflections before a tool_call (only when preceded by a user message)
"""

import json
import sys
import copy
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class PostProcessStats:
    total_examples: int = 0
    examples_modified: int = 0
    user_user_merged: int = 0
    reflections_removed: int = 0
    tool_call_loop_removed: int = 0  # Examples with >N tool_calls in a single message
    
    def __str__(self):
        return f"""
Post-Processing Stats:
  Total examples:      {self.total_examples}
  Examples modified:   {self.examples_modified}
  User-user merged:    {self.user_user_merged}
  Reflections removed: {self.reflections_removed}
  Tool-call loops:     {self.tool_call_loop_removed} (removed)
"""


MAX_TOOL_CALLS_PER_MESSAGE = 5


def has_tool_call_loop(messages: List[Dict]) -> bool:
    """
    Check whether an example has the tool_call loop bug:
    a single assistant message with too many tool_calls.
    """
    for msg in messages:
        if msg.get('role') == 'assistant' and msg.get('tool_calls'):
            if len(msg['tool_calls']) > MAX_TOOL_CALLS_PER_MESSAGE:
                return True
    return False


def find_prev_non_assistant(messages: List[Dict], idx: int) -> str:
    """Find the role of the previous non-assistant message."""
    for j in range(idx - 1, -1, -1):
        if messages[j].get('role') != 'assistant':
            return messages[j].get('role')
    return None


def is_tool_call_message(msg: Dict) -> bool:
    """Check whether an assistant message has tool_calls."""
    return msg.get('role') == 'assistant' and msg.get('tool_calls')


def is_content_message(msg: Dict) -> bool:
    """Check whether an assistant message only has content (no tool_calls)."""
    return (msg.get('role') == 'assistant' and 
            msg.get('content') and 
            not msg.get('tool_calls'))


def postprocess_messages(messages: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Process a list of messages and fix the issues.

    Handled cases:
    1. consecutive user-user -> merge
    2. user -> assistant(content) -> assistant(tool_call) -> remove the first assistant
    3. user -> assistant(content) -> assistant(content) -> remove the first assistant (useless transition)

    Returns:
        (fixed_messages, stats_dict)
    """
    if not messages:
        return messages, {'user_merged': 0, 'reflections_removed': 0}
    
    stats = {'user_merged': 0, 'reflections_removed': 0}
    result = []
    i = 0
    
    while i < len(messages):
        msg = messages[i]
        role = msg.get('role')
        
        # CASE 1: consecutive user-user -> merge
        if role == 'user':
            merged_content = [msg.get('content', '')]
            j = i + 1
            while j < len(messages) and messages[j].get('role') == 'user':
                merged_content.append(messages[j].get('content', ''))
                stats['user_merged'] += 1
                j += 1

            # Build merged message
            new_msg = copy.deepcopy(msg)
            new_msg['content'] = '\n'.join(c for c in merged_content if c)
            result.append(new_msg)
            i = j
            continue
        
        # CASE 2: assistant-assistant where the first is a reflection/transition
        if role == 'assistant' and is_content_message(msg):
            # Check whether the next one is also assistant (with tool_call OR with content)
            if i + 1 < len(messages) and messages[i + 1].get('role') == 'assistant':
                next_msg = messages[i + 1]
                next_is_tool = is_tool_call_message(next_msg)
                next_is_content = is_content_message(next_msg)

                if next_is_tool or next_is_content:
                    # Find what came before
                    prev_role = None
                    for j in range(len(result) - 1, -1, -1):
                        if result[j].get('role') != 'assistant':
                            prev_role = result[j].get('role')
                            break

                    # If a USER came before -> this is a reflection/transition, skip it
                    if prev_role == 'user':
                        stats['reflections_removed'] += 1
                        i += 1
                        continue

        # Normal message, append
        result.append(copy.deepcopy(msg))
        i += 1
    
    return result, stats


def find_first_tool_position(messages: List[Dict]) -> int:
    """Find the position of the first tool call."""
    for i, msg in enumerate(messages):
        if msg.get('role') == 'assistant' and msg.get('tool_calls'):
            return i
    return 0


def postprocess_example(example: Dict) -> Tuple[Dict, Dict]:
    """
    Post-process a single example.

    Returns:
        (fixed_example, stats_dict)
    """
    messages = example.get('messages', [])
    new_messages, stats = postprocess_messages(messages)

    new_example = copy.deepcopy(example)
    new_example['messages'] = new_messages

    # Fully recompute observed
    num_tool_calls = sum(
        len(m.get('tool_calls', [])) 
        for m in new_messages 
        if m.get('tool_calls')
    )
    new_example['observed'] = {
        'num_messages': len(new_messages),
        'num_tool_calls': num_tool_calls,
        'first_tool_position': find_first_tool_position(new_messages)
    }
    
    # Re-validate with the new messages
    try:
        from ..core.validator import validate_example
        v = validate_example(new_example)
        # Convert to a serializable dict
        new_example['validation'] = {
            'example_id': v.example_id,
            'score': v.score,
            'passed': v.passed,
            'failed': v.failed,
            'warnings': v.warnings,
            'results': [
                {
                    'param': r.param_name,
                    'expected': r.expected,
                    'observed': r.observed,
                    'status': r.status.value,
                    'message': r.message
                }
                for r in v.results
            ]
        }
    except Exception:
        # If validation fails, keep the original one
        pass

    # Mark as post-processed
    new_example['postprocessed'] = True
    new_example['postprocess_stats'] = stats
    
    return new_example, stats


def postprocess_batch(input_path: Path, dry_run: bool = False) -> PostProcessStats:
    """
    Post-process an entire batch.

    Args:
        input_path: path to the batch folder or jsonl file
        dry_run: if True, do not save but only show the changes

    Returns:
        PostProcessStats
    """
    # Find the JSONL file
    if input_path.is_dir():
        jsonl_file = input_path / "examples.jsonl"
    else:
        jsonl_file = input_path

    if not jsonl_file.exists():
        print(f"ERROR: file not found: {jsonl_file}")
        sys.exit(1)

    # Read examples
    examples = []
    metadata = None

    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            if data.get('_metadata'):
                metadata = data
            else:
                examples.append(data)
    
    print(f"Loaded {len(examples)} examples from {jsonl_file}")

    # Post-process
    stats = PostProcessStats(total_examples=len(examples))
    processed_examples = []

    for ex in examples:
        messages = ex.get('messages', [])
        if has_tool_call_loop(messages):
            stats.tool_call_loop_removed += 1
            if dry_run:
                max_tc = max(
                    len(m.get('tool_calls', []))
                    for m in messages
                    if m.get('tool_calls')
                )
                print(f"\n--- REMOVED: {ex.get('id')} (tool_call loop: {max_tc} in single msg) ---")
            continue  # Skip this example

        new_ex, ex_stats = postprocess_example(ex)
        processed_examples.append(new_ex)

        if ex_stats['user_merged'] > 0 or ex_stats['reflections_removed'] > 0:
            stats.examples_modified += 1
            stats.user_user_merged += ex_stats['user_merged']
            stats.reflections_removed += ex_stats['reflections_removed']

            if dry_run:
                print(f"\n--- Example {ex.get('id')} ---")
                print(f"  User merged: {ex_stats['user_merged']}")
                print(f"  Reflections removed: {ex_stats['reflections_removed']}")

                # Show diff
                old_len = len(ex.get('messages', []))
                new_len = len(new_ex.get('messages', []))
                print(f"  Messages: {old_len} -> {new_len}")

    print(stats)

    if dry_run:
        print("DRY RUN - no file saved")
        return stats

    # Save post-processed file
    output_file = jsonl_file.parent / "examples_postprocessed.jsonl"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Updated metadata
        if metadata:
            metadata['postprocessed'] = True
            metadata['postprocess_stats'] = {
                'examples_modified': stats.examples_modified,
                'user_merged': stats.user_user_merged,
                'reflections_removed': stats.reflections_removed,
                'tool_call_loop_removed': stats.tool_call_loop_removed
            }
            f.write(json.dumps(metadata, ensure_ascii=False) + '\n')

        # Examples
        for ex in processed_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"Saved to: {output_file}")
    
    return stats


def main():
    if len(sys.argv) < 2:
        print("Usage: synthfc postprocess <batch_folder> [--dry-run]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    dry_run = '--dry-run' in sys.argv
    
    postprocess_batch(input_path, dry_run=dry_run)


if __name__ == "__main__":
    main()
