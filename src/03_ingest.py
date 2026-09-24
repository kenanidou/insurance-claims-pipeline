"""
03_ingest.py — Ingestion Layer
Διαβάζει το raw CSV, ελέγχει το schema και κάνει type casting.
ΔΕΝ αλλάζει τίποτα στα δεδομένα — μόνο φορτώνει και ελέγχει.
"""

import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import RAW_CSV

# ── Ποιες στήλες περιμένουμε και τι τύπο πρέπει να έχουν ──────────
REQUIRED_COLUMNS = [
    "claim_id", "customer_id", "policy_type",
    "claim_date", "settlement_date",
    "claim_amount", "settlement_amount",
    "status", "customer_age", "region"
]

# Χάρτης: στήλη → τύπος δεδομένων
DTYPE_MAP = {
    "claim_id":          "string",
    "customer_id":       "string",
    "policy_type":       "string",
    "claim_amount":      "float64",
    "settlement_amount": "float64",
    "status":            "string",
    "customer_age":      "Int64",   # κεφαλαίο I = δέχεται NaN
    "region":            "string",
}


def ingest(filepath):
    print(f"📂 Φορτώνω: {filepath}")

    # ── 1. Φόρτωση CSV ─────────────────────────────────────────────
    df = pd.read_csv(filepath)
    print(f"   Γραμμές: {len(df)} | Στήλες: {len(df.columns)}")

    # ── 2. Έλεγχος ότι υπάρχουν όλες οι απαραίτητες στήλες ────────
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"❌ Λείπουν στήλες: {missing}")
    print(f"   ✅ Όλες οι {len(REQUIRED_COLUMNS)} στήλες υπάρχουν")

    # ── 3. Type casting ────────────────────────────────────────────
    # Ημερομηνίες: string → datetime (λάθος format → NaT αντί για crash)
    df["claim_date"]      = pd.to_datetime(df["claim_date"],      errors="coerce")
    df["settlement_date"] = pd.to_datetime(df["settlement_date"], errors="coerce")

    # Αριθμοί και strings
    for col, dtype in DTYPE_MAP.items():
        df[col] = df[col].astype(dtype)

    print(f"   ✅ Type casting ολοκληρώθηκε")

    # ── 4. Αναφορά nulls ───────────────────────────────────────────
    print("\n--- Nulls ανά στήλη ---")
    null_counts = df.isnull().sum()
    null_pct    = (null_counts / len(df) * 100).round(1)
    for col in df.columns:
        if null_counts[col] > 0:
            print(f"   {col}: {null_counts[col]} nulls ({null_pct[col]}%)")

    # ── 5. Τύποι δεδομένων μετά το casting ────────────────────────
    print("\n--- Τύποι στηλών ---")
    print(df.dtypes.to_string())

    return df


if __name__ == "__main__":
    df = ingest(RAW_CSV)

    print(f"\n--- Πρώτες 3 γραμμές ---")
    print(df.head(3).to_string())
    print(f"\n✅ Ingestion ολοκληρώθηκε — {len(df)} εγγραφές έτοιμες για cleaning")