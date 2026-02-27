from __future__ import annotations

from pathlib import Path
from lucidobs.telemetry.generator import run_logs

import subprocess
import typer

app = typer.Typer(help="LucidOBS: ICU Telemetry Observability Platform")


def _run(cmd: list[str]) -> None:
    typer.echo(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


@app.command()
def up(detach: bool = True) -> None:
    """Boots the local observability stack (Grafana, Prometheus, Loki, OTel Collector)."""
    cmd = ["docker", "compose", "up"]
    if detach:
        cmd.append("-d")
    _run(cmd)
    typer.echo("Grafana: http://localhost:3000 (admin/admin)")
    typer.echo("Prometheus: http://localhost:9090")
    typer.echo("Loki: http://localhost:3100")
    typer.echo("OTel health: http://localhost:13133")


@app.command()
def down(volumes: bool = False) -> None:
    """Stops the stack. Use --volumes to wipe persisted data (full clean refresh)."""
    cmd = ["docker", "compose", "down"]
    if volumes:
        cmd.append("-v")
    _run(cmd)


@app.command()
def run(
    patients: int = typer.Option(10, help="Number of simulated ICU patients."),
    rate: float = typer.Option(1.0, help="Seconds between emitted samples."),
    seed: int = typer.Option(42, help="Random seed for deterministic output."),
    out: str = typer.Option("runtime/logs/telemetry.jsonl", help="JSONL output path."),
) -> None:
    
    # Generates ICU patient telemetry logs (structured JSON) to stdout + file for Loki ingestion.
    
    out_path = Path(out)
    typer.echo(f"=====|Writing logs to: {out_path}|=====")
    typer.echo("Press Ctrl+C to stop.")
    run_logs(patients=patients, rate_seconds=rate, seed=seed, out_path=out_path)


if __name__ == "__main__":
    app()