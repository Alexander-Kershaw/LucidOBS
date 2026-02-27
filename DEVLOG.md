***
# LucidOBS DEVLOG
***
## Repo skeleton
**TODO**
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


### Screenshots

#### Grafana Datasources Provisioned

![Grafana Datasources](assets/screenshots/grafana_datasources.png)

Grafana automatically provisioned Prometheus and Loki datasources via configuration files. This confirms the visualization layer is correctly connected to both metrics and log backends without manual UI setup.

---

#### Prometheus Scrape Targets Healthy

![Prometheus Targets](assets/screenshots/prometheus_targets.png)

Prometheus successfully scrapes the OpenTelemetry Collector Prometheus exporter endpoint. This verifies:

- Docker network connectivity
- Collector exporter configuration correctness
- Prometheus scrape configuration validity

This confirms that the telemetry pipeline is structurally functional.

---

#### OpenTelemetry Collector Health Endpoint

![Collector Health](assets/screenshots/collector_health.png)

The collector health endpoint confirms the OpenTelemetry Collector service is running and accepting telemetry. This service acts as the central routing hub for all telemetry signals in LucidOBS.


---

**status: COMPLETE**

Stack boots successfully. Prometheus confirms collector scrape target healthy. Grafana datasources provisioned automatically.

---

## Structured logs → Loki → Grafana
**TODO**
- Python telemetry generator that emits structured JSON logs (JSONL) to stdout and `runtime/logs/telemetry.jsonl`
- OpenTelemetry Collector `filelog` receiver tails the JSONL file and exports logs to Loki
- Grafana dashboard **“LucidOBS - Latest Events”** to view recent telemetry events

**Why this design**
- Used the OTel Collector `filelog` receiver instead of adding Promtail to keep the system smaller and easier to review.
- Logs are written locally first (file and stdout), then ingested by the observability pipeline. This makes it local-first and makes it easy to debug by inspecting the raw log file.

**Key concepts**
- **Structured logging**: logs are JSON objects, not free-text. This makes filtering and parsing more reliable.
- **JSONL**: one JSON object per line. It’s append-friendly and tail-friendly, favourable for logs.
- **Loki**: log store optimized for indexing labels and scanning log content.
- **LogQL**: Loki’s query language. Starts with `{service_name="lucidobs"}` to retrieve all LucidOBS logs.

**Verification**
1) Booted the stack: `lucidobs up`
2) Generated logs: `lucidobs run --patients 10 --rate 1 --seed 42`
3) Confirmed file output: `tail -n 5 runtime/logs/telemetry.jsonl`
4) In Grafana (Explored Loki), query: `{service_name="lucidobs"}`
5) New telemetry_sample log lines continuously appeared

---

### Screenshots

#### Live ICU Telemetry Log Stream (Grafana Dashboard)

![Latest Events Dashboard](assets/screenshots/logs_dashboard.png)

Grafana dashboard displaying real-time ICU telemetry logs ingested via the OpenTelemetry Collector and stored in Loki.

End-to-end log ingestion pipeline functionality is confirmed.

---

#### LogQL Query in Grafana Explore

![Grafana Explore LogQL](assets/screenshots/logs_explore.png)

Direct LogQL query `{service_name="lucidobs"}` retrieving structured telemetry events.

This verifies logs are indexed and queryable independently of dashboards.

---

#### Raw JSONL Telemetry File

![Telemetry JSONL Tail](assets/screenshots/log_file_tail.png)

Local JSONL log file written by the telemetry generator.

This demonstrates the source of truth for telemetry before ingestion into the observability pipeline.

---

**status: COMPLETE**

Patient logs are streamed displaying real-time ICU telemetry logs on the Grafana dashboard.

---