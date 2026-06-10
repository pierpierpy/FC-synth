# synthfc — Synthetic Function-Calling Dataset Generator

Generate diverse, validated, multi-turn **function-calling (tool-use)** conversations to fine-tune
or evaluate LLMs — then post-process, validate, export and expand them into a training-ready dataset,
all from a single command-line tool.

A strong **teacher** LLM (any OpenAI-compatible or Azure OpenAI model) produces the conversations.
Every conversation is sampled from configurable distributions so the resulting dataset is varied along
many axes — call type, languages, conversation length, user style, tool count, edge cases, and 120+
realistic domains.

```text
sample params  ──▶  teacher LLM  ──▶  validate  ──▶  postprocess  ──▶  export  ──▶  expand
 (distributions)    (generation)      (rules)        (repair)         (train/test)   (child convos)
```

---

## Why

Public function-calling datasets tend to be single-turn, English-only, and thin on the messy realities
of production assistants: clarifying questions, out-of-scope requests, tool errors and recovery, frustrated
users, vague phrasing, and long multi-step conversations. `synthfc` generates that variety on purpose by
**sampling controlled parameters** for each example and asking a teacher model to realize them, then
**validating** the structure so the output is safe to train on.

The mock tool library ships in two languages (English and Italian) across 21 categories (~200 tools), and
the sampler draws from 120+ domains (telecom/customer support, banking, e-commerce, travel, healthcare,
public administration, HR, real estate, automotive, education, tech, and more).

---

## Install

Requires Python ≥ 3.10.

```bash
git clone <your-fork-url> synthfc && cd synthfc
python -m venv .venv && source .venv/bin/activate

# Editable install with the optional web UI + token-stats extras:
pip install -e ".[all]"
# (or just `pip install -e .` for the core CLI, or `pip install -r requirements.txt`)
```

This installs a `synthfc` command. You can also run everything as `python -m synthfc …` without installing.

## Configure

Secrets come **only** from the environment — never from the code or the YAML config.

```bash
cp .env.example .env          # then edit .env
set -a && source .env && set +a
```

| Variable | Meaning |
|---|---|
| `SYNTHFC_PROVIDER` | `openai` (any OpenAI-compatible API) or `azure` |
| `SYNTHFC_MODEL` | Teacher model / deployment name (e.g. `gpt-4o`) |
| `SYNTHFC_API_KEY` | API key (`OPENAI_API_KEY` is also accepted) |
| `SYNTHFC_ENDPOINT` | Base URL (vLLM/Together/local…) or **required** Azure resource URL |
| `SYNTHFC_API_VERSION` | Azure only |
| `SYNTHFC_DATA_DIR` | Override output dir (default `./data`) |
| `SYNTHFC_CONFIG` | Use a config file other than `configs/default.yaml` |

Generation parameters and sampling distributions live in [`configs/default.yaml`](configs/default.yaml)
(no secrets there). Edit it to reshape the dataset, or point `--config` at your own copy.

---

## Quickstart

```bash
# 1. Generate a batch of conversations with the teacher model
synthfc generate -n 100
#    → writes data/batch_100_<timestamp>/examples.jsonl (+ postprocessed)

# 2. Build a training-ready dataset (validate → postprocess → export → expand)
synthfc build batch_100_<timestamp>
#    → writes data/batch_100_<timestamp>/data/{all,train,test,expanded}.jsonl

# 3. Browse and review what you generated
synthfc serve
#    → http://127.0.0.1:8000
```

Preview what gets sampled, without spending any tokens:

```bash
synthfc sample -n 5
```

---

## Commands

Run `synthfc --help` or `synthfc <command> --help` for full flags.

| Command | What it does |
|---|---|
| `synthfc generate -n N` | Generate `N` conversations with the teacher LLM (async by default; `--sync` for serial). Auto-postprocesses unless `--no-postprocess`. |
| `synthfc build <batch>` | Run the full pipeline on a batch: validate → postprocess → re-validate → export (train/test split) → expand. `--expand 0` to skip expansion. |
| `synthfc serve` | Launch the FastAPI web UI to inspect examples, filter by validation status, and review conversations. |
| `synthfc merge a.jsonl b.jsonl -o out.jsonl` | Merge exported datasets (dedups, ensures every conversation ends with an assistant turn). |
| `synthfc stats data.jsonl --tokenizer <hf-id>` | Length/token statistics (real token counts with a chat template, or word counts without). |
| `synthfc sample -n N` | Print sampled generation parameters without calling the API. |
| `synthfc batch-api -n N` | Generate via the provider's offline Batch API (cheaper, slower); `--resume <id>` to resume. |

---

## How it works

### 1. Sampling (`synthfc/core/sampler.py`)

Each example draws one value from every distribution in `configs/default.yaml` — call type
(positive / negative / clarification), language combo (tool language × conversation language),
length, user style, number of tools and tool calls, history type, system-prompt verbosity, parameter
complexity, edge cases, and the domain. This is what makes the dataset diverse and controllable. Some
parameters have conditional logic in code that can override the config (e.g. `multi_tool` positives force
2–3 tool calls), so observed distributions may differ slightly from the configured ones — by design.

### 2. Generation (`synthfc/core/prompt_builder.py`, `generator.py`, `client.py`)

The sampled parameters are compiled into a prompt for the teacher model, which returns a complete
conversation as structured JSON (enforced via a response schema). Generation runs concurrently with a
configurable semaphore and periodic checkpointing. The client is provider-agnostic: the same code path
serves OpenAI, any OpenAI-compatible endpoint, or Azure OpenAI.

### 3. Validation (`synthfc/core/validator.py`)

Each conversation is checked against 10+ structural rules. Findings are split into two levels:

| Level | Behavior | Examples |
|---|---|---|
| **FAIL** | Excluded from the export | `parallel_tool_calls`, `consecutive_roles` |
| **WARNING** | Kept in the export | `call_type`, `num_tool_calls`, `conversation_length`, `user_style`, … |

The two FAILs are unrecoverable structural problems for typical training chat templates:

- **`parallel_tool_calls`** — an assistant message with two or more tool calls at once. Many chat templates
  (e.g. several Qwen/Llama variants) support only one tool call per assistant message, and the calls can't be
  split without losing the parallel semantics. ~2–3% of raw examples.
- **`consecutive_roles`** — two assistant turns in a row where the first is an empty "reflection" before the
  action. Syntactically invalid for many templates. Postprocessing repairs most of these; the rest fail.

### 4. Postprocessing (`synthfc/pipeline/postprocess.py`)

Structural cleanup before export: merges consecutive `user` turns, removes pre-tool "reflection" assistant
messages, and drops degenerate tool-call loops. Produces `examples_postprocessed.jsonl`.

### 5. Export (`synthfc/pipeline/export.py`)

Converts to the simple training format, filters out FAILs, and splits into `train.jsonl` (90%) and
`test.jsonl` (10%) plus a combined `all.jsonl`.

### 6. Expansion / "cutting" (`synthfc/pipeline/expand.py`)

Creates **child conversations** by cutting originals at natural boundaries — after each complete
`assistant[tool_call] → tool → assistant` cycle, and optionally once before the first tool call (a pure-dialogue
child). This gives the model supervision at multiple stages of a conversation and multiplies example variety.
All originals are kept; children are added on top.

```text
Original (10 msgs, 2 tool cycles)            Children generated
[system]                                     1. pre-tool child (dialogue only)
[user]  "hi"                                 2. post-tool child (1 complete cycle)
[assistant] "hello!"         ◀── pre-tool    3. the original (kept intact)
[user]  "find a flight"
[assistant] →search_flights
[tool]  {results}
[assistant] "found 3…"       ◀── post-tool
[user]  "book the first"
[assistant] →book_flight
[tool]  {confirmed}
[assistant] "booked!"        ◀── end (original)
```

---

## Output format

Each generated batch lives under `data/<batch_name>/`:

```text
data/<batch_name>/
├── examples.jsonl                 # raw teacher output + metadata & validation
├── examples_postprocessed.jsonl   # after structural cleanup
├── validation_results.json        # validation report
├── summary.json                   # batch summary
└── data/
    ├── all.jsonl                  # all valid examples (training format)
    ├── train.jsonl                # 90%
    ├── test.jsonl                 # 10%
    └── expanded.jsonl             # all.jsonl + child conversations
```

**Training format** (`all`/`train`/`test`/`expanded`) — minimal and ready to fine-tune on:

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "tool_calls": [{"id": "...", "type": "function",
       "function": {"name": "search_documents", "arguments": "{...}"}}]},
    {"role": "tool", "tool_call_id": "...", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "tools": [ /* OpenAI-style tool/function definitions */ ]
}
```

See [`examples/sample.jsonl`](examples/sample.jsonl) for two real records (one English, one Italian).

---

## Project layout

```text
synthfc/
├── cli.py            # the single CLI entry point (Typer)
├── config.py         # config loading (env for secrets, YAML for everything else)
├── core/
│   ├── sampler.py        # parameter sampling from distributions
│   ├── prompt_builder.py # builds the teacher prompt
│   ├── generator.py      # async/sync batch generation
│   ├── client.py         # provider-agnostic LLM client + tool selection
│   ├── validator.py      # structural validation rules
│   └── batch_api.py       # offline Batch API path
├── pipeline/
│   ├── validate.py  postprocess.py  export.py  expand.py  merge.py  token_stats.py
├── tools/
│   ├── eng/          # English mock tool catalogue (21 categories)
│   └── ita/          # Italian mock tool catalogue
└── webapp/           # FastAPI dataset viewer
configs/default.yaml  # generation + sampling configuration (no secrets)
examples/sample.jsonl # sample output records
```

---

## Notes & limitations

- This dataset is **synthetic**: tool results are mock data, and conversations are model-generated. Validate
  for your own use case before training on it.
- The two FAIL classes assume a chat template that allows only one tool call per assistant message. If your
  template supports parallel tool calls, you can relax that check in `validator.py`.
- Generation cost scales with `-n` and your teacher model's pricing. Start small (`synthfc generate -n 20`) and
  inspect with `synthfc serve` before scaling up. The `batch-api` command is cheaper for large runs.

## License

[MIT](LICENSE).
