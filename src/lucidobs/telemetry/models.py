from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

# Distingush events into 3 categories
EventType = Literal["telemetry_sample", "clinical_event", "system_event"]

# Patient log dataclass (includes all base patient telemetry)
@dataclass(frozen=True)
class TelemetryLog:
    ts: str
    job: str
    patient_id: str
    ward: str
    device_id: str
    event: EventType

    heart_rate_bpm: int
    spo2_pct: int
    resp_rate_bpm: int
    sys_bp_mmhg: int
    dia_bp_mmhg: int
    temp_c: float

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()