#!/usr/bin/env bash
#
# serve_vllm.sh — serve a local teacher model with vLLM via Docker, exposing an
# OpenAI-compatible endpoint that synthfc can point at.
#
# Why Docker (and this env var) instead of `pip install vllm`:
#   Current vLLM wheels ship CUDA 13 binaries. On a host whose NVIDIA driver only
#   supports up to CUDA 12.2 (e.g. driver 535.x), a local pip install fails at
#   import/runtime with errors like `libcudart.so.13: cannot open shared object
#   file` or "CUDA driver version is insufficient / driver too old".
#   The official image vllm/vllm-openai:v0.22.1 is a CUDA 12.9 build, and setting
#   VLLM_ENABLE_CUDA_COMPATIBILITY=1 makes it use vLLM's *bundled CUDA
#   forward-compatibility libraries* — supported for datacenter GPUs (H100, A100,
#   ...) on an older driver. This combination is what we verified working on an
#   8x H100 80GB host with driver 535.247.01 (CUDA 12.2): the model loaded across
#   all 8 GPUs and tool-calling worked.
#
# NOTE on GPU access: we use `--gpus all` (the modern Docker GPU flag).
#   `--runtime nvidia` was tried and FAILED on this host — do not switch to it.
#
# Usage:
#   ./scripts/serve_vllm.sh
#   MODEL=Qwen/Qwen3.6-35B-A3B PORT=8765 TP=8 MAX_LEN=32768 ./scripts/serve_vllm.sh
#
# All knobs are env vars with sensible defaults (matching the verified setup):
set -euo pipefail

# --- Parameters (override via env) ------------------------------------------
# Teacher model (HF id or local path). MoE arch Qwen3_5MoeForConditionalGeneration
# requires vLLM >= 0.17 (v0.22.1 satisfies this).
MODEL="${MODEL:-Qwen/Qwen3.6-35B-A3B}"
# Host port to expose. synthfc points SYNTHFC_ENDPOINT at http://127.0.0.1:$PORT/v1
PORT="${PORT:-8765}"
# Tensor-parallel size = number of GPUs to shard the model across.
TP="${TP:-8}"
# Max context length (prompt + generation).
MAX_LEN="${MAX_LEN:-32768}"
# Fraction of each GPU's memory vLLM may use.
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.90}"
# Docker image (CUDA 12.9 build; verified working with the CUDA-compat env var).
IMAGE="${IMAGE:-vllm/vllm-openai:v0.22.1}"

# Derive a docker-safe container name from the model id (strip the org prefix,
# lowercase, replace any non-alphanumeric run with a single dash).
CONTAINER_NAME="vllm-$(echo "${MODEL##*/}" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//')"

echo "Starting vLLM (${IMAGE})"
echo "  model      : ${MODEL}"
echo "  container  : ${CONTAINER_NAME}"
echo "  endpoint   : http://127.0.0.1:${PORT}/v1"
echo "  tensor-par : ${TP}"
echo "  max-len    : ${MAX_LEN}"

# --- Run --------------------------------------------------------------------
# --ipc=host: vLLM uses shared memory for tensor-parallel comms.
# -v ~/.cache/huggingface: reuse the host HF cache so weights download once.
# VLLM_ENABLE_CUDA_COMPATIBILITY=1: THE key flag — use bundled CUDA forward-compat
#   libs so the CUDA 12.9 image runs on the 12.2 driver.
# Parser flags (Qwen3.x): the model emits an XML tool-call format, so we need
#   --tool-call-parser qwen3_xml (with --enable-auto-tool-choice) and
#   --reasoning-parser qwen3 to split out its reasoning trace.
exec docker run --rm --name "${CONTAINER_NAME}" \
  --gpus all \
  --ipc=host \
  -p "${PORT}:8000" \
  -v "${HOME}/.cache/huggingface:/root/.cache/huggingface" \
  --env VLLM_ENABLE_CUDA_COMPATIBILITY=1 \
  "${IMAGE}" \
  --model "${MODEL}" \
  --tensor-parallel-size "${TP}" \
  --max-model-len "${MAX_LEN}" \
  --gpu-memory-utilization "${GPU_MEM_UTIL}" \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml \
  --trust-remote-code
