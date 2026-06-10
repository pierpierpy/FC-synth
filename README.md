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

## Serving a local teacher model (vLLM + Docker)

The teacher can be **any OpenAI-compatible server** — OpenAI itself, Together/Groq, or a model you host
locally. If you want to self-host, [vLLM](https://github.com/vllm-project/vllm) is one easy recipe; this
section is the exact setup we verified on an 8× H100 host.

**Why Docker (not `pip install vllm`).** Recent vLLM wheels ship **CUDA 13** binaries. On a host whose
NVIDIA driver tops out at CUDA 12.2 (e.g. driver `535.x`), a local install fails at runtime with
`libcudart.so.13: cannot open shared object file` or *"CUDA driver version is insufficient / driver too
old"*. The fix: the official image `vllm/vllm-openai:v0.22.1` is a **CUDA 12.9** build, and it **bundles
CUDA forward-compatibility libraries** that are supported for datacenter GPUs (H100, A100, …) on older
drivers. Setting `VLLM_ENABLE_CUDA_COMPATIBILITY=1` turns those on, so the image runs fine on the 12.2
driver — verified: model loaded across all 8 GPUs, tool-calling worked.

> Use `--gpus all` (the modern Docker GPU flag). `--runtime nvidia` was tried and **failed** on this host.

### Run it

A parameterized launcher lives at [`scripts/serve_vllm.sh`](scripts/serve_vllm.sh):

```bash
# Defaults: MODEL=Qwen/Qwen3.6-35B-A3B PORT=8765 TP=8 MAX_LEN=32768
./scripts/serve_vllm.sh

# Or override any knob via env:
MODEL=Qwen/Qwen3.6-35B-A3B PORT=8765 TP=8 MAX_LEN=32768 ./scripts/serve_vllm.sh
```

Under the hood it runs (abbreviated):

```bash
docker run --rm --gpus all --ipc=host -p 8765:8000 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  --env VLLM_ENABLE_CUDA_COMPATIBILITY=1 \
  vllm/vllm-openai:v0.22.1 \
  --model Qwen/Qwen3.6-35B-A3B --tensor-parallel-size 8 --max-model-len 32768 \
  --gpu-memory-utilization 0.90 \
  --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_xml --trust-remote-code
```

**Parser flags (model-specific).** `Qwen/Qwen3.6-35B-A3B` is an MoE model (arch
`Qwen3_5MoeForConditionalGeneration`, needs vLLM ≥ 0.17) that emits an **XML tool-call format** and a
separate reasoning trace. So we pass `--enable-auto-tool-choice --tool-call-parser qwen3_xml` (parse those
XML tool calls into OpenAI `tool_calls`) and `--reasoning-parser qwen3` (split the reasoning out of the
final answer). A different model needs different parsers — see vLLM's tool-calling docs.

### Point synthfc at it

Set the four `SYNTHFC_*` env vars to the local endpoint (`SYNTHFC_API_KEY` is required but unused, so any
placeholder works):

```bash
SYNTHFC_PROVIDER=openai
SYNTHFC_MODEL='Qwen/Qwen3.6-35B-A3B'
SYNTHFC_ENDPOINT='http://127.0.0.1:8765/v1'
SYNTHFC_API_KEY=EMPTY
```

Drop the same block into your `.env` (`cp .env.example .env`, then `set -a && source .env && set +a`).

### Readiness & sanity checks

```bash
# Is the server up and serving the model?
curl http://127.0.0.1:8765/v1/models

# One-line tool-calling sanity check (server should return a tool_calls response):
curl http://127.0.0.1:8765/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen/Qwen3.6-35B-A3B","messages":[{"role":"user","content":"What is the weather in Rome?"}],"tools":[{"type":"function","function":{"name":"get_weather","description":"Get current weather for a city","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}],"tool_choice":"auto"}'
```

Once `/v1/models` lists the model and the second call comes back with a `tool_calls` field, `synthfc
generate` will use it as the teacher.

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

## The core idea: when to call a tool (and when *not* to)

The hardest part of function calling isn't the syntax of a tool call — it's the **decision**: should the
assistant call a tool *at all* for this turn, and if so, which one and with what arguments? A model that
only ever sees "user asks → call tool" learns to **over-trigger**: it fabricates tool calls for chit-chat,
general-knowledge questions, and requests no available tool can serve. A good function-calling dataset has
to teach the *boundary*, not just the happy path.

We frame that boundary as a 2×2 matrix over two independent yes/no axes:

- **Does the request *require* a tool?** — can it only be answered correctly by calling one of the available
  tools, or can the assistant handle it from its own knowledge / in plain dialogue?
- **Does the correct answer *emit* a tool call?** — does the gold assistant turn contain `tool_calls`, or is
  it text only?

|                              | **Answer uses a tool** (emits `tool_calls`)                                                                                                                                                                | **Answer is text only** (no `tool_calls`)                                                                                                                                                          |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Request requires a tool**  | **① True positive — *call correctly*.** The happy path: a clear, in-scope request, answered by calling the right tool with the right arguments. Sampled as `call_type = positive`.                          | **③ Needed but no call — *don't fabricate*.** The request would need a tool, but the assistant legitimately produces no call: it asks for the missing argument and the user never supplies it, or a tool errors out. Sampled as `clarification` (`unresolved` / `partial`) and tool-error edge cases. Teaches the model to *stall or recover* instead of inventing a call. |
| **Request needs no tool**    | **② Spurious call — *the anti-pattern*.** Chit-chat / general knowledge / out-of-scope, yet a tool gets called. This is the over-triggering failure mode. We do **not** generate these as "gold" answers — the model learns to avoid this quadrant by seeing quadrant ④ done right. | **④ True negative — *correct restraint*.** The right answer is plain text. Sampled as `call_type = negative`: `no_need` (chit-chat), `already_answered` (answer from the model's own knowledge), or `out_of_scope` (no suitable tool → politely decline and redirect). This is the quadrant that teaches restraint. |

**The diagonal is the lesson.** ① (call when you should) and ④ (don't call when you shouldn't) are the two
*correct* behaviors, and the dataset is deliberately weighted across both — not just ①. Quadrant ③ is
generated as a legitimate, realistic outcome (conversations don't always succeed). Quadrant ② is the
mistake we're training *against*; the model converges to the boundary by seeing ④ answered correctly, never
by being shown a spurious call as the target.

How the sampler's `call_type` maps onto the matrix:

| `call_type`     | Subtypes                                          | Quadrant(s) |
| --------------- | ------------------------------------------------- | ----------- |
| `positive`      | `direct`, `after_chitchat`, `followup`, `multi_tool`, `after_clarification` | ①           |
| `negative`      | `no_need`, `already_answered`, `out_of_scope`     | ④           |
| `clarification` | `resolved` → eventually calls; `unresolved` / `partial` → never calls | ① / ③       |

A model trained on all four behaviors learns *whether*, *which*, and *how* — not just how.

---

## How it works

### 1. Sampling (`synthfc/core/sampler.py`)

Every example is built by **drawing one value from each of ~18 distributions** defined in
`configs/default.yaml`, then asking the teacher model to realize exactly that combination. Sampling — rather
than free-form prompting — is what makes the dataset diverse *and* controllable: you reshape the dataset by
editing weights, not prompts. Run `synthfc sample -n 5` to see sampled parameter sets without spending tokens.

The axes that get sampled (see [`configs/default.yaml`](configs/default.yaml) for the weights):

| Axis | Values | Controls |
|---|---|---|
| `call_type` | positive / negative / clarification | the matrix quadrant (see above) |
| `language_combo` | (tool_lang, conv_lang) ∈ {it,en}² | tool language × conversation language (incl. mixed) |
| `num_tools_available` | 2–5 | how many tools are offered for the turn |
| `num_tool_calls` | 0–3 | how many calls the gold answer makes |
| `conversation_length` | short / medium / long / very_long | total turns |
| `user_style` | formal, informal, vague, telegraphic, frustrated, confused, verbose | how the user writes |
| `history_type` | none, chitchat, context_setting, previous_tool, multi_topic | what precedes the request |
| `system_prompt_type` | none / minimal / standard / detailed | system-prompt verbosity |
| `param_complexity` | explicit, implicit, mixed, missing | how arguments are stated (drives clarification) |
| `edge_case` | tool_error, recovery, user_correction, ambiguous, multi_step, partial_success, topic_change, … | realistic complications |
| `domain` | 120+ domains (telecom, banking, travel, health, …) | the scenario, which constrains tool categories |

**Conditional logic (why observed ≠ configured).** `sample_params()` is not a flat product of independent
draws — later parameters depend on earlier ones, so the realized distribution differs from the configured one
*by design*. The main dependencies:

- `domain` is drawn first (weighted), then it constrains which **tool categories** are eligible
  (`get_compatible_categories`), and 1–2 of those are chosen — so tools are always plausible for the scenario.
- For `positive`/`multi_tool`, `num_tool_calls` is **forced** to 2–3 (ignoring the `num_tool_calls`
  distribution); `followup` is forced to 2–3 as well. Only "plain" positives use the configured distribution.
- `first_tool_position` depends on `positive_type`: `direct` ⇒ position 1; `after_chitchat` /
  `after_clarification` ⇒ later positions. `negative` and unresolved `clarification` have *no* tool call
  (`num_tool_calls = 0`).
- `history_type` is forced to `none` when the first tool call is at position ≤ 1 (no room for history).
- `param_complexity` and `out_of_scope_requests` are only sampled where they make sense (positive, or
  resolved clarification).

The takeaway: edit `configs/default.yaml` to shift the dataset, but expect the *observed* mix to be shaped by
these dependencies. `synthfc sample` and the analysis helpers in `sampler.py` let you inspect the real mix.

### 2. Generation (`synthfc/core/prompt_builder.py`, `generator.py`, `client.py`)

The sampled parameters are compiled into a prompt for the teacher model, which returns a complete
conversation as structured JSON. The output is constrained by an OpenAI `json_schema` response format
(`strict: true`) that fixes the message shape — `role ∈ {user, assistant, tool}`, and every assistant
`tool_calls` entry carries `id`, `type`, and a `function` with string `name` + `arguments`. The *stricter*
behavioral rules below are enforced by the prompt text, not the schema.

**What the teacher is told to produce.** `prompt_builder.py` assembles the prompt from modular blocks keyed
on the sampled parameters, and bakes in the structural contract that makes the output trainable:

- **Multi-turn shape.** A tool call is its **own** assistant message (`content: null`, `tool_calls: [...]`);
  the result comes back as a separate `tool` message keyed by `tool_call_id`; the assistant then replies in a
  new message with `tool_calls: null`. `arguments` is a JSON-**escaped string**, not an object.
- **No "reflection" before a tool.** The model must call the tool **directly** — never emit a chatty
  "Sure, doing that now…" assistant turn right before the tool call (that produces two consecutive assistant
  turns, which breaks many chat templates). The only allowed assistant→assistant adjacency is a brief comment
  *after* a tool result.
- **Tool placement & count.** When sampled, the prompt injects hard constraints: call a tool at turn
  *`first_tool_position`*, exactly *`num_tool_calls`* times. `positive/direct` ⇒ immediate call; `multi_tool`
  and `followup` ⇒ ≥2 calls; `negative` and unresolved `clarification` ⇒ **zero** calls (a soft reminder that
  "assistant messages contain only text" is appended).

Generation runs concurrently (an `asyncio.Semaphore` sized by `concurrency`), with per-example error capture
(a failed call is recorded with `error=...` rather than aborting the batch), optional checkpointing every *N*
examples, and **inline validation** of each example as it completes. Each saved example carries its sampled
`params`, the `observed` metrics (actual tool-call count, first-tool position, message count, detected
language, system-prompt type), and its full validation report. The client is provider-agnostic: the same path
serves OpenAI, any OpenAI-compatible endpoint, or Azure OpenAI.

### 3. Edge cases & scenarios

Beyond the four matrix quadrants, the sampler can inject a realistic **complication** into a conversation
(`edge_case`), so the model sees more than clean happy paths. By default ~65% of examples have no edge case;
the rest draw from:

| Edge case | What the conversation does |
|---|---|
| `tool_error` | A tool returns an error; the assistant handles it gracefully in plain language. |
| `tool_error_recovery` | The flagship multi-turn case: request → tool call → **error** → the assistant explains it, the user provides a new valid request, and the assistant **calls the tool again successfully** (≥2 calls, one failing + one succeeding). The error is part of the story — the assistant never claims it "has no access". |
| `user_correction` | The user corrects themselves mid-flow ("no wait, I meant the 2023 document") and the assistant adapts. |
| `ambiguous_request` | A vague request ("send me the report") that needs disambiguation before acting. |
| `multi_step_task` | One request that decomposes into several tool steps ("generate the report, send it to my boss, then archive it"). |
| `partial_success` | A batch operation that only partly succeeds (2 of 3 documents) and is reported honestly. |
| `topic_change` | The user switches topic mid-conversation. |

Independently, **out-of-scope distractor turns** (`out_of_scope_requests`, sampled only for `positive` or
resolved `clarification`) sprinkle 0–3 requests no available tool can serve, *distributed naturally through*
the conversation — training the model to decline those turns while still completing the in-scope ones. This is
how quadrant ② (spurious calls) is taught against *inside* an otherwise-positive conversation.

### 4. Validation (`synthfc/core/validator.py`)

Every example runs through **10 checks** that compare what was *requested* (`params`) against what the model
*actually did* (`observed` + the raw messages). Each check returns one of `PASS` / `WARN` / `FAIL` / `SKIP`,
and the example gets a `score = passed / (non-skipped checks)`. Crucially, only **two** checks can ever `FAIL`
(and thus exclude an example from the export). Everything else is at most a `WARN` — kept, because the teacher
is *allowed* to deviate from the sampled plan as long as the result is structurally sound.

**The two FAIL checks** (structural, unrecoverable for common chat templates):

| Check | FAILs when | Why it's fatal |
|---|---|---|
| `parallel_tool_calls` | any assistant message has **>1** `tool_calls` | Many chat templates (several Qwen/Llama variants) allow only one tool call per assistant message; the calls can't be split without losing the parallel semantics. |
| `consecutive_roles` | two `assistant` turns in a row where the first isn't preceded by a `tool` (i.e. a `user → assistant → assistant` reflection) | Breaks turn structure. `tool → tool` and `tool → assistant → assistant` are fine; `user → user` is only a `WARN` (postprocessing merges those). |

**The eight WARN-only checks** (quality signals, never block export):

| Check | Compares | PASS / WARN |
|---|---|---|
| `call_type` | requested type vs. actual call count | `positive`/resolved-`clarification` should call; `negative`/unresolved should not |
| `num_tool_calls` | requested vs. actual count | PASS only on an exact match |
| `conversation_length` | message count vs. category band | `short (2–6)`, `medium (4–14)`, `long (8–22)`, `very_long (15–100)`; ±4 still WARNs |
| `system_prompt_type` | prompt word count vs. band | `minimal (1–20)`, `standard (15–80)`, `detailed (50–500)` |
| `conversation_language` | detected vs. requested language | Italian-marker heuristic over user turns |
| `first_tool_position` | requested vs. actual first-call turn | PASS within ±3, WARN within ±5 |
| `user_style` | detected vs. requested style | heuristic over user text (formal/informal/vague/telegraphic/frustrated/confused/verbose) |
| `out_of_scope_requests` | declines found vs. requested distractors | SKIPped unless distractors were requested |

`synthfc build` runs validation, then **re-runs it after postprocessing** so the report reflects the cleaned
data. Reports are written to `validation_results.json`.

### 5. Postprocessing (`synthfc/pipeline/postprocess.py`)

Structural cleanup that repairs *recoverable* issues before export (it does **not** drop examples on a
validator FAIL — only on the loop case below):

- **Merge consecutive `user` turns** — collapses `user → user` into one message (joined with newlines). This is
  the `user-user` case the validator only WARNs about.
- **Remove a pre-tool reflection** — when an assistant content turn sits right before another assistant turn and
  the nearest prior non-assistant turn was a `user`, the reflection turn is dropped. This repairs the most
  common `consecutive_roles` FAIL.
- **Drop tool-call loops** — an example with any assistant message carrying **>5** `tool_calls` is removed
  outright (a degenerate teacher failure mode).

It then recomputes the `observed` metrics on the cleaned messages and re-validates for reporting. Note the
repair and the validator aren't perfect mirror images: a `user → assistant(tool_call) → assistant` case still
FAILs validation but isn't repaired here — those examples are simply filtered at export. Output:
`examples_postprocessed.jsonl`.

### 6. Export (`synthfc/pipeline/export.py`)

Converts to the minimal training format, **filters out the FAILs** (`parallel_tool_calls`, `consecutive_roles`)
and generation errors, then splits into `train.jsonl` (90%) and `test.jsonl` (10%) plus a combined `all.jsonl`
(seeded, reproducible).

### 7. Expansion / "cutting" (`synthfc/pipeline/expand.py`)

Creates **child conversations** by truncating each parent at natural boundaries, giving the model supervision at
multiple stages of the same dialogue and multiplying variety. Two kinds of cut:

- **`post_tool`** — after each complete `assistant[tool_call] → tool → assistant` cycle (so the child ends right
  after a successful tool response).
- **`pre_tool`** — at most once, just before the first tool call, yielding a pure-dialogue child (the assistant
  content turn must have >10 chars).

Every child must leave **≥4 non-system messages** and must **end on an assistant turn**, and can't equal the
full original. Children are emitted only for a random `--expand` percent subset (seeded), and carry metadata:
`id` (`<parent>_cut<N>`), `parent_id`, `cut_type`, `cut_at`, `original_length`. All originals are always kept;
children are added on top.

```text
Original (10 msgs, 2 tool cycles)            Children generated
[system]                                     1. pre-tool child  (dialogue only)
[user]  "hi"                                 2. post-tool child (1 complete cycle)
[assistant] "hello!"         ◀── pre-tool    3. the original    (kept intact)
[user]  "find a flight"
[assistant] →search_flights
[tool]  {results}
[assistant] "found 3…"       ◀── post-tool
[user]  "book the first"
[assistant] →book_flight
[tool]  {confirmed}
[assistant] "booked!"        ◀── end (original, not a cut)
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

## Extending with new tools

The mock tool library lives in `synthfc/tools/eng/` (English) and `synthfc/tools/ita/` (Italian), one Python
module per category (`weather.py`, `finance.py`, `knowledge_base.py`, …). You'd add tools when you want the
dataset to cover a capability or product surface it doesn't yet — e.g. your own product's APIs, a new vertical,
or simply more tool *variety* within an existing domain so the model sees many phrasings of the same intent.

A tool is just an **OpenAI-style function definition**. The dataset's value comes from variety, so when adding
tools, vary names, descriptions, and argument shapes for the *same* underlying intent — that's what teaches the
model to map diverse user phrasings onto the right tool. (`knowledge_base.py` is a good example: ~20 near-synonym
document tools.)

### 1. Define the tools

Create or edit a category module, e.g. `synthfc/tools/eng/payments.py`:

```python
"""Payment tools - English version."""

PAYMENTS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_payment",
            "description": "Send a payment to a recipient. Use when the user wants to pay or transfer money.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Name or account of the payee"},
                    "amount":    {"type": "number", "description": "Amount to send"},
                    "currency":  {"type": "string", "description": "ISO currency code", "default": "EUR"},
                },
                "required": ["recipient", "amount"],
            },
        },
    },
    # ... add more, including near-synonyms (transfer_funds, make_payment, ...) for diversity
]
```

### 2. (Optional) Add a mock executor

The **teacher model invents tool results during generation**, so an executor is *not* required to grow the
dataset. Executors (`def execute_<cat>_tool(tool_name: str, args: dict) -> dict`) are only used if you call the
tools yourself (e.g. the interactive/batch paths or your own evaluation harness). Categories without one —
like `knowledge_base` — simply have no entry in `EXECUTORS`. If you add one, return a plausible dict (or
`{"error": ...}` to exercise the tool-error edge cases):

```python
def execute_payments_tool(tool_name: str, args: dict) -> dict:
    if tool_name == "send_payment":
        return {"status": "success", "transaction_id": "TX-12345", "amount": args.get("amount")}
    return {"error": f"Unknown payments tool: {tool_name}"}
```

### 3. Register the category in `tools/eng/__init__.py`

Wire it in at these points (mirror an existing category like `weather`):

```python
from .payments import PAYMENTS_TOOLS, execute_payments_tool   # 1. import

ALL_TOOLS = ( ... + PAYMENTS_TOOLS )                           # 2. add to ALL_TOOLS

for tool in PAYMENTS_TOOLS:                                    # 3. map tool name -> category
    TOOL_CATEGORIES[tool["function"]["name"]] = "payments"

EXECUTORS = { ..., "payments": execute_payments_tool }         # 4. (only if you wrote an executor)

# get_tools_by_category()'s category_map and the module-level TOOLS_BY_CATEGORY
TOOLS_BY_CATEGORY = { ..., "payments": PAYMENTS_TOOLS }        # 5. + 6. add to both maps
```

### 4. Mirror it in the Italian catalogue

Add the same category to `synthfc/tools/ita/` with **Italian** names/descriptions (e.g. `invia_pagamento`).
Keep the category **key** identical (`"payments"`) so the cross-language selector lines up — `client.py`'s
`CATEGORY_MAP_EN_TO_IT` maps English category keys to the Italian catalogue's keys; add an entry there if your
Italian package keys differ.

### 5. Make the new category reachable by the sampler

Tools are only offered for a turn if the sampled **domain** maps to your category. In
`synthfc/core/sampler.py`:

- Add `"payments"` to the relevant domains in `get_compatible_categories()` (and to `TOOL_CATEGORIES` there if
  you introduce a new grouping), and
- optionally add new `DOMAINS` entries (and `DOMAIN_WEIGHTS`) so payment scenarios actually get sampled.

### 6. Verify

```python
from synthfc.tools.eng import TOOLS_BY_CATEGORY, execute_tool
assert "payments" in TOOLS_BY_CATEGORY
print(execute_tool("send_payment", {"recipient": "Acme", "amount": 10}))
```

Then `synthfc sample -n 20` and confirm your category appears in `tool_categories`, and generate a small batch
(`synthfc generate -n 10`) to eyeball real conversations using the new tools.

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
