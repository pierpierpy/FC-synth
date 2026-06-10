"""LLM client and result conversion.

Provider-agnostic: works with any OpenAI-compatible endpoint (OpenAI, vLLM,
Together, Groq, a local server, ...) or with Azure OpenAI, selected via the
``provider`` config field. Credentials are read from the environment only —
never from the YAML config or this file.
"""

from __future__ import annotations

import json
import random
from typing import Dict, List, Optional

from openai import AsyncOpenAI, OpenAI

try:
    from ..config import get_config
except ImportError:  # pragma: no cover - fallback for direct execution
    from synthfc.config import get_config


# =============================================================================
# CLIENT (lazy initialization)
# =============================================================================

_client = None
_async_client = None


def _build_clients():
    """Create (sync, async) clients for the configured provider."""
    cfg = get_config().model

    if not cfg.api_key:
        raise RuntimeError(
            "No API key found. Set SYNTHFC_API_KEY (or OPENAI_API_KEY) in your "
            "environment. See .env.example."
        )

    if cfg.provider == "azure":
        from openai import AsyncAzureOpenAI, AzureOpenAI

        if not cfg.endpoint:
            raise RuntimeError(
                "provider='azure' requires SYNTHFC_ENDPOINT to be set to your "
                "Azure OpenAI resource endpoint."
            )
        sync = AzureOpenAI(
            api_key=cfg.api_key,
            api_version=cfg.api_version,
            azure_endpoint=cfg.endpoint,
        )
        asyncc = AsyncAzureOpenAI(
            api_key=cfg.api_key,
            api_version=cfg.api_version,
            azure_endpoint=cfg.endpoint,
        )
    else:
        # OpenAI-compatible. base_url is optional (defaults to OpenAI's API).
        kwargs = {"api_key": cfg.api_key}
        if cfg.endpoint:
            kwargs["base_url"] = cfg.endpoint
        sync = OpenAI(**kwargs)
        asyncc = AsyncOpenAI(**kwargs)

    return sync, asyncc


def get_client():
    """Return the lazily-initialized synchronous client."""
    global _client, _async_client
    if _client is None:
        _client, _async_client = _build_clients()
    return _client


def get_async_client():
    """Return the lazily-initialized asynchronous client."""
    global _client, _async_client
    if _async_client is None:
        _client, _async_client = _build_clients()
    return _async_client


def get_model() -> str:
    """Return the model / deployment name from config."""
    return get_config().model.model


# =============================================================================
# CATEGORY MAPPINGS
# =============================================================================

CATEGORY_MAP_EN_TO_IT = {
    "weather": "meteo",
    "finance": "finanza",
    "calendar": "calendario",
    "search": "ricerca",
    "communication": "comunicazione",
    "productivity": "produttivita",
    "travel": "viaggi",
    "ecommerce": "ecommerce",
    "smart_home": "casa_smart",
    "media": "media",
    "health": "salute",
    "utilities": "utilita",
    "database": "database",
    "documents": "documenti",
    "social_media": "social",
    "code": "codice",
    "booking": "prenotazioni",
    "news": "notizie",
    "government": "pubblica_amministrazione",
    "iot": "iot",
    "crm": "crm",
    "knowledge_base": "knowledge_base",
}

CATEGORY_MAP_IT_TO_EN = {v: k for k, v in CATEGORY_MAP_EN_TO_IT.items()}


# =============================================================================
# RESPONSE SCHEMA
# =============================================================================

RESPONSE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "conversation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "system_prompt": {
                    "type": ["string", "null"],
                    "description": "Conversation system prompt, null if absent",
                },
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["user", "assistant", "tool"],
                            },
                            "content": {"type": ["string", "null"]},
                            "tool_calls": {
                                "anyOf": [
                                    {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "type": {"type": "string"},
                                                "function": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "arguments": {"type": "string"},
                                                    },
                                                    "required": ["name", "arguments"],
                                                    "additionalProperties": False,
                                                },
                                            },
                                            "required": ["id", "type", "function"],
                                            "additionalProperties": False,
                                        },
                                    },
                                    {"type": "null"},
                                ]
                            },
                            "tool_call_id": {"type": ["string", "null"]},
                        },
                        "required": ["role", "content", "tool_calls", "tool_call_id"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["system_prompt", "messages"],
            "additionalProperties": False,
        },
    },
}


# =============================================================================
# RESULT CONVERTER — turns API output into the clean training format
# =============================================================================

def convert_result(api_result: dict, tools: List[dict]) -> dict:
    """Convert raw API output into the final clean training format.

    Args:
        api_result: output from :func:`call_api` with ``system_prompt`` and ``messages``.
        tools: the list of tool definitions used.

    Returns:
        dict with ``system_prompt``, ``messages`` and ``tools`` ready for training.
    """
    clean_messages = []

    for msg in api_result.get("messages", []):
        role = msg["role"]
        content = msg.get("content")
        tool_calls = msg.get("tool_calls")
        tool_call_id = msg.get("tool_call_id")

        clean_msg = {"role": role}

        if role == "user":
            clean_msg["content"] = content

        elif role == "assistant":
            if tool_calls and len(tool_calls) > 0:
                # Assistant tool call: role + tool_calls (no content).
                clean_msg["tool_calls"] = tool_calls
            else:
                clean_msg["content"] = content

        elif role == "tool":
            clean_msg["content"] = content
            clean_msg["tool_call_id"] = tool_call_id

        clean_messages.append(clean_msg)

    clean_tools = [
        {"type": tool["type"], "function": tool["function"]} for tool in tools
    ]

    return {
        "system_prompt": api_result.get("system_prompt"),
        "messages": clean_messages,
        "tools": clean_tools,
    }


# =============================================================================
# TOOL SELECTOR
# =============================================================================

def select_tools_for_params(
    tool_language: str,
    categories: List[str],
    num_tools: int,
    tools_it: Dict[str, List[dict]],
    tools_en: Dict[str, List[dict]],
) -> List[dict]:
    """Pick a random subset of tools given language and categories.

    Args:
        tool_language: ``"it"`` or ``"en"``.
        categories: category names from the sampler (in English form).
        num_tools: how many tools to select.
        tools_it: Italian category -> tools mapping.
        tools_en: English category -> tools mapping.

    Returns:
        A list of tool definitions.
    """
    if tool_language == "it":
        it_categories = [CATEGORY_MAP_EN_TO_IT.get(c, c) for c in categories]
        pool: List[dict] = []
        for cat in it_categories:
            pool.extend(tools_it.get(cat, []))
    else:
        pool = []
        for cat in categories:
            pool.extend(tools_en.get(cat, []))

    # Fall back to the full catalogue if no tools matched the categories.
    if not pool:
        source = tools_it if tool_language == "it" else tools_en
        for tools_list in source.values():
            pool.extend(tools_list)

    return random.sample(pool, min(num_tools, len(pool)))


# =============================================================================
# API CALLER
# =============================================================================

def call_api(api_request: dict, model: Optional[str] = None, client=None) -> dict:
    """Call the chat completions API with the conversation schema (sync).

    Args:
        api_request: dict with ``messages`` and optionally ``temperature``.
        model: model / deployment name (default: from config).
        client: client instance (default: from config).

    Returns:
        The generated conversation as a dict.
    """
    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    cfg = get_config().model

    response = client.chat.completions.create(
        model=model,
        messages=api_request["messages"],
        response_format=RESPONSE_SCHEMA,
        temperature=api_request.get("temperature", cfg.temperature),
        top_p=cfg.top_p,
    )
    return json.loads(response.choices[0].message.content)


async def call_api_async(api_request: dict, model: Optional[str] = None, client=None) -> dict:
    """Call the chat completions API with the conversation schema (async).

    Args:
        api_request: dict with ``messages`` and optionally ``temperature``.
        model: model / deployment name (default: from config).
        client: async client instance (default: from config).

    Returns:
        The generated conversation as a dict.
    """
    if client is None:
        client = get_async_client()
    if model is None:
        model = get_model()

    cfg = get_config().model

    response = await client.chat.completions.create(
        model=model,
        messages=api_request["messages"],
        response_format=RESPONSE_SCHEMA,
        temperature=api_request.get("temperature", cfg.temperature),
        top_p=cfg.top_p,
    )
    return json.loads(response.choices[0].message.content)


# =============================================================================
# PRINT EXAMPLE
# =============================================================================

def print_example(params: dict, tools: List[dict], result: dict):
    """Pretty-print a generated example: sampled params + the conversation."""
    print("=" * 70)
    print("INPUT PARAMETERS")
    print("=" * 70)

    call_type = params["call_type"]
    if call_type == "positive":
        subtype = params["positive_type"]
    elif call_type == "negative":
        subtype = params["negative_reason"]
    else:
        subtype = params["clarification_outcome"]
    print(f"Call type:       {call_type} / {subtype}")

    print(f"Language:        {params['conversation_language']} (tools: {params['tool_language']})")
    print(f"Length:          {params['conversation_length']}")
    print(f"User style:      {params['user_style']}")
    print(f"History type:    {params['history_type']}")
    print(f"System prompt:   {params['system_prompt_type']}")
    print(f"Num tool calls:  {params['num_tool_calls']}")
    print(f"First tool pos:  {params['first_tool_position']}")
    print(f"Param complex:   {params['param_complexity']}")
    print(f"Domain:          {params['domain']}")
    print(f"Edge case:       {params['edge_case']}")

    print(f"\nTools ({len(tools)}):")
    for t in tools:
        print(f"  - {t['function']['name']}")

    print("\n" + "=" * 70)
    print("GENERATED CONVERSATION")
    print("=" * 70)

    sp = result.get("system_prompt")
    print(f"\n[SYSTEM] {sp if sp else '(none)'}")

    print(f"\n--- Messages ({len(result['messages'])}) ---")

    for i, msg in enumerate(result["messages"]):
        role = msg["role"]
        content = msg.get("content") or ""
        tool_calls = msg.get("tool_calls")

        if role == "user":
            print(f"\n[{i+1}] [USER] {content}")
        elif role == "assistant":
            if tool_calls and tool_calls[0]:
                tc = tool_calls[0]
                print(f"\n[{i+1}] [ASSISTANT] -> tool_call: {tc['function']['name']}")
                print(f"                 args: {tc['function']['arguments']}")
            else:
                print(f"\n[{i+1}] [ASSISTANT] {content}")
        elif role == "tool":
            print(f"\n[{i+1}] [TOOL] ({msg.get('tool_call_id')})")
            print(f"       {content[:300]}{'...' if len(content) > 300 else ''}")

    actual_tool_calls = sum(
        1 for m in result["messages"] if m.get("tool_calls") and m["tool_calls"][0]
    )
    expected = params["num_tool_calls"]
    match = "OK" if actual_tool_calls == expected else "MISMATCH!"
    print(f"\n*** Tool calls: {actual_tool_calls} (expected: {expected}) {match} ***")
