"""
ingest_utils.py — Βοηθητικές συναρτήσεις ingestion
Χρησιμοποιείται από άλλα scripts για να φορτώνουν το CSV σωστά.
"""

import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUIRED_COLUMNS = [
    "claim_id", "customer_id", "policy_type",
    "claim_date", "settlement_date",
    "claim_amount", "settlement_amount",
    "status", "customer_age", "region"
]

DTYPE_MAP = {
    "claim_id":          "string",
    "customer_id":       "string",
    "policy_type":       "string",
    "claim_amount":      "float64",
    "settlement_amount": "float64",
    "status":            "string",
    "customer_age":      "Int64",
    "region":            "string",
}


def ingest(filepath):
    df = pd.read_csv(filepath)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Λείπουν στήλες: {missing}")

    df["claim_date"]      = pd.to_datetime(df["claim_date"],      errors="coerce")
    df["settlement_date"] = pd.to_datetime(df["settlement_date"], errors="coerce")

    for col, dtype in DTYPE_MAP.items():
        df[col] = df[col].astype(dtype)

    return df