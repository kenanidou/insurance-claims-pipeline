"""
02_generate_data.py — Δημιουργία δεδομένων
Παράγει 200 φανταστικές ασφαλιστικές αξιώσεις και τις αποθηκεύει ως CSV.
"""

import pandas as pd
import numpy as np
import os, sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import RAW_CSV, NUM_RECORDS, RANDOM_SEED

rng = np.random.default_rng(RANDOM_SEED)

POLICY_TYPES   = ["AUTO", "HEALTH", "PROPERTY", "LIFE", "LIABILITY"]
POLICY_WEIGHTS = [0.35,   0.30,     0.20,       0.10,  0.05]

STATUSES       = ["APPROVED", "PENDING", "REJECTED", "UNDER_REVIEW"]
STATUS_WEIGHTS = [0.55,       0.20,      0.15,       0.10]

REGIONS = ["Αττική", "Θεσσαλονίκη", "Κρήτη", "Μακεδονία",
           "Θεσσαλία", "Ήπειρος", "Πελοπόννησος", "Δωδεκάνησα"]

AVG_AMOUNTS = {
    "AUTO":      8_000,
    "HEALTH":   15_000,
    "PROPERTY": 25_000,
    "LIFE":     80_000,
    "LIABILITY":12_000,
}

def random_dates(start_year, end_year, n):
    start      = datetime(start_year, 1, 1)
    end        = datetime(end_year, 12, 31)
    days_range = (end - start).days
    offsets    = rng.integers(0, days_range, size=n)
    return [start + timedelta(days=int(d)) for d in offsets]

def generate_data(n):
    print(f"Παράγω {n} εγγραφές...")

    claim_ids     = [f"CLM{str(i).zfill(4)}" for i in range(1, n + 1)]
    customer_pool = [f"CUST{str(i).zfill(4)}" for i in range(1, int(n * 0.6) + 1)]
    customer_ids  = rng.choice(customer_pool, size=n)
    policy_types  = rng.choice(POLICY_TYPES, p=POLICY_WEIGHTS, size=n)

    claim_amounts = np.array([
        max(100, rng.normal(AVG_AMOUNTS[pt], AVG_AMOUNTS[pt] * 0.4))
        for pt in policy_types
    ]).round(2)

    claim_dates      = random_dates(2022, 2024, n)
    settlement_dates = [d + timedelta(days=int(rng.integers(0, 181)))
                        for d in claim_dates]

    statuses = rng.choice(STATUSES, p=STATUS_WEIGHTS, size=n)

    settlement_amounts = np.where(
        statuses == "APPROVED",
        (claim_amounts * rng.uniform(0.5, 1.0, size=n)).round(2),
        np.nan
    )

    ages    = rng.integers(18, 85, size=n)
    regions = rng.choice(REGIONS, size=n)

    df = pd.DataFrame({
        "claim_id":          claim_ids,
        "customer_id":       customer_ids,
        "policy_type":       policy_types,
        "claim_date":        [d.strftime("%Y-%m-%d") for d in claim_dates],
        "settlement_date":   [d.strftime("%Y-%m-%d") for d in settlement_dates],
        "claim_amount":      claim_amounts,
        "settlement_amount": settlement_amounts,
        "status":            statuses,
        "customer_age":      ages,
        "region":            regions,
    })

    # Σκόπιμα λάθη
    df.loc[rng.random(n) < 0.03, "claim_amount"] = np.nan
    df.loc[rng.random(n) < 0.03, "region"]       = None
    neg_mask = rng.random(n) < 0.02
    df.loc[neg_mask, "claim_amount"] = -abs(df.loc[neg_mask, "claim_amount"])
    dup_idx = rng.choice(df.index, size=5, replace=False)
    df = pd.concat([df, df.iloc[dup_idx]], ignore_index=True)
    bad_mask = rng.random(len(df)) < 0.05
    df.loc[bad_mask, "status"] = df.loc[bad_mask, "status"].str.lower()

    print(f"  Σύνολο εγγραφών (με λάθη): {len(df)}")
    return df

if __name__ == "__main__":
    os.makedirs(os.path.dirname(RAW_CSV), exist_ok=True)
    df = generate_data(NUM_RECORDS)
    df.to_csv(RAW_CSV, index=False)
    print(f"\n✅ Αποθηκεύτηκε: {RAW_CSV}")
    print(df.head().to_string())
    print(df.isnull().sum())
    print(df["status"].value_counts())