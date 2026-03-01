from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone

from lucidobs.telemetry.generator import run_logs

import subprocess
import typer
import json

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


@app.command()
def inject(
    event: str = typer.Option(..., help="Scenario name: spo2_drop | tachycardia | hypotension | dropout"),
    patient: str = typer.Option(..., help="Patient id like P003"),
    duration: int = typer.Option(120, help="Duration in seconds"),
    path: str = typer.Option("runtime/scenarios/overrides.json", help="Override file path"),
) -> None:
    
    # Injects a deterministic scenario for a patient by writing an override file the generator reads

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    until_ts = now + timedelta(seconds=duration)

    # Map scenario to forced values
    if event == "spo2_drop":
        set_values = {"spo2_pct": 82}
    elif event == "tachycardia":
        set_values = {"heart_rate_bpm": 155}
    elif event == "hypotension":
        set_values = {"sys_bp_mmhg": 78, "dia_bp_mmhg": 48}
    else:
        raise typer.BadParameter(f"Unknown event: {event}")

    # Load existing overrides
    payload = {}
    if out_path.exists():
        try:
            payload = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}

    payload[patient] = {
        "until_ts": until_ts.isoformat(),
        "event": event,
        "set": set_values,
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    typer.echo(f"Injected {event} for {patient} until {until_ts.isoformat()}")


if __name__ == "__main__":
    app()