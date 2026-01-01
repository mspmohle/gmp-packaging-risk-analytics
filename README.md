In progress

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

bash
conda env create -f environment.yml -n gmp-packaging-risk-analytics || conda env update -f environment.yml -n gmp-packaging-risk-analytics
conda activate gmp-packaging-risk-analytics
python -V

### 2) Run the notebooks (in order)

Run each notebook **top-to-bottom**:

- `00_env_and_paths_sanity.ipynb`
- `01_synthetic_iot_data_generator.ipynb`
- `02_feature_engineering_and_labels.ipynb`
- `03_risk_scoring_and_dashboard_exports.ipynb`

### 3) Verify exports were published
ls -lah EXPORTS.json
ls -lah data/processed/risk_scoring/latest_test | head




