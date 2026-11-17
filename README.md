# Insurance Claims — End-to-End Data Pipeline

A portfolio project demonstrating a complete data engineering pipeline: from synthetic data generation to a SQL analytics layer and an interactive HTML dashboard.

---

## Overview

This pipeline processes 200 synthetic insurance claims through 6 sequential steps — ingestion, cleaning, validation, star-schema loading, SQL queries with window functions, and a browser-based dashboard.

**Tech stack:** Python · pandas · SQLAlchemy · SQLite · Chart.js

---

## Project Structure

```
insurance_pipeline/
├── src/
│   ├── config.py               # Central settings & constants
│   ├── 02_generate_data.py     # Synthetic data generation (with intentional errors)
│   ├── 03_ingest.py            # CSV ingestion & type casting
│   ├── ingest_utils.py         # Shared ingestion helper (DRY)
│   ├── 04_clean_validate.py    # Data cleaning & business rule validation
│   ├── 05_load_db.py           # Star schema creation & DB load
│   └── 06_run_queries.py       # SQL analytics queries
├── sql/
│   └── queries.sql             # 5 analytical SQL queries
├── dashboard/
│   └── index.html              # Interactive dashboard (Chart.js)
└── data/                       # Generated at runtime (not tracked)
```

---

## Pipeline Steps

| Step | Script | Description |
|------|--------|-------------|
| 1 | `config.py` | Constants: paths, limits, seed |
| 2 | `02_generate_data.py` | 200 synthetic claims with intentional dirty data |
| 3 | `03_ingest.py` | Load CSV, validate schema, cast types |
| 4 | `04_clean_validate.py` | Remove duplicates, fix negatives, fill nulls, validate rules |
| 5 | `05_load_db.py` | Build star schema in SQLite, compute derived fields |
| 6 | `06_run_queries.py` | Run 5 analytical SQL queries |
| 7 | `dashboard/index.html` | Visualise results in browser |

---

## Star Schema

```
dim_policy_types ──┐
dim_regions      ──┤── fact_claims
dim_customers    ──┘
```

**Computed fields in `fact_claims`:**
- `settlement_ratio` = settlement_amount / claim_amount
- `days_to_settle` = settlement_date − claim_date
- `risk_tier` = LOW / MEDIUM / HIGH / CRITICAL (based on claim amount)

---

## 📊 SQL Queries

| Query | Concept |
|-------|---------|
| Q1 — Exposure per policy type | `GROUP BY`, `JOIN`, `SUM`, `AVG` |
| Q2 — Approval rate per type | `CASE WHEN`, percentage calculation |
| Q3 — Risk tier breakdown | Custom `ORDER BY CASE` |
| Q4 — Top 10 claims | `ROW_NUMBER() OVER (ORDER BY ...)` |
| Q5 — Monthly running total | `SUM() OVER (ORDER BY ...)` |

---

## How to Run

```bash
# 1. Install dependencies
pip install pandas sqlalchemy

# 2. Generate data
python src/02_generate_data.py

# 3. Clean & validate
python src/04_clean_validate.py

# 4. Load to SQLite
python src/05_load_db.py

# 5. Run SQL queries
python src/06_run_queries.py

# 6. Open dashboard
# Double-click dashboard/index.html in your browser
```

---

## Key Findings

- **LIFE** insurance: highest avg claim (€89,140) but lowest volume (22 claims)
- **AUTO** insurance: most frequent (78 claims) with avg €8,562
- **LIFE** has the highest approval rate at **72.7%**
- Total portfolio exposure 2022–2024: **€4.34M**
- All Top 10 largest claims belong to LIFE policy type

## Skills Gained

- **End-to-end pipeline design:** structuring a modular ETL pipeline in Python (generate → ingest → clean → load → query → visualise), with central configuration and reusable helpers
- **Data ingestion:** loading CSV data, validating the schema and casting data types with pandas
- **Data cleaning & validation:** removing duplicates, fixing negative values, handling nulls and enforcing business rules on deliberately dirty data
- **Dimensional modelling:** designing a star schema with a fact table and three dimension tables
- **Feature engineering:** computing derived fields such as settlement ratio, days to settle and risk tiers
- **Databases:** creating and loading a SQLite database with SQLAlchemy
- **Analytical SQL:** JOINs, GROUP BY with aggregates, CASE WHEN, custom sorting and window functions (`ROW_NUMBER()`, running totals with `SUM() OVER`)
- **Data visualisation:** building an interactive HTML dashboard with Chart.js
- **Insight communication:** turning query results into business findings on exposure, claim volume and approval rates

