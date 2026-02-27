from __future__ import annotations

import json
import random
import time
from pathlib import Path

from lucidobs.telemetry.models import TelemetryLog
from lucidobs.telemetry.metrics import MetricsSink, Vitals


def _patient_ids(n: int) -> list[str]:
    return [f"P{i:03d}" for i in range(1, n + 1)]


def _baseline_vitals(rng: random.Random) -> dict:
    # Basic patient vitals
    hr = int(rng.normalvariate(80, 8))
    spo2 = int(rng.normalvariate(97, 1))
    rr = int(rng.normalvariate(16, 2))
    sys = int(rng.normalvariate(120, 10))
    dia = int(rng.normalvariate(80, 8))
    temp = round(rng.normalvariate(36.8, 0.2), 2)

    # Bound vitals to plausible ranges 
    hr = max(35, min(hr, 180))
    spo2 = max(50, min(spo2, 100))
    rr = max(6, min(rr, 40))
    sys = max(60, min(sys, 200))
    dia = max(30, min(dia, 130))
    temp = max(34.0, min(temp, 41.0))

    return {
        "heart_rate_bpm": hr,
        "spo2_pct": spo2,
        "resp_rate_bpm": rr,
        "sys_bp_mmhg": sys,
        "dia_bp_mmhg": dia,
        "temp_c": temp,
    }

# Create patient logs
def run_logs(
    patients: int,
    rate_seconds: float,
    seed: int,
    out_path: Path,
    ward: str = "ICU-A",
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    pids = _patient_ids(patients)
    metrics_sink = MetricsSink(otlp_endpoint="http://localhost:4318/v1/metrics")

    # Line-buffered append
    with out_path.open("a", encoding="utf-8") as f:
        while True:
            pid = rng.choice(pids)
            vitals = _baseline_vitals(rng)

            log = TelemetryLog(
                ts=TelemetryLog.now_iso(),
                job="lucidobs",
                patient_id=pid,
                ward=ward,
                device_id=f"dev-{pid}",
                event="telemetry_sample",
                **vitals,
            )

            # Latest vitals metrics to export to collector
            metrics_sink.update(
                patient_id=pid,
                ward=ward,
                device_id=f"dev-{pid}",
                vitals=Vitals(
                    heart_rate_bpm=log.heart_rate_bpm,
                    spo2_pct=log.spo2_pct,
                    resp_rate_bpm=log.resp_rate_bpm,
                    sys_bp_mmhg=log.sys_bp_mmhg,
                    dia_bp_mmhg=log.dia_bp_mmhg,
                    temp_c=log.temp_c,
                ),
            )

            payload = json.dumps(log.__dict__, ensure_ascii=False)
            print(payload)          # stdout
            f.write(payload + "\n") # file
            f.flush()

            time.sleep(rate_seconds)