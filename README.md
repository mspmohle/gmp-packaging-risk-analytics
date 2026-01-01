# GMP Packaging Risk Analytics

A portfolio-grade, end-to-end analytics pipeline that simulates (and can later ingest) GMP packaging process signals, engineers risk features + labels, produces **dashboard-ready risk scoring exports**, and serves the latest results through a lightweight **FastAPI** service.

This repo is designed to demonstrate:
- **Reproducible analytics engineering** (consistent paths, artifacts, and exports indexing)
- **Feature engineering + labeling** for operational risk (asset/hour → asset/day → dashboard KPIs)
- **Risk scoring + prioritization** (top-K alerting and precision@K diagnostics)
- **Operationalization** via an API layer that exposes the latest exports for dashboards and downstream tools

## Why this project

GMP packaging operations generate high-volume signals across assets, lines, and sites (sensor readings, alarms, downtime markers, quality checks, environmental conditions, and operator inputs). The challenge is turning that noisy telemetry into a **reliable, explainable prioritization workflow**:

- Which assets or lines look most “at risk” *today*?
- Which sites show emerging patterns that merit review?
- How do we measure whether the alerting policy is actually useful?

This project builds a complete demonstration pipeline that converts raw panel-style process signals into:
1) **engineered features and labels**
2) **risk scores and ranked alert queues**
3) **dashboard exports** (CSV/JSON/PNG/ZIP)
4) a small **API** that serves the latest exports for consumption by dashboards or downstream applications

The current implementation uses **synthetic data generation** to make the workflow reproducible and safe for public sharing. The structure is intentionally built so a real GMP/packaging dataset can be swapped in later with minimal changes to downstream steps.

## What’s included

### Pipeline stages (notebooks)

This repo is organized as a clear, linear pipeline:

1. **00_env_and_paths_sanity.ipynb**  
   Establishes reproducible paths and validates the runtime environment.

2. **01_synthetic_iot_data_generator.ipynb**  
   Generates synthetic, panel-style GMP/packaging telemetry suitable for downstream feature engineering and scoring.

3. **02_feature_engineering_and_labels.ipynb**  
   Builds model-ready features and operational labels (e.g., hour-level → day-level aggregation) to support prioritization and evaluation.

4. **03_risk_scoring_and_dashboard_exports.ipynb**  
   Computes risk scores, ranks alert candidates, generates KPI summaries, and publishes a **dashboard export bundle**.

### Key outputs (artifacts)

The pipeline publishes a “latest” export directory that is designed for direct dashboard consumption:

- **CSV**: alert queues, top sites/lines, daily trend tables  
- **JSON**: KPI summary and metadata for dashboards  
- **PNG**: trend visuals and at-a-glance charts  
- **ZIP**: a single bundle containing all dashboard artifacts  

The API layer exposes these artifacts through stable endpoints so a dashboard or consumer does not need to know file paths.
## Repository structure

```text
.
├── 00_env_and_paths_sanity.ipynb
├── 01_synthetic_iot_data_generator.ipynb
├── 02_feature_engineering_and_labels.ipynb
├── 03_risk_scoring_and_dashboard_exports.ipynb
├── EXPORTS.json
├── environment.yml
├── data/
│   └── processed/                    # gitignored (local run outputs)
├── reports/
│   └── risk_scoring/
│       └── latest_test/              # markdown summaries (repo-visible)
├── scripts/
│   └── run_api.sh                    # helper to start the FastAPI service
└── src/
    ├── __init__.py
    └── app/
        ├── __init__.py
        └── main.py                   # FastAPI app serving latest exports
```
### Notes on version control

- Large generated artifacts and run outputs under `data/processed/**` are intentionally not committed.
- `EXPORTS.json` is committed and acts as the **portable index** for locating the most recent published exports.
- Reports under `reports/` are intended to be lightweight, human-readable summaries of the latest run.

## End-to-end quickstart (notebooks → exports → API)

### 1) Create/update the environment (conda)

```bash
conda env create -f environment.yml -n gmp-packaging-risk-analytics || conda env update -f environment.yml -n gmp-packaging-risk-analytics
conda activate gmp-packaging-risk-analytics
python -V
```
### 2) Run the notebooks (in order)

Run each notebook **top-to-bottom**:

- `00_env_and_paths_sanity.ipynb`
- `01_synthetic_iot_data_generator.ipynb`
- `02_feature_engineering_and_labels.ipynb`
- `03_risk_scoring_and_dashboard_exports.ipynb`

### 3) Verify exports were published

```bash
ls -lah EXPORTS.json
ls -lah data/processed/risk_scoring/latest_test | head
```
## Health
curl -s http://127.0.0.1:8000/health

## View the latest exports index (first few lines)
curl -s http://127.0.0.1:8000/exports/index | head -n 20

## Resolve the latest risk scoring bundle location
curl -s "http://127.0.0.1:8000/exports/resolve?key=risk_scoring.latest_test" | python -m json.tool

## Fetch KPI JSON
curl -s "http://127.0.0.1:8000/exports/file?key=risk_scoring.latest_test.files.dashboard_kpis_test.json" | python -m json.tool

## Fetch a CSV as plain text
curl -s "http://127.0.0.1:8000/exports/file?key=risk_scoring.latest_test.files.dashboard_daily_trend_last14_test.csv&as_text=true" | head -n 15

## Metrics & evaluation

This project frames risk scoring as an **operational prioritization** problem: given limited reviewer attention, surface the most actionable assets/lines/sites first.

### Alerting policy (budgeted review)

For each UTC day, the pipeline selects a fixed number of “alert” candidates (a review budget), using a simple policy such as:

- **Top-K assets per day**: choose the K assets with the highest predicted risk for that day

This produces an interpretable daily “alert queue” that can be monitored over time and consumed directly by a dashboard.

### precision@K (operational usefulness)

To evaluate whether the alert queue is useful, the pipeline computes **precision@K**:

- For a given day, among the **K alerted assets**, what fraction were truly “positive” (according to the label definition)?
- Reported as a value in \[0, 1\], where higher is better.

In the exported dashboard metrics, precision@K is computed on an **asset-day label** derived from the underlying hour-level labels, for example:

- `y_asset_day = max(y_true_hour)` over all hours for that asset on that UTC date

This matches common operational workflows: an asset-day is considered “positive” if **any** hour in that day triggered the target condition.

### What to look for in the exports

The `latest_test` dashboard exports include daily trend tables and KPIs that help answer:

- Is the alert queue stable or noisy day-to-day?
- Are we maintaining acceptable precision@K under the chosen budget?
- Do risk levels cluster by site/line (suggesting systemic issues) or appear isolated (suggesting local events)?

## Outputs & dashboard exports

After running `03_risk_scoring_and_dashboard_exports.ipynb`, the pipeline publishes a “latest” export bundle under:

- `data/processed/risk_scoring/latest_test/`

This directory is designed to be **dashboard-ready** (CSV/JSON/PNG) and is indexed by `EXPORTS.json`.

### Key exported files

#### KPI summary (JSON)

- `dashboard_kpis_test.json`  
  Compact KPI payload intended for a dashboard “top row” (run metadata, scope, date range, alerting policy, and evaluation summaries such as precision@K).

#### Daily trend table (CSV)

- `dashboard_daily_trend_last14_test.csv`  
  Day-level trend metrics for the most recent window (e.g., number of positive hours, positive rate, alert counts, precision@K by day). Useful for time-series dashboard panels and QA.

#### Alert queue (CSV + PNG)

- `dashboard_alert_queue_latest_day_test.csv`  
  The ranked set of alert candidates for the most recent day (what gets reviewed today).

- `alert_queue_latest_day_test.png`  
  A quick visual representation of the latest-day alert queue.

#### Top entities (CSVs + PNGs)

- `dashboard_top_sites_latest_day_test.csv` / `top_sites_latest_day_test.png`  
  Highest-risk sites for the latest day.

- `dashboard_top_lines_latest_day_test.csv`  
  Highest-risk lines for the latest day (dashboard table view).

#### Trend visuals (PNGs)

- `daily_risk_trend_test.png`  
  Risk trend over the recent window.

- `daily_positive_hours_test.png`  
  Trend of positive-hour counts/rates over the recent window.

#### Bundle (ZIP)

- `dashboard_bundle_test.zip`  
  A single zipped bundle containing the dashboard artifacts for easy sharing or handoff.

#### Bundle index (JSON)

- `DASHBOARD_EXPORTS.json`  
  A small, local index of the files inside the latest export directory (useful for simple dashboards or scripts).

### Run index (repo root)

- `EXPORTS.json` (repo root)  
  The authoritative pointer to the most recently published export directories and files. The API serves this index via `GET /exports/index`.

## How the API maps to exports

The API is intentionally file-centric: it reads `EXPORTS.json` and exposes the most recent published artifacts without hard-coding paths into the client.

### EXPORTS.json structure (high level)

At minimum, the index contains a structure like:

- `risk_scoring.latest_test.run_id`
- `risk_scoring.latest_test.export_dir`
- `risk_scoring.latest_test.published_dir`
- `risk_scoring.latest_test.pointer`
- `risk_scoring.latest_test.files.<filename>`

Where `files` is a dictionary mapping filenames to absolute paths. Filenames may include dots (e.g., `dashboard_kpis_test.json`), and the API supports that.

### API usage pattern

1. Query the current index:
   - `GET /exports/index`

2. Resolve a logical key to a path (optional diagnostics):
   - `GET /exports/resolve?key=risk_scoring.latest_test`

3. Retrieve a specific artifact by key:
   - `GET /exports/file?key=risk_scoring.latest_test.files.dashboard_kpis_test.json`

### Example keys

- Latest export directory:  
  `risk_scoring.latest_test.published_dir`

- KPI JSON:  
  `risk_scoring.latest_test.files.dashboard_kpis_test.json`

- Daily trend CSV:  
  `risk_scoring.latest_test.files.dashboard_daily_trend_last14_test.csv`

## Reproducibility & adapting to real data

### Environment reproducibility

This repo provides an `environment.yml` for a consistent conda environment. For portfolio review, the key goals are:

- consistent Python version and core data stack
- deterministic notebook execution (where applicable)
- stable output locations and export indexing via `EXPORTS.json`

### Deterministic runs (recommended practice)

Where randomness is used (e.g., synthetic data generation), the notebooks are designed to support:

- a fixed RNG seed
- a run timestamp / run_id that is recorded in exports
- clean “latest” publishing that overwrites only the **latest pointer**, not historical run directories

This supports both:
- reproducible debugging, and
- a simple “always point dashboards to the latest run” workflow.

### Swapping in real GMP/packaging data

The pipeline is intentionally modular:

- **Notebook 01** can be replaced with a real ingestion notebook (database extract, historian export, CSV drops, etc.).
- **Notebook 02** expects a panel-style dataset and performs feature + label construction.
- **Notebook 03** expects engineered features and produces scores + dashboard exports.

To adapt this repo to real data, the typical steps are:

1. Replace the synthetic generator with an ingestion routine that produces the same core columns and time granularity.
2. Keep feature/label logic stable (or document changes), since it defines what “risk” means operationally.
3. Preserve the export contract (`latest_test/` contents + `EXPORTS.json`) so the API and dashboards remain unchanged.

## Roadmap / extensions

This repo is intentionally scoped as a portfolio-grade, end-to-end prototype. The most natural next steps toward production readiness would include:

### Modeling improvements

- Replace baseline scoring with a trained model (e.g., gradient boosting) and track calibration and drift.
- Add feature attribution (e.g., SHAP) to explain why a site/line/asset is flagged.
- Support multiple risk “modes” (quality deviation risk, downtime risk, environmental excursion risk).

### Operational robustness

- Add unit tests for export contracts (required filenames/columns) and API key resolution.
- Add a lightweight “data contract” check (schema validation) between Notebook 02 and Notebook 03.
- Add CI checks that validate the API starts and the OpenAPI schema is generated.

### Dashboard / delivery

- Add a simple static dashboard (e.g., Streamlit) that consumes `/exports/file`.
- Add authentication (token) if serving beyond localhost.
- Provide an optional “publish to S3” step (store artifacts and serve via signed URLs).

### Data ingestion (real-world)

- Replace synthetic generation with ingestion from historians, MES, QMS, or environmental monitoring systems.
- Add mapping layers for site/line/asset hierarchies and reference data (CAPA records, maintenance logs).

## About

Built by **Michael Mohle** as a portfolio project focused on analytics engineering and operational risk workflows in regulated (GMP) environments.

If you’d like to discuss this project or collaborate, please reach at mohle.michael.s@gmail.com  .

## License

This project is released under the license included in this repository. See the `LICENSE` file for details.

