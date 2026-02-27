from __future__ import annotations

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


if __name__ == "__main__":
    app()