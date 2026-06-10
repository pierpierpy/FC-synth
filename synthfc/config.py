"""Configuration for synthfc.

Configuration comes from three layers, merged in this order (later wins):

1. Built-in defaults (below).
2. A YAML config file (``configs/default.yaml`` by default, or the path
   passed to :func:`get_config` / the ``SYNTHFC_CONFIG`` env var).
3. Environment variables for anything secret (API keys, endpoints).

No secrets are ever stored in the YAML or in this file. Provide them via the
environment (see ``.env.example``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
# This file lives at <repo_root>/synthfc/config.py, so the repo root is one
# level up from the package directory.
PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "default.yaml"


def data_dir() -> Path:
    """Directory where generated batches are written.

    Defaults to ``<repo_root>/data`` and can be overridden with the
    ``SYNTHFC_DATA_DIR`` environment variable.
    """
    env = os.environ.get("SYNTHFC_DATA_DIR")
    base = Path(env) if env else REPO_ROOT / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base


# --------------------------------------------------------------------------- #
# Defaults (no secrets here — those come from the environment)
# --------------------------------------------------------------------------- #
DEFAULT_CONFIG: Dict[str, Any] = {
    "model": {
        # "openai" for any OpenAI-compatible endpoint (OpenAI, vLLM, Together,
        # Groq, local servers, ...) or "azure" for Azure OpenAI.
        "provider": "openai",
        # Model / deployment name to call.
        "model": "gpt-4o",
        "temperature": 1.0,
        "top_p": 1.0,
        "max_tokens": 4096,
        # Azure-only: API version. Ignored for the "openai" provider.
        "api_version": "2024-10-21",
    },
    "generation": {
        "batch_size": 25,
        "concurrency": 25,
        "max_retries": 3,
        "retry_delay": 2.0,
        # Delay between calls in the synchronous path (seconds).
        "delay_between_calls": 0.0,
        # Save a checkpoint every N examples (0 = disabled).
        "checkpoint_every": 0,
    },
    "validation": {
        "enabled": True,
        "strict": False,
    },
    # "sampling" distributions are optional; when absent the built-in defaults
    # in synthfc.core.sampler are used.
    "sampling": {},
}


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge ``override`` into a copy of ``base``."""
    result = dict(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class ModelConfig:
    provider: str
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    api_version: str
    # Secrets / connection — resolved from the environment, never the YAML.
    api_key: Optional[str] = None
    endpoint: Optional[str] = None


@dataclass
class GenerationConfig:
    batch_size: int
    concurrency: int
    max_retries: int
    retry_delay: float
    delay_between_calls: float = 0.0
    checkpoint_every: int = 0


class Config:
    """Loaded configuration with typed accessors."""

    def __init__(self, config_path: Optional[str | Path] = None):
        self._raw: Dict[str, Any] = DEFAULT_CONFIG

        path = (
            Path(config_path)
            if config_path
            else Path(os.environ.get("SYNTHFC_CONFIG", DEFAULT_CONFIG_PATH))
        )
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            self._raw = deep_merge(DEFAULT_CONFIG, user_config)

    @property
    def model(self) -> ModelConfig:
        m = self._raw.get("model", {})
        defaults = DEFAULT_CONFIG["model"]
        provider = os.environ.get(
            "SYNTHFC_PROVIDER", m.get("provider", defaults["provider"])
        )
        return ModelConfig(
            provider=provider,
            model=os.environ.get("SYNTHFC_MODEL", m.get("model", defaults["model"])),
            temperature=m.get("temperature", defaults["temperature"]),
            top_p=m.get("top_p", defaults["top_p"]),
            max_tokens=m.get("max_tokens", defaults["max_tokens"]),
            api_version=os.environ.get(
                "SYNTHFC_API_VERSION", m.get("api_version", defaults["api_version"])
            ),
            # Secrets strictly from the environment.
            api_key=os.environ.get("SYNTHFC_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            endpoint=os.environ.get("SYNTHFC_ENDPOINT") or os.environ.get("OPENAI_BASE_URL"),
        )

    @property
    def generation(self) -> GenerationConfig:
        g = self._raw.get("generation", {})
        defaults = DEFAULT_CONFIG["generation"]
        return GenerationConfig(
            batch_size=g.get("batch_size", defaults["batch_size"]),
            concurrency=g.get("concurrency", defaults["concurrency"]),
            max_retries=g.get("max_retries", defaults["max_retries"]),
            retry_delay=g.get("retry_delay", defaults["retry_delay"]),
            delay_between_calls=g.get(
                "delay_between_calls", defaults["delay_between_calls"]
            ),
            checkpoint_every=g.get("checkpoint_every", defaults["checkpoint_every"]),
        )

    @property
    def sampling(self) -> Dict[str, Dict[str, float]]:
        return self._raw.get("sampling", {}) or {}

    @property
    def validation(self) -> Dict[str, Any]:
        return self._raw.get("validation", DEFAULT_CONFIG["validation"])

    def get(self, key: str, default: Any = None) -> Any:
        return self._raw.get(key, default)


# --------------------------------------------------------------------------- #
# Singleton
# --------------------------------------------------------------------------- #
_config: Optional[Config] = None


def get_config(config_path: Optional[str | Path] = None) -> Config:
    """Return the process-wide :class:`Config`, creating it on first use."""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reload_config(config_path: Optional[str | Path] = None) -> Config:
    """Force-reload the configuration from disk."""
    global _config
    _config = Config(config_path)
    return _config
