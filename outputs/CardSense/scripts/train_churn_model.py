"""Train and compare simple churn-classification baselines."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "cleaned_customers.csv"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
TARGET = "Attrition_Flag"
POSITIVE_LABEL = "Attrited Customer"


def make_preprocessor(numeric_columns: list[str], categorical_columns: list[str]) -> ColumnTransformer:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric, numeric_columns),
        ("categorical", categorical, categorical_columns),
    ])


def run_training() -> tuple[pd.DataFrame, dict]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}. Run scripts/clean_data.py first.")

    df = pd.read_csv(DATA_PATH)
    if TARGET not in df:
        raise KeyError(f"Target column {TARGET!r} is missing from {DATA_PATH}.")

    y = (df[TARGET] == POSITIVE_LABEL).astype("int8")
    excluded = {TARGET, "CLIENTNUM"}
    excluded.update(c for c in df.columns if c.startswith("Naive_Bayes_Classifier"))
    X = df.drop(columns=[c for c in excluded if c in df.columns])
    if X.empty:
        raise ValueError("No candidate features remain after excluding target, identifier, and classifier outputs.")

    numeric_columns = X.select_dtypes(include=np.number).columns.tolist()
    categorical_columns = [c for c in X.columns if c not in numeric_columns]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    X_fit, X_validation, y_fit, y_validation = train_test_split(
        X_train, y_train, test_size=0.20, random_state=43, stratify=y_train
    )

    candidates = {
        "logistic_regression": LogisticRegression(
            class_weight="balanced", max_iter=2000, solver="liblinear", random_state=42
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=250, min_samples_leaf=3, class_weight="balanced_subsample",
            n_jobs=-1, random_state=42,
        ),
    }

    fitted = {}
    results = []
    for name, estimator in candidates.items():
        pipeline = Pipeline([
            ("preprocessor", make_preprocessor(numeric_columns, categorical_columns)),
            ("classifier", estimator),
        ])
        pipeline.fit(X_fit, y_fit)
        probabilities = pipeline.predict_proba(X_validation)[:, 1]
        results.append({
            "model": name,
            "validation_average_precision": float(average_precision_score(y_validation, probabilities)),
            "validation_roc_auc": float(roc_auc_score(y_validation, probabilities)),
        })
        fitted[name] = pipeline

    results.sort(key=lambda row: row["validation_average_precision"], reverse=True)
    selected = results[0]["model"]
    selected_pipeline = fitted[selected]
    selected_pipeline.fit(X_train, y_train)
    test_probabilities = selected_pipeline.predict_proba(X_test)[:, 1]
    test_predictions = (test_probabilities >= 0.5).astype("int8")
    test_output = pd.DataFrame({
        "CLIENTNUM": df.loc[X_test.index, "CLIENTNUM"].to_numpy(),
        "Actual_Attrition": np.where(y_test.to_numpy() == 1, POSITIVE_LABEL, "Existing Customer"),
        "Predicted_Attrition": np.where(test_predictions == 1, POSITIVE_LABEL, "Existing Customer"),
        "Attrited_Probability": test_probabilities,
        "Threshold": 0.50,
    })
    test_metrics = {
        "average_precision": float(average_precision_score(y_test, test_probabilities)),
        "roc_auc": float(roc_auc_score(y_test, test_probabilities)),
        "precision_at_0_5": float(precision_score(y_test, test_predictions, zero_division=0)),
        "recall_at_0_5": float(recall_score(y_test, test_predictions, zero_division=0)),
        "f1_at_0_5": float(f1_score(y_test, test_predictions, zero_division=0)),
        "confusion_matrix_tn_fp_fn_tp": confusion_matrix(y_test, test_predictions, labels=[0, 1]).ravel().tolist(),
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_pipeline, MODEL_DIR / "churn_pipeline.joblib")

    summary = {
        "target": TARGET,
        "positive_class": POSITIVE_LABEL,
        "selection_metric": "validation_average_precision",
        "selected_model": selected,
        "random_state": 42,
        "test_size": 0.20,
        "train_rows": int(len(X_train)),
        "fit_rows_per_candidate": int(len(X_fit)),
        "validation_rows": int(len(X_validation)),
        "test_rows": int(len(X_test)),
        "train_attrited": int(y_train.sum()),
        "validation_attrited": int(y_validation.sum()),
        "test_attrited": int(y_test.sum()),
        "excluded_features": sorted(excluded),
        "candidate_features": X.columns.tolist(),
        "validation_results": results,
        "test_metrics_selected_model": test_metrics,
        "threshold_note": "Precision, recall, F1, and confusion matrix use a default 0.50 threshold; choose a business threshold separately.",
        "scope_note": "This is a baseline on stratified random splits of a historical labeled dataset, not a deployment-ready or causal model. The test split is held out from model selection.",
    }
    (REPORT_DIR / "model_evaluation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    test_output.to_csv(REPORT_DIR / "model_test_predictions.csv", index=False)
    return pd.DataFrame(results), summary


def main() -> int:
    results, summary = run_training()
    print("Validation comparison:")
    print(results.to_string(index=False))
    print("Selected model test metrics:", summary["test_metrics_selected_model"])
    print(f"Selected by validation average precision: {summary['selected_model']}")
    print(f"Saved pipeline: {MODEL_DIR / 'churn_pipeline.joblib'}")
    print(f"Saved metrics: {REPORT_DIR / 'model_evaluation.json'}")
    print(f"Saved held-out predictions: {REPORT_DIR / 'model_test_predictions.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
