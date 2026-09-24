-- ============================================================
-- queries.sql — Αναλυτικά SQL Queries
-- Τρέξε τα ένα-ένα για να δεις τα αποτελέσματα
-- ============================================================


-- ── Query 1: Βασικό GROUP BY ──────────────────────────────────
-- Πόσες αξιώσεις και ποιο μέσο ποσό ανά τύπο ασφαλιστηρίου;
-- Concepts: JOIN, GROUP BY, COUNT, AVG, ORDER BY

SELECT
    pt.policy_type,
    COUNT(*)                          AS total_claims,
    ROUND(AVG(f.claim_amount), 0)     AS avg_claim,
    ROUND(SUM(f.claim_amount), 0)     AS total_exposure
FROM   fact_claims f
JOIN   dim_policy_types pt ON f.policy_type_id = pt.policy_type_id
GROUP  BY pt.policy_type
ORDER  BY total_exposure DESC;


-- ── Query 2: Ανάλυση Status ───────────────────────────────────
-- Ποσοστό εγκρίσεων ανά τύπο ασφαλιστηρίου
-- Concepts: CASE WHEN, διαίρεση για ποσοστά

SELECT
    pt.policy_type,
    COUNT(*)                                              AS total,
    SUM(CASE WHEN f.status = 'APPROVED' THEN 1 ELSE 0 END) AS approved,
    ROUND(
        100.0 * SUM(CASE WHEN f.status = 'APPROVED' THEN 1 ELSE 0 END)
        / COUNT(*), 1
    )                                                     AS approval_rate_pct
FROM   fact_claims f
JOIN   dim_policy_types pt ON f.policy_type_id = pt.policy_type_id
GROUP  BY pt.policy_type
ORDER  BY approval_rate_pct DESC;


-- ── Query 3: Risk Tier ─────────────────────────────────────────
-- Κατανομή αξιώσεων ανά επίπεδο κινδύνου
-- Concepts: GROUP BY σε υπολογισμένη στήλη, CASE WHEN (ήδη στο fact)

SELECT
    risk_tier,
    COUNT(*)                       AS claims,
    ROUND(AVG(claim_amount), 0)    AS avg_amount,
    ROUND(AVG(settlement_ratio) * 100, 1) AS avg_settlement_pct
FROM   fact_claims
WHERE  settlement_ratio IS NOT NULL
GROUP  BY risk_tier
ORDER  BY CASE risk_tier
    WHEN 'LOW'      THEN 1
    WHEN 'MEDIUM'   THEN 2
    WHEN 'HIGH'     THEN 3
    WHEN 'CRITICAL' THEN 4
END;


-- ── Query 4: Window Function — Ranking ────────────────────────
-- Top 10 μεγαλύτερες αξιώσεις με ranking
-- Concepts: ROW_NUMBER() OVER (ORDER BY ...)

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
LIMIT  10;


-- ── Query 5: Window Function — Running Total ──────────────────
-- Αθροιστικό σύνολο αξιώσεων ανά μήνα (2022-2024)
-- Concepts: strftime για ημερομηνίες, SUM() OVER (ORDER BY ...)

SELECT
    strftime('%Y-%m', claim_date)          AS month,
    COUNT(*)                               AS monthly_claims,
    ROUND(SUM(claim_amount), 0)            AS monthly_amount,
    ROUND(SUM(SUM(claim_amount)) OVER (
        ORDER BY strftime('%Y-%m', claim_date)
    ), 0)                                  AS cumulative_amount
FROM   fact_claims
GROUP  BY strftime('%Y-%m', claim_date)
ORDER  BY month;