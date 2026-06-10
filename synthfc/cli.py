"""synthfc command-line interface.

A single entry point for the whole workflow. Run ``python -m synthfc --help``
(or just ``synthfc --help`` after ``pip install -e .``) to see every command.

Typical flow::

    synthfc generate -n 100              # generate a batch with the teacher LLM
    synthfc build <batch_name>           # validate + postprocess + export + expand
    synthfc serve                        # browse results in the web UI

Run ``synthfc <command> --help`` for the flags of any command.
"""

from __future__ import annotations

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from .config import data_dir, get_config

app = typer.Typer(
    help="Synthetic multi-turn function-calling dataset generator.",
    no_args_is_help=True,
    add_completion=False,
)


# --------------------------------------------------------------------------- #
# generate
# --------------------------------------------------------------------------- #
@app.command()
def generate(
    n: int = typer.Option(
        None, "--num", "-n", help="Number of examples to generate (default: from config)."
    ),
    sync: bool = typer.Option(
        False, "--sync", help="Use the synchronous path instead of async."
    ),
    name: Optional[str] = typer.Option(
        None, "--name", help="Batch name (default: batch_<n>_<timestamp>)."
    ),
    postprocess: bool = typer.Option(
        True, "--postprocess/--no-postprocess", help="Run postprocessing after generation."
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to a YAML config file."
    ),
):
    """Generate a batch of conversations with the teacher LLM."""
    from .core import generator
    from .pipeline import postprocess as pp

    cfg = get_config(config)
    count = n if n is not None else cfg.generation.batch_size

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_name = name or f"batch_{count}_{timestamp}"
    batch_dir = data_dir() / batch_name
    batch_dir.mkdir(parents=True, exist_ok=True)
    output_file = batch_dir / "examples.jsonl"

    mode = "sync" if sync else f"async (concurrency={cfg.generation.concurrency})"
    typer.echo(f"Generating {count} examples")
    typer.echo(f"  model:       {cfg.model.model} ({cfg.model.provider})")
    typer.echo(f"  temperature: {cfg.model.temperature}")
    typer.echo(f"  mode:        {mode}")
    typer.echo(f"  output:      {batch_dir}")

    if sync:
        examples = generator.generate_batch(n=count, output_file=str(output_file), verbose=True)
    else:
        examples = asyncio.run(
            generator.generate_batch_async(n=count, output_file=str(output_file), verbose=True)
        )

    errors = sum(1 for e in examples if e.error)
    typer.echo(f"\nGenerated {len(examples)} ({errors} errors)")

    if postprocess:
        typer.echo("Postprocessing…")
        stats = pp.postprocess_batch(batch_dir, dry_run=False)
        typer.echo(
            f"  modified {stats.examples_modified}/{stats.total_examples}, "
            f"user-merged {stats.user_user_merged}, "
            f"reflections removed {stats.reflections_removed}"
        )

    typer.echo(f"\nSaved to {batch_dir}/")
    typer.echo(f"Next: synthfc build {batch_name}")


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #
@app.command()
def build(
    batch: str = typer.Argument(..., help="Batch name under the data directory."),
    expand_pct: int = typer.Option(
        50, "--expand", "-e", help="Percent of the dataset to expand into child conversations (0 to skip)."
    ),
    test_split: float = typer.Option(
        0.1, "--test-split", "-t", help="Fraction of examples held out for the test split."
    ),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed for split/expand."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML config file."),
):
    """Build a training-ready dataset: validate → postprocess → export → expand."""
    from .pipeline import expand, export, postprocess, validate

    get_config(config)
    batch_dir = data_dir() / batch
    if not batch_dir.exists():
        typer.secho(f"Batch not found: {batch_dir}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    pp_file = batch_dir / "examples_postprocessed.jsonl"

    typer.secho("[1/5] Validate", fg=typer.colors.CYAN)
    validate.validate_path(batch_dir)

    typer.secho("[2/5] Postprocess", fg=typer.colors.CYAN)
    postprocess.postprocess_batch(batch_dir, dry_run=False)

    typer.secho("[3/5] Re-validate", fg=typer.colors.CYAN)
    validate.validate_path(pp_file)

    typer.secho("[4/5] Export", fg=typer.colors.CYAN)
    export.export_dataset(
        batch_name=batch,
        output_name=batch,
        test_split=test_split,
        use_postprocessed=True,
        seed=seed,
        filter_failed=True,
    )

    all_file = batch_dir / "data" / "all.jsonl"
    if expand_pct > 0:
        typer.secho(f"[5/5] Expand ({expand_pct}%)", fg=typer.colors.CYAN)
        expand.expand_dataset(
            input_path=all_file,
            output_path=all_file.parent / "expanded.jsonl",
            percentage=expand_pct,
            seed=seed,
        )
    else:
        typer.secho("[5/5] Expand skipped", fg=typer.colors.CYAN)

    # Drop checkpoints once we have a finished dataset.
    for ckpt in batch_dir.glob("checkpoint_*.jsonl"):
        ckpt.unlink()

    typer.secho(f"\nDone. Output in {batch_dir / 'data'}/", fg=typer.colors.GREEN)


# --------------------------------------------------------------------------- #
# serve
# --------------------------------------------------------------------------- #
@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host."),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port."),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code changes (dev)."),
):
    """Launch the web UI to browse and review generated datasets."""
    import uvicorn

    typer.echo(f"Serving on http://{host}:{port}")
    uvicorn.run("synthfc.webapp.app:app", host=host, port=port, reload=reload)


# --------------------------------------------------------------------------- #
# merge
# --------------------------------------------------------------------------- #
@app.command()
def merge(
    inputs: list[Path] = typer.Argument(..., help="JSONL dataset files to merge."),
    output: Path = typer.Option(..., "--output", "-o", help="Output JSONL path."),
    dedup: bool = typer.Option(True, "--dedup/--no-dedup", help="Drop duplicate conversations."),
):
    """Merge multiple exported JSONL datasets into one."""
    from .pipeline import merge as merge_mod

    total = merge_mod.merge_datasets([str(p) for p in inputs], str(output), dedup=dedup)
    typer.secho(f"Wrote {total} conversations to {output}", fg=typer.colors.GREEN)


# --------------------------------------------------------------------------- #
# stats
# --------------------------------------------------------------------------- #
@app.command()
def stats(
    dataset: Path = typer.Argument(..., help="JSONL dataset to analyze."),
    tokenizer: Optional[str] = typer.Option(
        None, "--tokenizer", help="HF tokenizer name/path for token statistics."
    ),
):
    """Print token / length statistics for a dataset."""
    from .pipeline import token_stats

    token_stats.report(str(dataset), tokenizer)


# --------------------------------------------------------------------------- #
# sample
# --------------------------------------------------------------------------- #
@app.command()
def sample(
    n: int = typer.Option(5, "--num", "-n", help="How many parameter sets to preview."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML config file."),
):
    """Preview sampled generation parameters without calling the API."""
    from .core import sampler

    get_config(config)
    for i in range(n):
        params = sampler.sample_params()
        typer.echo(f"--- sample {i + 1} ---")
        typer.echo(json.dumps(params.to_dict(), ensure_ascii=False, indent=2))


# --------------------------------------------------------------------------- #
# batch-api (offline Azure / OpenAI Batch API path)
# --------------------------------------------------------------------------- #
@app.command(name="batch-api")
def batch_api(
    n: int = typer.Option(..., "--num", "-n", help="Number of examples to request."),
    resume: Optional[str] = typer.Option(None, "--resume", help="Resume an existing batch job id."),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML config file."),
):
    """Generate via the provider's offline Batch API (cheaper, slower)."""
    from .core import batch_api as ba

    get_config(config)
    ba.run(n=n, resume=resume)


if __name__ == "__main__":
    app()
