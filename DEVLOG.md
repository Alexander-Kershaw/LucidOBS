# LucidOBS DEVLOG

## Repo skeleton
**Completions**
- Docker Compose stack: Grafana, Prometheus, Loki, OpenTelemetry Collector
- Grafana provisioning for datasources (Prometheus + Loki)
- Stub CLI (`lucidobs up`, `lucidobs down`)

**Why this design**
- Local-first, no Kubernetes: emphasis is on observability concepts for now.
- Grafana provisioning for convenient dashboards and datasources appearing without manual setup.
- Prometheus scrapes the OTel Collector’s Prometheus exporter endpoint. Even before ICU vitals are generated and emitted, this gives a real target to validate wiring and networking.

**Key concepts**
- **OpenTelemetry (OTel)** is the standard API and protocol family for emitting telemetry (metrics/logs/traces).
- **OTLP** is the transport format used by OTel SDKs to send telemetry to a collector (HTTP or gRPC).
- **Collector** is a router: it receives telemetry, optionally processes it (batching, filtering), then exports it elsewhere.
- **Prometheus** is pull-based: it scrapes an HTTP endpoint on a refresh schedule.
- **Grafana** visualizes data and manages alerts; it reads from datasources like Prometheus (metrics) and Loki (logs) to a central dashboard platform.
- **Loki** stores logs and is queried with **LogQL**.

**Verification**
1) Boot stack:
   - `lucidobs up`
2) Open Grafana:
   - http://localhost:3000 (admin/admin)
   - Confirm datasources exist: Prometheus + Loki
3) Verify Prometheus target is healthy:
   - Prometheus: http://localhost:9090
   - Prometheus target: http://localhost:9090/targets
   - Expect `otel-collector` target to be **UP**
4) Verify collector health endpoint:
   - http://localhost:13133

**Screenshots**
- Grafana home page showing datasources present
- Prometheus Targets page showing `otel-collector` is UP