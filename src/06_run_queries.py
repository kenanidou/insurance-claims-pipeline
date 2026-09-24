"""
06_run_queries.py — Εκτέλεση SQL Queries
Τρέχει και τα 5 queries και εκτυπώνει τα αποτελέσματα.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "data", "insurance.db")
engine  = create_engine(f"sqlite:///{DB_PATH}")

QUERIES = {

    "Q1 — Έκθεση ανά τύπο ασφαλιστηρίου": """
        SELECT
            pt.policy_type,
            COUNT(*)                          AS total_claims,
            ROUND(AVG(f.claim_amount), 0)     AS avg_claim,
            ROUND(SUM(f.claim_amount), 0)     AS total_exposure
        FROM   fact_claims f
        JOIN   dim_policy_types pt ON f.policy_type_id = pt.policy_type_id
        GROUP  BY pt.policy_type
        ORDER  BY total_exposure DESC
    """,

    "Q2 — Ποσοστό έγκρισης ανά τύπο": """
        SELECT
            pt.policy_type,
            COUNT(*)                                               AS total,
            SUM(CASE WHEN f.status = 'APPROVED' THEN 1 ELSE 0 END) AS approved,
            ROUND(
                100.0 * SUM(CASE WHEN f.status = 'APPROVED' THEN 1 ELSE 0 END)
                / COUNT(*), 1
            )                                                      AS approval_rate_pct
        FROM   fact_claims f
        JOIN   dim_policy_types pt ON f.policy_type_id = pt.policy_type_id
        GROUP  BY pt.policy_type
        ORDER  BY approval_rate_pct DESC
    """,

    "Q3 — Ανάλυση Risk Tier": """
        SELECT
            risk_tier,
            COUNT(*)                              AS claims,
            ROUND(AVG(claim_amount), 0)           AS avg_amount,
            ROUND(AVG(settlement_ratio) * 100, 1) AS avg_settlement_pct
        FROM   fact_claims
        WHERE  settlement_ratio IS NOT NULL
        GROUP  BY risk_tier
        ORDER  BY CASE risk_tier
            WHEN 'LOW'      THEN 1
            WHEN 'MEDIUM'   THEN 2
            WHEN 'HIGH'     THEN 3
            WHEN 'CRITICAL' THEN 4
        END
    """,

    "Q4 — Top 10 μεγαλύτερες αξιώσεις": """
        SELECT
            ROW_NUMBER() OVER (ORDER BY claim_amount DESC) AS rank,
            claim_id,
            pt.policy_type,
            r.region,
            claim_amount,
            status
        FROM   fact_claims f
        JOIN   dim_policy_types pt ON f.policy_type_id = pt.policy_type_id
        JOIN   dim_regions r       ON f.region_id      = r.region_id
        ORDER  BY claim_amount DESC
        LIMIT  10
    """,

    "Q5 — Μηνιαίο Running Total": """
        SELECT
            strftime('%Y-%m', claim_date)        AS month,
            COUNT(*)                             AS monthly_claims,
            ROUND(SUM(claim_amount), 0)          AS monthly_amount,
            ROUND(SUM(SUM(claim_amount)) OVER (
                ORDER BY strftime('%Y-%m', claim_date)
            ), 0)                                AS cumulative_amount
        FROM   fact_claims
        GROUP  BY strftime('%Y-%m', claim_date)
        ORDER  BY month
    """,
}


if __name__ == "__main__":
    with engine.connect() as conn:
        for title, sql in QUERIES.items():
            print(f"\n{'='*55}")
            print(f"  {title}")
            print(f"{'='*55}")
            df = pd.read_sql(text(sql), conn)
            print(df.to_string(index=False))