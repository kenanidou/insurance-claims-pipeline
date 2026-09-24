"""
05_load_db.py — Load στη βάση δεδομένων (SQLite)
Δημιουργεί star schema και φορτώνει τα καθαρά δεδομένα.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import CLEAN_CSV, BASE_DIR

# Το αρχείο της βάσης θα δημιουργηθεί εδώ
DB_PATH = os.path.join(BASE_DIR, "data", "insurance.db")
engine  = create_engine(f"sqlite:///{DB_PATH}")


def create_tables():
    """Δημιουργεί τους πίνακες του star schema."""
    with engine.begin() as conn:

        # ── Dimension Tables ───────────────────────────────────────

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_policy_types (
                policy_type_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_type     TEXT UNIQUE NOT NULL
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_regions (
                region_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                region      TEXT UNIQUE NOT NULL
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_customers (
                customer_id     TEXT PRIMARY KEY,
                customer_age    INTEGER
            )
        """))

        # ── Fact Table ─────────────────────────────────────────────
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_claims (
                claim_sk            INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id            TEXT UNIQUE NOT NULL,
                customer_id         TEXT,
                policy_type_id      INTEGER,
                region_id           INTEGER,
                claim_date          TEXT,
                settlement_date     TEXT,
                claim_amount        REAL,
                settlement_amount   REAL,
                settlement_ratio    REAL,    -- settlement / claim
                days_to_settle      INTEGER, -- μέρες μέχρι εκκαθάριση
                status              TEXT,
                risk_tier           TEXT,    -- LOW / MEDIUM / HIGH / CRITICAL
                FOREIGN KEY (customer_id)    REFERENCES dim_customers(customer_id),
                FOREIGN KEY (policy_type_id) REFERENCES dim_policy_types(policy_type_id),
                FOREIGN KEY (region_id)      REFERENCES dim_regions(region_id)
            )
        """))

    print("✅ Πίνακες δημιουργήθηκαν")


def load_data():
    """Φορτώνει τα δεδομένα από το clean CSV στη βάση."""
    df = pd.read_csv(CLEAN_CSV, parse_dates=["claim_date", "settlement_date"])
    print(f"📂 Φόρτωσα {len(df)} εγγραφές από το clean CSV")

    with engine.begin() as conn:

        # ── 1. dim_policy_types ────────────────────────────────────
        policy_types = pd.DataFrame({"policy_type": df["policy_type"].unique()})
        policy_types.to_sql("dim_policy_types", conn, if_exists="append",
                            index=False)

        # Φέρνουμε τα IDs που έδωσε η βάση
        pt_map = pd.read_sql("SELECT * FROM dim_policy_types", conn)
        pt_map = dict(zip(pt_map["policy_type"], pt_map["policy_type_id"]))

        # ── 2. dim_regions ─────────────────────────────────────────
        regions = pd.DataFrame({"region": df["region"].unique()})
        regions.to_sql("dim_regions", conn, if_exists="append", index=False)

        r_map = pd.read_sql("SELECT * FROM dim_regions", conn)
        r_map = dict(zip(r_map["region"], r_map["region_id"]))

        # ── 3. dim_customers ───────────────────────────────────────
        customers = (df.groupby("customer_id")["customer_age"]
                       .last()
                       .reset_index())
        customers.to_sql("dim_customers", conn, if_exists="append", index=False)

        # ── 4. fact_claims — με υπολογισμένα πεδία ─────────────────
        fact = df.copy()

        # Foreign keys
        fact["policy_type_id"] = fact["policy_type"].map(pt_map)
        fact["region_id"]      = fact["region"].map(r_map)

        # Υπολογισμένα πεδία
        fact["settlement_ratio"] = (
            fact["settlement_amount"] / fact["claim_amount"]
        ).round(4)

        fact["days_to_settle"] = (
            fact["settlement_date"] - fact["claim_date"]
        ).dt.days

        # Risk tier βάση ποσού
        def risk_tier(amount):
            if   amount < 5_000:   return "LOW"
            elif amount < 50_000:  return "MEDIUM"
            elif amount < 200_000: return "HIGH"
            else:                  return "CRITICAL"

        fact["risk_tier"] = fact["claim_amount"].apply(risk_tier)

        # Επιλέγουμε μόνο τις στήλες που χρειάζεται το fact table
        fact_cols = ["claim_id", "customer_id", "policy_type_id", "region_id",
                     "claim_date", "settlement_date", "claim_amount",
                     "settlement_amount", "settlement_ratio", "days_to_settle",
                     "status", "risk_tier"]

        fact[fact_cols].to_sql("fact_claims", conn, if_exists="append", index=False)

    print("✅ Δεδομένα φορτώθηκαν στη βάση")


def show_summary():
    """Εκτυπώνει σύνοψη από τη βάση."""
    with engine.connect() as conn:
        print("\n--- Εγγραφές ανά πίνακα ---")
        for table in ["dim_policy_types", "dim_regions", "dim_customers", "fact_claims"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   {table}: {count}")

        print("\n--- Μέσο ποσό αξίωσης ανά τύπο ασφαλιστηρίου ---")
        result = conn.execute(text("""
            SELECT pt.policy_type,
                   COUNT(*)                        AS claims,
                   ROUND(AVG(f.claim_amount), 0)   AS avg_amount
            FROM   fact_claims f
            JOIN   dim_policy_types pt ON f.policy_type_id = pt.policy_type_id
            GROUP  BY pt.policy_type
            ORDER  BY avg_amount DESC
        """))
        for row in result:
            print(f"   {row[0]:<12} | {row[1]} αξιώσεις | μέσο: €{row[2]:,.0f}")


if __name__ == "__main__":
    create_tables()
    load_data()
    show_summary()
    print(f"\n✅ Βάση αποθηκεύτηκε: {DB_PATH}")