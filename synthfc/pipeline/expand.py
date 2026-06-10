#!/usr/bin/env python3
"""
Conversation Cutter - Generate child conversations cut at natural points.

Logic:
    1. Find complete tool cycles: ASSISTANT[TC] -> TOOL -> ASSISTANT
       - Cut AFTER the assistant that follows the TOOL
    2. Find the last ASSISTANT with content BEFORE the first tool_call
       - At most 1 pre-tool cut (pure dialogue)

Constraints:
    - At least 4 messages (excluding system)
    - No duplicates (do not cut if cut == len(msgs))
    - Each child ends with an assistant message that has content
"""

import json
import random
import argparse
from pathlib import Path


def find_tool_cycles(msgs: list) -> list:
    """
    Find all complete tool cycles: ASSISTANT[TC] -> TOOL -> ASSISTANT

    Returns:
        List of tuples (tc_idx, tool_idx, assistant_idx)
    """
    cycles = []
    i = 0

    while i < len(msgs):
        m = msgs[i]

        # Look for an ASSISTANT with tool_calls
        if m.get('role') == 'assistant' and m.get('tool_calls'):
            tc_idx = i

            # Look for a TOOL right after (up to 2 msgs later for parallel calls)
            tool_idx = None
            for j in range(i + 1, min(i + 3, len(msgs))):
                if msgs[j].get('role') == 'tool':
                    tool_idx = j
                    break

            if tool_idx:
                # Look for an ASSISTANT with content after the TOOL
                assist_idx = None
                for j in range(tool_idx + 1, min(tool_idx + 3, len(msgs))):
                    if msgs[j].get('role') == 'assistant' and msgs[j].get('content'):
                        assist_idx = j
                        break

                if assist_idx:
                    cycles.append((tc_idx, tool_idx, assist_idx))
                    i = assist_idx
        i += 1

    return cycles


def find_cut_points(msgs: list) -> list:
    """
    Find all valid cut points.

    Returns:
        List of dicts with 'type' ('pre_tool' or 'post_tool') and 'cut_at' (index)
    """
    has_system = msgs[0].get('role') == 'system' if msgs else False
    min_msgs = 4  # excluding system

    cuts = []

    # Step 1: Find complete tool cycles
    tool_cycles = find_tool_cycles(msgs)

    # Step 2: Generate post-tool cuts (after each complete cycle)
    for tc_idx, tool_idx, assist_idx in tool_cycles:
        cut_idx = assist_idx + 1  # cut AFTER the assistant

        # Check constraints
        msgs_without_sys = cut_idx - (1 if has_system else 0)
        if msgs_without_sys < min_msgs:
            continue
        if cut_idx >= len(msgs):  # no duplicates
            continue

        cuts.append({
            'type': 'post_tool',
            'cut_at': cut_idx,
            'n_tools': len([c for c in tool_cycles if c[2] < cut_idx])
        })

    # Step 3: Find pre-tool cut (at most 1)
    first_tc_idx = tool_cycles[0][0] if tool_cycles else len(msgs)

    # Look for the last ASSISTANT with content BEFORE the first tool_call
    for i in range(first_tc_idx - 1, -1, -1):
        m = msgs[i]
        if m.get('role') == 'assistant' and m.get('content') and len(m.get('content', '')) > 10:
            cut_idx = i + 1
            msgs_without_sys = cut_idx - (1 if has_system else 0)
            if msgs_without_sys >= min_msgs and cut_idx < len(msgs):
                cuts.insert(0, {
                    'type': 'pre_tool',
                    'cut_at': cut_idx,
                    'n_tools': 0
                })
                break

    return cuts


def create_child_conversation(original: dict, cut_idx: int, cut_type: str, child_num: int) -> dict:
    """Create a child conversation by cutting at the given index."""
    msgs = original.get('messages', [])
    child_msgs = msgs[:cut_idx]

    # Copy the original metadata
    child = {
        'messages': child_msgs,
        'id': f"{original.get('id', 'unknown')}_cut{child_num}",
        'parent_id': original.get('id'),
        'cut_type': cut_type,
        'cut_at': cut_idx,
        'original_length': len(msgs),
    }
    
    # Copy other fields if present
    for key in ['params', 'tools', 'domain']:
        if key in original:
            child[key] = original[key]

    return child


def expand_dataset(input_path: Path, output_path: Path, percentage: int, seed: int = 42):
    """
    Expand the dataset by creating child conversations.
    The output contains: ALL originals + the children generated from the subset.

    Args:
        input_path: Path to the all.jsonl file
        output_path: Path for the expanded.jsonl file
        percentage: Percentage of conversations to generate children from (1-100)
        seed: Seed for reproducibility
    """
    random.seed(seed)

    # Read all conversations
    conversations = []
    with open(input_path) as f:
        for line in f:
            if line.strip():
                conversations.append(json.loads(line))

    total = len(conversations)
    n_to_process = int(total * percentage / 100)

    # Select a random subset to generate children from
    indices_to_process = set(random.sample(range(total), n_to_process))

    # Statistics
    stats = {
        'total_original': total,
        'processed': 0,
        'cuts_pre_tool': 0,
        'cuts_post_tool': 0,
        'children_created': 0,
        'no_cuts_available': 0
    }
    
    # Output: all originals + children
    output = []

    # First add ALL original conversations
    for convo in conversations:
        output.append(convo)

    # Then generate children from the selected subset
    for idx, convo in enumerate(conversations):
        if idx not in indices_to_process:
            continue

        stats['processed'] += 1
        msgs = convo.get('messages', [])
        cuts = find_cut_points(msgs)

        if not cuts:
            stats['no_cuts_available'] += 1
            continue

        # Create one child per cut point
        for child_num, cut in enumerate(cuts, 1):
            child = create_child_conversation(convo, cut['cut_at'], cut['type'], child_num)
            output.append(child)
            stats['children_created'] += 1
            
            if cut['type'] == 'pre_tool':
                stats['cuts_pre_tool'] += 1
            else:
                stats['cuts_post_tool'] += 1
    
    # Write output
    with open(output_path, 'w') as f:
        for item in output:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Generate child conversations cut at natural points'
    )
    parser.add_argument('input', help='Path to the all.jsonl file')
    parser.add_argument('percentage', type=int, help='Percentage of the dataset to process (1-100)')
    parser.add_argument('--output', '-o', help='Output path (default: expanded.jsonl in the same folder)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return 1

    output_path = Path(args.output) if args.output else input_path.parent / 'expanded.jsonl'

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Percentage: {args.percentage}%")
    print(f"Seed: {args.seed}")
    print()

    stats = expand_dataset(input_path, output_path, args.percentage, args.seed)

    print("=" * 50)
    print("STATISTICS")
    print("=" * 50)
    print(f"Original conversations: {stats['total_original']}")
    print(f"Processed for cuts ({args.percentage}%): {stats['processed']}")
    print(f"Without valid cuts: {stats['no_cuts_available']}")
    print()
    print(f"Children created: {stats['children_created']}")
    print(f"   - Pre-tool (pure dialogue): {stats['cuts_pre_tool']}")
    print(f"   - Post-tool (with cycles): {stats['cuts_post_tool']}")
    print()
    total_output = stats['total_original'] + stats['children_created']
    print(f"TOTAL OUTPUT: {total_output}")
    print(f"   - Originals: {stats['total_original']}")
    print(f"   - Children: {stats['children_created']}")
    print()
    print(f"Saved to: {output_path}")

    return 0


if __name__ == '__main__':
    exit(main())
