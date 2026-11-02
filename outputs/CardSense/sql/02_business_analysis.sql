-- 1) Portfolio churn and retention baseline
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE attrition_flag = 'Attrited Customer') AS attrited_customers,
    COUNT(*) FILTER (WHERE attrition_flag = 'Existing Customer') AS existing_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE attrition_flag = 'Attrited Customer') / NULLIF(COUNT(*), 0), 2) AS churn_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE attrition_flag = 'Existing Customer') / NULLIF(COUNT(*), 0), 2) AS retention_pct
FROM cardsense.customers;

-- 2) Churn rate by product and customer tenure band
SELECT
    card_category,
    CASE WHEN months_on_book < 24 THEN 'Under 2 years'
         WHEN months_on_book < 48 THEN '2–3 years'
         ELSE '4+ years' END AS tenure_band,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE attrition_flag = 'Attrited Customer') / NULLIF(COUNT(*), 0), 2) AS churn_pct
FROM cardsense.customers
GROUP BY card_category, tenure_band
ORDER BY card_category, tenure_band;

-- 3) Inactivity and contact patterns by attrition outcome
SELECT
    attrition_flag,
    ROUND(AVG(months_inactive_12_mon), 2) AS avg_inactive_months,
    ROUND(AVG(contacts_count_12_mon), 2) AS avg_bank_contacts,
    COUNT(*) AS customers
FROM cardsense.customers
GROUP BY attrition_flag
ORDER BY attrition_flag;

-- 4) Transaction engagement by attrition outcome
SELECT
    attrition_flag,
    ROUND(AVG(total_trans_ct), 2) AS avg_transaction_count,
    ROUND(AVG(total_trans_amt), 2) AS avg_transaction_amount,
    ROUND(AVG(total_ct_chng_q4_q1), 3) AS avg_transaction_count_change,
    ROUND(AVG(total_amt_chng_q4_q1), 3) AS avg_transaction_amount_change,
    COUNT(*) AS customers
FROM cardsense.customers
GROUP BY attrition_flag
ORDER BY attrition_flag;

-- 5) Churn by utilization band
SELECT
    CASE WHEN avg_utilization_ratio < 0.10 THEN '0–9%'
         WHEN avg_utilization_ratio < 0.30 THEN '10–29%'
         WHEN avg_utilization_ratio < 0.60 THEN '30–59%'
         ELSE '60–100%' END AS utilization_band,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE attrition_flag = 'Attrited Customer') / NULLIF(COUNT(*), 0), 2) AS churn_pct
FROM cardsense.customers
GROUP BY utilization_band
ORDER BY MIN(avg_utilization_ratio);

-- 6) Churn by profile fields for descriptive segmentation
SELECT
    education_level,
    marital_status,
    income_category,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE attrition_flag = 'Attrited Customer') / NULLIF(COUNT(*), 0), 2) AS churn_pct
FROM cardsense.customers
GROUP BY education_level, marital_status, income_category
HAVING COUNT(*) >= 30
ORDER BY churn_pct DESC, customers DESC;
