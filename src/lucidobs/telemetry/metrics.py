from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from opentelemetry import metrics
from opentelemetry.metrics import Observation
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


Key = Tuple[str, str, str]  # Key identifiers (patient_id, ward, device_id)


@dataclass
class Vitals:
    heart_rate_bpm: float
    spo2_pct: float
    resp_rate_bpm: float
    sys_bp_mmhg: float
    dia_bp_mmhg: float
    temp_c: float


class MetricsSink:
    """
    MetricsSink stores latest vitals per patient and exposes them via ObservableGauges.
    Prometheus will scrape them from the collector's Prometheus exporter.
    """

    def __init__(self, otlp_endpoint: str = "http://localhost:4318") -> None:
        self._latest: Dict[Key, Vitals] = {}

        resource = Resource.create({"service.name": "lucidobs"})
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otlp_endpoint),
            export_interval_millis=2000,
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)

        self._meter = metrics.get_meter("lucidobs.telemetry", "0.1.0")

        # Observable gauges
        self._meter.create_observable_gauge(
            name="icu_heart_rate_bpm",
            callbacks=[self._obs_hr],
            description="ICU heart rate",
            unit="bpm",
        )
        self._meter.create_observable_gauge(
            name="icu_spo2",
            callbacks=[self._obs_spo2],
            description="ICU oxygen saturation",
            unit="percent",
        )
        self._meter.create_observable_gauge(
            name="icu_resp_rate_bpm",
            callbacks=[self._obs_rr],
            description="ICU respiratory rate",
            unit="breaths/min",
        )
        self._meter.create_observable_gauge(
            name="icu_sys_bp_mmhg",
            callbacks=[self._obs_sys],
            description="ICU systolic blood pressure",
            unit="mmHg",
        )
        self._meter.create_observable_gauge(
            name="icu_dia_bp_mmhg",
            callbacks=[self._obs_dia],
            description="ICU diastolic blood pressure",
            unit="mmHg",
        )
        self._meter.create_observable_gauge(
            name="icu_temp_c",
            callbacks=[self._obs_temp],
            description="ICU temperature",
            unit="C",
        )

    def update(self, patient_id: str, ward: str, device_id: str, vitals: Vitals) -> None:
        self._latest[(patient_id, ward, device_id)] = vitals

    def _iter_measurements(self):
        for (patient_id, ward, device_id), v in self._latest.items():
            attrs = {"patient_id": patient_id, "ward": ward, "device_id": device_id}
            yield attrs, v

    def _obs_hr(self, _options):
        for attrs, v in self._iter_measurements():
            yield Observation(v.heart_rate_bpm, attrs)

    def _obs_spo2(self, _options):
        for attrs, v in self._iter_measurements():
            yield Observation(v.spo2_pct, attrs)

    def _obs_rr(self, _options):
        for attrs, v in self._iter_measurements():
            yield Observation(v.resp_rate_bpm, attrs)

    def _obs_sys(self, _options):
        for attrs, v in self._iter_measurements():
            yield Observation(v.sys_bp_mmhg, attrs)

    def _obs_dia(self, _options):
        for attrs, v in self._iter_measurements():
            yield Observation(v.dia_bp_mmhg, attrs)

    def _obs_temp(self, _options):
        for attrs, v in self._iter_measurements():
            yield Observation(v.temp_c, attrs)