# CardSense Phase 1: data quality summary

Source: `data/raw/BankChurners.csv` (IBM Credit Card Customers Kaggle dataset).

## Dataset profile

- 10,127 rows and 23 columns in the source file.
- `Attrition_Flag`: 8,500 existing customers (83.93%) and 1,627 attrited customers (16.07%).
- 0 missing cells, 0 exact duplicate rows, and 0 duplicate `CLIENTNUM` values.
- After removing the two `Naive_Bayes_Classifier*` outputs, the cleaned file has 10,127 rows and 21 columns.

## Plausibility review

The checks in the data understanding notebook found no flagged rows for age outside 18–120, dependent count outside 0–10, nonpositive months on book, nonpositive credit limit, nonpositive transaction count, or utilization outside 0–1. Observed ranges include customer age 26–73, months on book 13–56, credit limit 1,438.30–34,516, transaction count 10–139, and utilization 0–0.999.

These rules are screening checks, not formal business validation. No imputations, clipping, or recoding were applied. The processed CSV is a separate file; the source CSV remains unchanged.

## Business interpretation

Attrition is a historical label in this dataset, not a prediction. The attrited share is about one in six records, so future classification work should account for the class imbalance and evaluate more than accuracy. The classifier output columns in the source were removed to prevent target leakage. `CLIENTNUM` remains for traceability and should be excluded from any future model features.
