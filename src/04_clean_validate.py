"""
04_clean_validate.py — Cleaning & Validation
Διορθώνει τα προβλήματα του raw CSV και αποθηκεύει καθαρό αρχείο.
"""

import pandas as pd
import numpy as np
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import RAW_CSV, CLEAN_CSV, MIN_CLAIM, MAX_CLAIM, MIN_AGE, MAX_AGE

# Φορτώνουμε το ingestion module που φτιάξαμε στο Βήμα 3
from src.ingest_utils import ingest


def clean(df):
    print("🧹 Ξεκινάω Cleaning...")
    original_len = len(df)

    # ── 1. Αφαίρεση Duplicates ─────────────────────────────────────
    df = df.drop_duplicates(subset=["claim_id"]).copy()
    print(f"   Duplicates αφαιρέθηκαν: {original_len - len(df)}")

    # ── 2. String normalization — uppercase + trim spaces ──────────
    # π.χ. "approved" → "APPROVED", "  AUTO  " → "AUTO"
    for col in ["status", "policy_type", "claim_id", "customer_id"]:
        df[col] = df[col].str.strip().str.upper()
    print(f"   ✅ String normalization (uppercase)")

    # ── 3. Αρνητικά ποσά → θετικά ─────────────────────────────────
    neg_count = (df["claim_amount"] < 0).sum()
    df["claim_amount"] = df["claim_amount"].abs()
    print(f"   Αρνητικά ποσά διορθώθηκαν: {neg_count}")

    # ── 4. Nulls σε claim_amount → διαγραφή γραμμής ───────────────
    # (δεν μπορούμε να ξέρουμε το σωστό ποσό — καλύτερα να φύγει)
    before = len(df)
    df = df.dropna(subset=["claim_amount"])
    print(f"   Γραμμές με null claim_amount αφαιρέθηκαν: {before - len(df)}")

    # ── 5. Nulls σε region → "UNKNOWN" ────────────────────────────
    # (ξέρουμε ότι υπάρχει αξίωση, απλώς δεν ξέρουμε περιφέρεια)
    region_nulls = df["region"].isna().sum()
    df["region"] = df["region"].fillna("UNKNOWN")
    print(f"   Null regions → 'UNKNOWN': {region_nulls}")

    print(f"\n   Εγγραφές: {original_len} → {len(df)} (αφαιρέθηκαν {original_len - len(df)})")
    return df


def validate(df):
    print("\n🔍 Ξεκινάω Validation...")
    warnings = []
    errors   = []

    # ── Κανόνας 1: claim_amount στα όρια ──────────────────────────
    low  = (df["claim_amount"] < MIN_CLAIM).sum()
    high = (df["claim_amount"] > MAX_CLAIM).sum()
    if low  > 0: warnings.append(f"claim_amount < €{MIN_CLAIM}: {low} εγγραφές")
    if high > 0: warnings.append(f"claim_amount > €{MAX_CLAIM}: {high} εγγραφές")

    # ── Κανόνας 2: customer_age στα όρια ──────────────────────────
    bad_age = ((df["customer_age"] < MIN_AGE) | (df["customer_age"] > MAX_AGE)).sum()
    if bad_age > 0: errors.append(f"customer_age εκτός {MIN_AGE}-{MAX_AGE}: {bad_age} εγγραφές")

    # ── Κανόνας 3: settlement_date >= claim_date ───────────────────
    bad_dates = (df["settlement_date"] < df["claim_date"]).sum()
    if bad_dates > 0: errors.append(f"settlement_date < claim_date: {bad_dates} εγγραφές")

    # ── Κανόνας 4: status whitelist ────────────────────────────────
    valid_statuses = {"APPROVED", "PENDING", "REJECTED", "UNDER_REVIEW"}
    bad_status = (~df["status"].isin(valid_statuses)).sum()
    if bad_status > 0: warnings.append(f"Άγνωστο status: {bad_status} εγγραφές")

    # ── Κανόνας 5: nulls < 5% ──────────────────────────────────────
    for col in df.columns:
        pct = df[col].isna().mean() * 100
        if pct >= 5 and col != "settlement_amount":  # settlement_amount εξαιρείται
            errors.append(f"{col}: {pct:.1f}% nulls (όριο 5%)")

    # ── Αναφορά ────────────────────────────────────────────────────
    if warnings:
        print("   ⚠️  Warnings:")
        for w in warnings: print(f"      - {w}")
    if errors:
        print("   ❌ Errors:")
        for e in errors: print(f"      - {e}")
    if not warnings and not errors:
        print("   ✅ Όλοι οι κανόνες πέρασαν!")

    return {"warnings": warnings, "errors": errors}


if __name__ == "__main__":
    # 1. Φόρτωση μέσω ingestion layer
    df = ingest(RAW_CSV)

    # 2. Cleaning
    df_clean = clean(df)

    # 3. Validation
    report = validate(df_clean)

    # 4. Αποθήκευση καθαρού CSV
    os.makedirs(os.path.dirname(CLEAN_CSV), exist_ok=True)
    df_clean.to_csv(CLEAN_CSV, index=False)

    print(f"\n✅ Καθαρό CSV αποθηκεύτηκε: {CLEAN_CSV}")
    print(f"\n--- Κατανομή status μετά cleaning ---")
    print(df_clean["status"].value_counts().to_string())