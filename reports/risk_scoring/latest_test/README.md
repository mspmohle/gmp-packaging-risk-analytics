# Risk Scoring Dashboard — Latest TEST Snapshot

This folder contains a **git-friendly snapshot** of the latest TEST exports from the panel risk-scoring pipeline.
It is intentionally small so it can be reviewed on GitHub without committing the full processed dataset.

## Quick links
- **Dashboard Report (Markdown):** `DASHBOARD_REPORT_TEST.md`
- **Alert queue (latest day):** `dashboard_alert_queue_latest_day_test.csv`
- **Top sites (latest day):** `dashboard_top_sites_latest_day_test.csv`
- **Top lines (latest day):** `dashboard_top_lines_latest_day_test.csv`
- **Daily trend (last 14 days):** `dashboard_daily_trend_last14_test.csv`
- **KPIs / provenance:** `dashboard_kpis_test.json`
- **API-ready payload:** `dashboard_payload_test.json`

## Figures
- `figures/daily_risk_trend_test.png`
- `figures/daily_positive_hours_test.png`
- `figures/alert_queue_latest_day_test.png`
- `figures/top_sites_latest_day_test.png`

## Notes
- TEST outputs are produced from a grouped-by-asset split and a Top-5 assets/day alert budget.
- For full raw/processed artifacts, see the run directory under `data/processed/risk_scoring/<export_run_id>/` (not committed).