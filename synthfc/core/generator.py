"""
Batch Generator for the FC Dataset.
Generates conversations in batches and saves them with complete metadata.
Supports both sync and async generation with a semaphore for controlled parallelism.
"""

import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import time

from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm

from .sampler import sample_params, SampledParams
from .prompt_builder import generate_api_request
from .client import select_tools_for_params, call_api, call_api_async, convert_result
from ..config import get_config
from .validator import validate_example, ExampleValidation

from ..tools.ita import TOOLS_BY_CATEGORY as TOOLS_IT
from ..tools.eng import TOOLS_BY_CATEGORY as TOOLS_EN


@dataclass
class GeneratedExample:
    """A generated example with all its metadata."""
    id: str
    timestamp: str

    # Conversation data
    system_prompt: str
    messages: List[Dict]
    tools: List[Dict]

    # Requested parameter metadata
    params: Dict

    # Observed metrics (for validation)
    observed: Dict

    # Validation results
    validation: Optional[Dict] = None

    # Status
    generation_time_ms: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


def count_tool_calls(messages: List[Dict]) -> int:
    """Count the tool calls in the conversation."""
    count = 0
    for msg in messages:
        if msg.get('tool_calls'):
            count += len(msg['tool_calls'])
    return count


def find_first_tool_position(messages: List[Dict]) -> int:
    """Find the position (1-indexed) of the first assistant message with tool_calls."""
    for i, msg in enumerate(messages):
        if msg.get('role') == 'assistant' and msg.get('tool_calls'):
            return i + 1  # 1-indexed
    return 0


def count_messages(messages: List[Dict]) -> int:
    """Count the total number of messages."""
    return len(messages)


def detect_system_prompt_type(system_prompt: str) -> str:
    """Estimate the system prompt type based on its length."""
    if not system_prompt or system_prompt.strip() == "":
        return "none"
    
    words = len(system_prompt.split())
    if words <= 15:
        return "minimal"
    elif words <= 60:
        return "standard"
    else:
        return "detailed"


def detect_conversation_language(messages: List[Dict]) -> str:
    """Detect the dominant language of the conversation."""
    # Common Italian words
    italian_markers = ['ciao', 'buongiorno', 'grazie', 'prego', 'vorrei', 'potrei',
                       'per favore', 'gentilmente', 'aiuto', 'problema', 'cosa', 'come',
                       'quando', 'dove', 'perché', 'quale', 'quanto', 'sono', 'ho', 'hai',
                       'è', 'siamo', 'volete', 'posso', 'puoi', 'deve', 'devo']
    
    text = " ".join([m.get('content', '') or '' for m in messages]).lower()
    
    italian_count = sum(1 for word in italian_markers if word in text)
    
    return "it" if italian_count >= 3 else "en"


def extract_observed_metrics(result: Dict) -> Dict:
    """Extract the observable metrics from the generated conversation."""
    messages = result.get('messages', [])
    system_prompt = result.get('system_prompt', '')
    
    return {
        'num_tool_calls': count_tool_calls(messages),
        'first_tool_position': find_first_tool_position(messages),
        'num_messages': count_messages(messages),
        'system_prompt_type': detect_system_prompt_type(system_prompt),
        'conversation_language': detect_conversation_language(messages),
        'has_system_prompt': bool(system_prompt and system_prompt.strip()),
    }


def generate_single(params: Optional[SampledParams] = None) -> GeneratedExample:
    """
    Generate a single example with metadata.

    Args:
        params: parameters to use (if None, sample at random)

    Returns:
        GeneratedExample with data and metadata
    """
    if params is None:
        params = sample_params()

    example_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    # Select tools
    tools = select_tools_for_params(
        tool_language=params.tool_language,
        categories=params.tool_categories,
        num_tools=params.num_tools_available,
        tools_it=TOOLS_IT,
        tools_en=TOOLS_EN
    )

    # Build the API request
    api_request = generate_api_request(params, tools)

    # Call the API
    start_time = time.time()
    try:
        result = call_api(api_request)
        generation_time = int((time.time() - start_time) * 1000)
        
        if "error" in result:
            return GeneratedExample(
                id=example_id,
                timestamp=timestamp,
                system_prompt="",
                messages=[],
                tools=tools,
                params=params.to_dict(),
                observed={},
                validation=None,
                generation_time_ms=generation_time,
                error=result["error"]
            )
        
        # Convert the result
        final = convert_result(result, tools)

        # Extract observed metrics
        observed = extract_observed_metrics(final)

        # Validate the example
        example_for_validation = {
            'id': example_id,
            'params': params.to_dict(),
            'observed': observed,
            'messages': final.get('messages', []),
            'system_prompt': final.get('system_prompt', '')
        }
        validation_result = validate_example(example_for_validation)
        
        return GeneratedExample(
            id=example_id,
            timestamp=timestamp,
            system_prompt=final.get('system_prompt', ''),
            messages=final.get('messages', []),
            tools=final.get('tools', tools),
            params=params.to_dict(),
            observed=observed,
            validation=validation_result.to_dict(),
            generation_time_ms=generation_time,
            error=None
        )
        
    except Exception as e:
        generation_time = int((time.time() - start_time) * 1000)
        return GeneratedExample(
            id=example_id,
            timestamp=timestamp,
            system_prompt="",
            messages=[],
            tools=tools,
            params=params.to_dict(),
            observed={},
            validation=None,
            generation_time_ms=generation_time,
            error=str(e)
        )


def generate_batch(
    n: int = None,
    output_file: Optional[str] = None,
    verbose: bool = True
) -> List[GeneratedExample]:
    """
    Generate a batch of examples.

    Args:
        n: number of examples to generate (default: from config)
        output_file: JSONL file to save to (optional)
        verbose: show progress with tqdm

    Returns:
        List of GeneratedExample
    """
    cfg = get_config()

    if n is None:
        n = cfg.generation.batch_size

    delay = cfg.generation.delay_between_calls
    checkpoint_every = cfg.generation.checkpoint_every

    examples = []
    errors = 0

    # Set up the progress bar
    pbar = tqdm(range(n), desc="Generating", disable=not verbose)

    for i in pbar:
        example = generate_single()
        examples.append(example)

        if example.error:
            errors += 1
            pbar.set_postfix(errors=errors)

        # Checkpoint - save in the same folder as the main file
        if checkpoint_every > 0 and output_file and (i + 1) % checkpoint_every == 0:
            output_path = Path(output_file)
            checkpoint_file = output_path.parent / f"checkpoint_{i+1}.jsonl"
            save_batch(examples, str(checkpoint_file))
            pbar.set_description(f"Checkpoint saved ({i+1})")

        # Rate limiting
        time.sleep(delay)

    pbar.close()

    if verbose:
        print(f"Generated {n} examples ({errors} errors)")

    # Save if requested
    if output_file:
        save_batch(examples, output_file)
        if verbose:
            print(f"Saved to {output_file}")

    return examples


def save_batch(examples: List[GeneratedExample], filepath: str):
    """Save a batch of examples to JSONL (one line per example)."""
    cfg = get_config()

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        # First line: metadata
        metadata = {
            "_metadata": True,
            "generated_at": datetime.now().isoformat(),
            "count": len(examples),
            "errors": sum(1 for e in examples if e.error),
            "version": "1.0",
            "model": cfg.model.model,
            "temperature": cfg.model.temperature,
        }
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")

        # The rest: examples
        for ex in examples:
            f.write(json.dumps(ex.to_dict(), ensure_ascii=False) + "\n")


def load_batch(filepath: str) -> List[GeneratedExample]:
    """Load a batch of examples from JSONL."""
    examples = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            # Skip the metadata line
            if data.get("_metadata"):
                continue
            examples.append(GeneratedExample(**data))

    return examples


# =============================================================================
# ASYNC GENERATION
# =============================================================================

async def generate_single_async(
    params: Optional[SampledParams] = None,
    semaphore: Optional[asyncio.Semaphore] = None
) -> GeneratedExample:
    """
    Generate a single example with metadata (async).

    Args:
        params: parameters to use (if None, sample at random)
        semaphore: semaphore to limit concurrency

    Returns:
        GeneratedExample with data and metadata
    """
    if params is None:
        params = sample_params()

    example_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    # Select tools
    tools = select_tools_for_params(
        tool_language=params.tool_language,
        categories=params.tool_categories,
        num_tools=params.num_tools_available,
        tools_it=TOOLS_IT,
        tools_en=TOOLS_EN
    )

    # Build the API request
    api_request = generate_api_request(params, tools)

    # Call the API with the semaphore
    start_time = time.time()
    try:
        if semaphore:
            async with semaphore:
                result = await call_api_async(api_request)
        else:
            result = await call_api_async(api_request)
        
        generation_time = int((time.time() - start_time) * 1000)
        
        if "error" in result:
            return GeneratedExample(
                id=example_id,
                timestamp=timestamp,
                system_prompt="",
                messages=[],
                tools=tools,
                params=params.to_dict(),
                observed={},
                validation=None,
                generation_time_ms=generation_time,
                error=result["error"]
            )
        
        # Convert the result
        final = convert_result(result, tools)

        # Extract observed metrics
        observed = extract_observed_metrics(final)

        # Validate the example
        example_for_validation = {
            'id': example_id,
            'params': params.to_dict(),
            'observed': observed,
            'messages': final.get('messages', []),
            'system_prompt': final.get('system_prompt', '')
        }
        validation_result = validate_example(example_for_validation)
        
        return GeneratedExample(
            id=example_id,
            timestamp=timestamp,
            system_prompt=final.get('system_prompt', ''),
            messages=final.get('messages', []),
            tools=final.get('tools', tools),
            params=params.to_dict(),
            observed=observed,
            validation=validation_result.to_dict(),
            generation_time_ms=generation_time,
            error=None
        )
        
    except Exception as e:
        generation_time = int((time.time() - start_time) * 1000)
        return GeneratedExample(
            id=example_id,
            timestamp=timestamp,
            system_prompt="",
            messages=[],
            tools=tools,
            params=params.to_dict(),
            observed={},
            validation=None,
            generation_time_ms=generation_time,
            error=str(e)
        )


async def generate_batch_async(
    n: int = None,
    output_file: Optional[str] = None,
    verbose: bool = True,
    concurrency: int = None
) -> List[GeneratedExample]:
    """
    Generate a batch of examples asynchronously with controlled parallelism.

    Args:
        n: number of examples to generate (default: from config)
        output_file: JSONL file to save to (optional)
        verbose: show progress
        concurrency: number of parallel calls (default: from config)

    Returns:
        List of GeneratedExample
    """
    cfg = get_config()

    if n is None:
        n = cfg.generation.batch_size

    if concurrency is None:
        concurrency = cfg.generation.concurrency

    checkpoint_every = cfg.generation.checkpoint_every

    # Create the semaphore
    semaphore = asyncio.Semaphore(concurrency)

    if verbose:
        print(f"Generating {n} examples with concurrency={concurrency}")

    # Pre-sample all parameters
    all_params = [sample_params() for _ in range(n)]

    # Generate all of them in parallel with the semaphore
    tasks = [generate_single_async(params, semaphore) for params in all_params]

    # Use async tqdm to show progress
    if verbose:
        examples = []
        for coro in atqdm(asyncio.as_completed(tasks), total=n, desc="Generating"):
            example = await coro
            examples.append(example)

            # Checkpoint
            if checkpoint_every > 0 and output_file and len(examples) % checkpoint_every == 0:
                output_path = Path(output_file)
                checkpoint_file = output_path.parent / f"checkpoint_{len(examples)}.jsonl"
                save_batch(examples, str(checkpoint_file))
    else:
        examples = await asyncio.gather(*tasks)

    errors = sum(1 for e in examples if e.error)

    if verbose:
        print(f"Generated {n} examples ({errors} errors)")

    # Save if requested
    if output_file:
        # Sort by timestamp for a consistent order
        examples.sort(key=lambda x: x.timestamp)
        save_batch(examples, output_file)
        if verbose:
            print(f"Saved to {output_file}")

    return examples


if __name__ == "__main__":
    # Quick test
    print("Testing batch generator...")
    examples = generate_batch(2, verbose=True)
    for ex in examples:
        print(f"\n--- Example {ex.id} ---")
        print(f"Params: call_type={ex.params['call_type']}, style={ex.params['user_style']}")
        print(f"Observed: {ex.observed}")
        if ex.error:
            print(f"ERROR: {ex.error}")
