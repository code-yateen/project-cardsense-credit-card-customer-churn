# CardSense – Credit Card Customer Churn & Revenue Optimization

Phase 1 (data understanding and cleaning) is complete. PostgreSQL and churn-modeling assets are prepared in `sql/`, `scripts/`, and `notebooks/`; the Power BI dashboard blueprint is in `dashboard/`.

## Dataset

The source CSV is at `data/raw/BankChurners.csv`. If setting up a fresh copy of the project, download it from [Kaggle](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers), extract the archive, and place the file there. See [data/README.md](data/README.md).

## Windows setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter notebook
```

If activation is blocked, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that PowerShell session, then activate. Run notebooks with working directory `notebooks/`; run scripts from the project root.

Cleaning removes the two `Naive_Bayes_Classifier*` outputs and exact duplicate rows, keeps `CLIENTNUM` for traceability, and reports missingness without silent imputation. The raw file is never overwritten.

## Project contents

- `notebooks/01_data_understanding.ipynb`: inspection, attrition mix, and data-quality checks.
- `notebooks/02_data_cleaning.ipynb`: cleaning and separate processed CSV export.
- `scripts/inspect_data.py` and `scripts/clean_data.py`: command-line workflows.
- `sql/01_create_schema.sql` and `sql/02_business_analysis.sql`: PostgreSQL schema and descriptive analysis queries.
- `scripts/load_to_postgres.py`: loads the cleaned CSV into PostgreSQL using `CARDSENSE_DATABASE_URL`.
- `scripts/run_postgres_phase.ps1`: initializes the project-local PostgreSQL runtime, loads the data, and runs the SQL analyses.
- `notebooks/03_churn_modeling.ipynb` and `scripts/train_churn_model.py`: compare baseline churn classifiers and save the selected pipeline.
- `dashboard/README.md` and `dashboard/measures.dax`: Power BI data model, measures, report-page plan, and interpretation guidance.
- `reports/phase1_data_quality_summary.md`: observed dataset profile and quality results.
- `reports/model_evaluation.md`: validation comparison and held-out test metrics for the churn baseline; the generated test prediction export can feed the model validation report page.

The PostgreSQL 18.6 runtime is downloaded into the Git-ignored `.pg_runtime/` folder. Its database cluster has not been initialized, so the schema and queries are prepared but not executed. See [sql/README.md](sql/README.md) for database setup. The churn baseline is implemented against the cleaned CSV. Power BI Desktop is not available here, so the dashboard blueprint is ready but no `.pbix` has been created.
