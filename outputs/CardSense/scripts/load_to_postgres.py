"""Load the cleaned CardSense CSV into PostgreSQL, upserting by clientnum."""
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "processed" / "cleaned_customers.csv"
TABLE_COLUMNS = [
    "clientnum", "attrition_flag", "customer_age", "gender", "dependent_count",
    "education_level", "marital_status", "income_category", "card_category",
    "months_on_book", "total_relationship_count", "months_inactive_12_mon",
    "contacts_count_12_mon", "credit_limit", "total_revolving_bal", "avg_open_to_buy",
    "total_amt_chng_q4_q1", "total_trans_amt", "total_trans_ct",
    "total_ct_chng_q4_q1", "avg_utilization_ratio",
]


def main() -> int:
    database_url = os.getenv("CARDSENSE_DATABASE_URL")
    if not database_url:
        raise SystemExit("Set CARDSENSE_DATABASE_URL to a PostgreSQL SQLAlchemy URL before loading.")
    if not CLEAN.exists():
        raise SystemExit(f"Cleaned data not found: {CLEAN}. Run scripts/clean_data.py first.")

    df = pd.read_csv(CLEAN)
    df.columns = df.columns.str.lower()
    missing = sorted(set(TABLE_COLUMNS) - set(df.columns))
    if missing:
        raise SystemExit(f"Cleaned CSV is missing expected columns: {missing}")
    df = df[TABLE_COLUMNS]

    engine = create_engine(database_url)
    stage = f"customers_stage_{uuid4().hex[:12]}"
    insert_columns = ", ".join(TABLE_COLUMNS)
    updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in TABLE_COLUMNS if c != "clientnum")
    updates += ", loaded_at = NOW()"
    try:
        with engine.begin() as conn:
            df.to_sql(stage, conn, schema="cardsense", if_exists="fail", index=False)
            conn.execute(text(
                f"INSERT INTO cardsense.customers ({insert_columns}) "
                f"SELECT {insert_columns} FROM cardsense.{stage} "
                f"ON CONFLICT (clientnum) DO UPDATE SET {updates}"
            ))
            conn.execute(text(f"DROP TABLE cardsense.{stage}"))
        print(f"Loaded or updated {len(df):,} customers in cardsense.customers.")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
