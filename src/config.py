"""
config.py — Κεντρικές ρυθμίσεις του pipeline
Αλλάζεις εδώ → αλλάζει παντού αυτόματα
"""

import os

# Βρίσκουμε αυτόματα το root directory του project
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths για τα αρχεία δεδομένων
RAW_CSV   = os.path.join(BASE_DIR, "data", "raw",       "claims.csv")
CLEAN_CSV = os.path.join(BASE_DIR, "data", "processed", "claims_clean.csv")

# Παράμετροι δεδομένων
NUM_RECORDS  = 200   # πόσες εγγραφές να παράγουμε
RANDOM_SEED  = 42    # για αναπαραγώγιμα αποτελέσματα

# Business rules — χρησιμοποιούνται στο validation
MIN_CLAIM = 100      # ελάχιστο ποσό αξίωσης σε €
MAX_CLAIM = 500_000  # μέγιστο ποσό αξίωσης σε €
MIN_AGE   = 18       # ελάχιστη ηλικία πελάτη
MAX_AGE   = 100      # μέγιστη ηλικία πελάτη

# PostgreSQL — θα το χρησιμοποιήσουμε στο Βήμα 5
DB_CONFIG = {
    "host":     os.getenv("PG_HOST", "localhost"),
    "port":     5432,
    "dbname":   "insurance_db",
    "user":     os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASS", "postgres"),
}