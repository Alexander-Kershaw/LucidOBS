from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

"""
Inject scenarios into telemetry generator deterministically with CLI

Forces values for a given patient for a specified duration
"""

DEFAULT_OVERRIDE_PATH = Path("runtime/scenarios/overrides.json")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


@dataclass
class Override:
    patient_id: str
    until_ts: datetime
    event: str
    set_values: Dict[str, Any]


def load_overrides(path: Path = DEFAULT_OVERRIDE_PATH) -> Dict[str, Override]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    overrides: Dict[str, Override] = {}
    for patient_id, payload in data.items():
        try:
            until_ts = _parse_dt(payload["until_ts"])
            event = payload.get("event", "override")
            set_values = payload.get("set", {})
            overrides[patient_id] = Override(
                patient_id=patient_id,
                until_ts=until_ts,
                event=event,
                set_values=set_values,
            )
        except Exception:
            continue

    # Drop expired
    now = _now()
    overrides = {k: v for k, v in overrides.items() if v.until_ts > now}
    return overrides


def apply_override(patient_id: str, vitals: Dict[str, Any], overrides: Dict[str, Override]) -> Dict[str, Any]:
    ov = overrides.get(patient_id)
    if not ov:
        return vitals

    # Apply injected scenario values
    out = dict(vitals)
    for k, v in ov.set_values.items():
        out[k] = v

    # Logging metadata
    out["_scenario"] = ov.event
    return out