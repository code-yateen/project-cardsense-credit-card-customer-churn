"""Clean a copy of the source CSV; never overwrite the raw file."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "BankChurners.csv"
OUT = ROOT / "data" / "processed" / "cleaned_customers.csv"
if not RAW.exists():
    raise SystemExit(f"Dataset missing: {RAW}. Download from the Kaggle URL in data/README.md.")
df_clean = pd.read_csv(RAW)
classifier_cols = [c for c in df_clean.columns if c.startswith("Naive_Bayes_Classifier")]
df_clean = df_clean.drop(columns=classifier_cols)
before = len(df_clean)
df_clean = df_clean.drop_duplicates().copy()
OUT.parent.mkdir(parents=True, exist_ok=True)
df_clean.to_csv(OUT, index=False)
print(f"Removed classifier columns: {classifier_cols}")
print(f"Removed exact duplicate rows: {before - len(df_clean)}")
print(f"Missing values remaining: {int(df_clean.isna().sum().sum())}")
if "CLIENTNUM" in df_clean:
    print(f"Duplicate CLIENTNUM remaining: {int(df_clean.CLIENTNUM.duplicated().sum())}")
print(f"Saved cleaned copy: {OUT}")
