# Risk Scoring Dashboard Exports (TEST)

- **Latest day:** `2025-12-11`
- **Alerts budget:** Top-5 assets/day (queue rows = `5`)
- **Mean alert score (p̂):** `0.248`
- **Max alert score (p̂):** `0.297`
- **Trend window:** `14` days (`2025-11-28` → `2025-12-11`)

## Files (API-ready)
- `dashboard_payload_test.json` — single JSON payload for API responses
- `dashboard_kpis_test.json` — KPI summary + provenance

## Tables (CSV)
- `dashboard_alert_queue_latest_day_test.csv` — Top-5 asset alerts for the latest day (+ “why”)
- `dashboard_top_sites_latest_day_test.csv` — Site rollup for the latest day
- `dashboard_top_lines_latest_day_test.csv` — Line rollup for the latest day
- `dashboard_daily_trend_last14_test.csv` — 14-day trend table

## Figures
- `figures/daily_risk_trend_test.png`
- `figures/daily_positive_hours_test.png`
- `figures/alert_queue_latest_day_test.png`
- `figures/top_sites_latest_day_test.png`

## Notes
- These artifacts are copied from `data/processed/risk_scoring/latest_test/` into `reports/` so they can be committed to GitHub safely.
- The underlying full datasets and large intermediate artifacts remain under `data/` and stay out of git by design.

## Quick Preview

### Alert Queue (latest day, first 5 rows)

| date_utc   | asset_id   | ts_peak                   |    p_hat | site_id   | line_id   | asset_type        | is_legacy   | why_push_to_1                                                                                    | why_push_to_0                                                          |
|:-----------|:-----------|:--------------------------|---------:|:----------|:----------|:------------------|:------------|:-------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------|
| 2025-12-11 | A0011      | 2025-12-11 00:00:00+00:00 | 0.29737  | S1        | S1-L3     | vision_inspection | False       | is_weekend_utc(+0.314); asset_type_vision_inspection(+0.300); telemetry_rows_hour(+0.173)        | is_legacy(-0.683); dow_utc_cos(-0.508); site_id_S1(-0.332)             |
| 2025-12-11 | A0032      | 2025-12-11 00:00:00+00:00 | 0.275497 | S4        | S4-L3     | vision_inspection | False       | line_speed_u_min_tele_mean(+0.452); is_weekend_utc(+0.314); asset_type_vision_inspection(+0.300) | is_legacy(-0.683); dow_utc_cos(-0.508); line_id_S4-L3(-0.285)          |
| 2025-12-11 | A0065      | 2025-12-11 00:00:00+00:00 | 0.251767 | S3        | S3-L5     | labeler           | False       | line_id_S3-L5(+0.553); is_weekend_utc(+0.314); telemetry_rows_hour(+0.186)                       | is_legacy(-0.683); dow_utc_cos(-0.508); asset_type_labeler(-0.409)     |
| 2025-12-11 | A0108      | 2025-12-11 00:00:00+00:00 | 0.250631 | S1        | S1-L4     | cartoner          | False       | is_weekend_utc(+0.314); asset_type_cartoner(+0.266); telemetry_rows_hour(+0.159)                 | is_legacy(-0.683); dow_utc_cos(-0.508); site_id_S1(-0.332)             |
| 2025-12-11 | A0012      | 2025-12-11 00:00:00+00:00 | 0.16361  | S4        | S4-L3     | weigh_check       | False       | is_weekend_utc(+0.314); telemetry_rows_hour(+0.173); line_speed_u_min_tele_max(+0.108)           | is_legacy(-0.683); dow_utc_cos(-0.508); asset_type_weigh_check(-0.411) |