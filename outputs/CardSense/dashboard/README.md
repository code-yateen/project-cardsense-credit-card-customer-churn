# CardSense Power BI dashboard blueprint

The prepared source is `../data/processed/cleaned_customers.csv`. Power BI Desktop was not found in this environment, so no `.pbix` file has been created. The DAX measures and report plan below are ready for the Desktop build.

## Load and model the data

1. In Power BI Desktop, choose **Get data → Text/CSV** and load `data/processed/cleaned_customers.csv`.
2. Name the imported table `Customers`. Confirm `CLIENTNUM` is whole number, `Customer_Age`, counts, months, and transaction amounts are whole number where appropriate; set limits and ratios to decimal number.
3. Keep one row per `CLIENTNUM`. The cleaned extract has one row per customer. Hide `CLIENTNUM` from report view; it is a technical identifier, not a customer-facing dimension.
4. Add the calculated columns and measures from [`measures.dax`](measures.dax). Format churn rate and attrition share as percentage. Format transaction amount and credit limit as numbers, not currency: the file contains no currency code or bank revenue field.

For the model validation page, separately import `reports/model_test_predictions.csv` as `ModelEvaluation`. Keep it disconnected from `Customers` and hide its `CLIENTNUM` and `Threshold` columns from report view. This export contains only the model's untouched test split, not scores for the complete customer base.

There is no date field or transaction-level fact table in the source, so do not present these quarterly comparisons as a trend over time. `Total_Trans_Amt` is customer transaction amount, not bank revenue.

## Suggested report pages

### 1. Portfolio overview

- KPI cards: total customers, attrited customers, churn rate, existing customers, average transaction count.
- 100% stacked bar: Existing vs. Attrited by `Card_Category`.
- Column chart: customer count by `Age Band`, split by `Attrition_Flag`.
- Slicers: `Card_Category`, `Education_Level`, `Marital_Status`, `Income_Category`.

### 2. Engagement and usage

- Clustered columns: average transaction count by attrition status.
- Bar chart: churn rate by `Months_Inactive_12_mon`.
- Column chart: churn rate by `Utilization Band`.
- Scatter: `Total_Trans_Ct` vs `Total_Trans_Amt`, color by `Attrition_Flag` (aggregate carefully; each point is a customer only if the visual uses `CLIENTNUM` as detail).

### 3. Customer segments

- Matrix: `Card_Category` × `Income_Category`, with customer count and churn rate.
- Bar chart: churn rate by `Education_Level` and `Marital_Status`.
- Include segment size alongside every churn rate to make small groups visible.

### 4. Model validation (test split only)

- KPI cards: `Test Precision`, `Test Recall`, and `Test F1` from `measures.dax`.
- Matrix: actual attrition on rows, predicted attrition on columns, and count of `ModelEvaluation` rows as values.
- Use `Attrited_Probability` in a histogram or distribution chart only as a test-set diagnostic.
- Label the page clearly as holdout evaluation. Do not show these test predictions as current customer risk scores.

## Interpretation notes

- `Attrition_Flag` is a historical status. The charts describe this dataset; they do not estimate future churn.
- The dataset includes `Unknown` categories in several profile columns. Keep them visible or label them as unknown; do not treat them as a known demographic category.
- A higher association with attrition does not show that a feature caused attrition.
- If using the model evaluation, present its held-out metrics separately from customer-level business KPIs. Do not use in-sample scores as current customer risk.
- `model_test_predictions.csv` contains customer identifiers and model test predictions; treat it as sensitive analytical data and keep it out of source control.
