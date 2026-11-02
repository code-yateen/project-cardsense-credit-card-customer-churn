"""Inspect BankChurners.csv without modifying it."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "BankChurners.csv"

if not RAW.exists():
    raise SystemExit(f"Dataset missing: {RAW}. Download from the Kaggle URL in data/README.md.")
df = pd.read_csv(RAW)
pd.set_option("display.max_columns", None)
print("Shape:", df.shape)
print("\nHead:\n", df.head())
print("\nTail:\n", df.tail())
print("\nColumns:\n", df.columns.tolist())
df.info()
print("\nNumerical summary:\n", df.describe())
print("\nCategorical summary:\n", df.describe(include="object"))
if "Attrition_Flag" in df:
    print("\nAttrition counts:\n", df.Attrition_Flag.value_counts(dropna=False))
    print("Percent:\n", df.Attrition_Flag.value_counts(normalize=True, dropna=False).mul(100))
print("\nMissing by column:\n", df.isna().sum())
print("Total missing:", int(df.isna().sum().sum()))
print("Exact duplicate records:", int(df.duplicated().sum()))
if "CLIENTNUM" in df:
    print("Duplicate CLIENTNUM:", int(df.CLIENTNUM.duplicated().sum()))
