-- CardSense PostgreSQL foundation. Run this before loading customers.
CREATE SCHEMA IF NOT EXISTS cardsense;

CREATE TABLE IF NOT EXISTS cardsense.customers (
    clientnum BIGINT PRIMARY KEY,
    attrition_flag TEXT NOT NULL CHECK (attrition_flag IN ('Existing Customer', 'Attrited Customer')),
    customer_age SMALLINT NOT NULL CHECK (customer_age BETWEEN 18 AND 120),
    gender TEXT NOT NULL,
    dependent_count SMALLINT NOT NULL CHECK (dependent_count >= 0),
    education_level TEXT NOT NULL,
    marital_status TEXT NOT NULL,
    income_category TEXT NOT NULL,
    card_category TEXT NOT NULL,
    months_on_book SMALLINT NOT NULL CHECK (months_on_book > 0),
    total_relationship_count SMALLINT NOT NULL CHECK (total_relationship_count >= 0),
    months_inactive_12_mon SMALLINT NOT NULL CHECK (months_inactive_12_mon >= 0),
    contacts_count_12_mon SMALLINT NOT NULL CHECK (contacts_count_12_mon >= 0),
    credit_limit NUMERIC(12, 2) NOT NULL CHECK (credit_limit >= 0),
    total_revolving_bal NUMERIC(12, 2) NOT NULL CHECK (total_revolving_bal >= 0),
    avg_open_to_buy NUMERIC(12, 2) NOT NULL CHECK (avg_open_to_buy >= 0),
    total_amt_chng_q4_q1 NUMERIC(12, 6) NOT NULL CHECK (total_amt_chng_q4_q1 >= 0),
    total_trans_amt NUMERIC(14, 2) NOT NULL CHECK (total_trans_amt >= 0),
    total_trans_ct INTEGER NOT NULL CHECK (total_trans_ct >= 0),
    total_ct_chng_q4_q1 NUMERIC(12, 6) NOT NULL CHECK (total_ct_chng_q4_q1 >= 0),
    avg_utilization_ratio NUMERIC(8, 6) NOT NULL CHECK (avg_utilization_ratio BETWEEN 0 AND 1),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_customers_attrition
    ON cardsense.customers (attrition_flag);
CREATE INDEX IF NOT EXISTS idx_customers_card_category
    ON cardsense.customers (card_category);
