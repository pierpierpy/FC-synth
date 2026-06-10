---
license: mit
task_categories:
  - text-generation
language:
  - en
  - it
tags:
  - function-calling
  - tool-use
  - synthetic
  - multi-turn
  - conversational
  - agents
size_categories:
  - 10K<n<100K
pretty_name: Synthetic Multi-Turn Function-Calling Conversations
configs:
  - config_name: default
    data_files:
      - split: train
        path: train.jsonl
      - split: test
        path: test.jsonl
---

# Synthetic Multi-Turn Function-Calling Conversations

Synthetic, multi-turn **function-calling (tool-use)** conversations for fine-tuning and evaluating LLMs,
generated and validated with [`synthfc`](https://github.com/YOUR_USERNAME/synthfc).

A strong teacher LLM produces each conversation from controlled, sampled parameters, so the dataset is
diverse along many axes (call type, languages, length, user style, tool count, edge cases, domain) and every
example passes structural validation suitable for common chat templates.

## Dataset structure

Each row is a single conversation in an OpenAI-style messages + tools format:

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "tool_calls": [
      {"id": "...", "type": "function",
       "function": {"name": "search_documents", "arguments": "{...}"}}]},
    {"role": "tool", "tool_call_id": "...", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "tools": [ /* OpenAI-style function/tool definitions */ ]
}
```

- `messages`: the conversation. Assistant tool calls follow the OpenAI `tool_calls` schema; `tool` messages
  carry the (mock) tool result keyed by `tool_call_id`. Conversations always end with an assistant turn.
- `tools`: the tool definitions available for that conversation.

### Splits

| Split | Description |
|---|---|
| `train` | ~90% of valid examples |
| `test`  | ~10% of valid examples |

An `expanded` variant (originals + cut "child" conversations for multi-stage supervision) can also be produced
with `synthfc build`.

## How it was created

1. **Sample** controlled parameters per example (call type, languages, length, user style, tool/call counts,
   edge cases, domain) from configurable distributions.
2. **Generate** the conversation with a teacher LLM constrained to a structured response schema.
3. **Validate** against 10+ structural rules; examples with `parallel_tool_calls` or unrecoverable
   `consecutive_roles` are excluded.
4. **Postprocess** to repair structural issues (merge consecutive user turns, remove reflection turns).
5. **Export** into the training format and split into train/test.

Full pipeline and code: <https://github.com/YOUR_USERNAME/synthfc>.

## Languages

English and Italian, including mixed tool-language / conversation-language combinations.

## Intended use & limitations

- **Intended use**: supervised fine-tuning and evaluation of function-calling / tool-use behavior, including
  multi-turn flows, clarification, out-of-scope handling, and tool-error recovery.
- **Synthetic data**: tool results are mock data and conversations are model-generated. They may contain
  artifacts or factual inaccuracies. Validate for your use case before training.
- **Template assumption**: the structural validation assumes a chat template allowing one tool call per
  assistant message. Re-validate if your template supports parallel tool calls.

## License

[MIT](LICENSE). Note that generations were produced with a teacher model; review that provider's terms for any
restrictions on training with model outputs.

## Citation

```bibtex
@software{synthfc,
  title  = {synthfc: Synthetic Function-Calling Dataset Generator},
  author = {Di Pasquale, Piergiorgio},
  year   = {2026},
  url    = {https://github.com/YOUR_USERNAME/synthfc}
}
```
