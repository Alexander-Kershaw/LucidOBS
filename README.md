***
# LucidOBS
***

**ICU telemetry observability demo: OpenTelemetry → Prometheus/Loki → Grafana dashboards with alerts**

## Quickstart 
```bash
pip install -e .
lucidobs up
```

---

## Architecture Diagram

```mermaid
flowchart LR

Generator[Telemetry Generator<br>Python]
Collector[OpenTelemetry Collector]
Prometheus[Prometheus<br>Metrics DB]
Loki[Loki<br>Logs DB]
Grafana[Grafana<br>Dashboards + Alerts]

Generator -->|OTLP| Collector
Collector -->|Metrics| Prometheus
Collector -->|Logs| Loki
Prometheus --> Grafana
Loki --> Grafana
```

---