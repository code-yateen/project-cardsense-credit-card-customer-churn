# CardSense churn baseline: evaluation

## Setup

- Target: `Attrition_Flag`; the positive class is `Attrited Customer`.
- Features exclude `CLIENTNUM` and all `Naive_Bayes_Classifier*` columns.
- Data split is stratified: 64% fit, 16% validation, 20% final test (seed 42/43).
- Candidates: class-weighted logistic regression and class-weighted random forest.
- Model selection uses validation average precision. The selected model is refit on the full 80% training partition and scored once on the untouched test partition.

## Validation comparison

| Model | Average precision | ROC AUC |
|---|---:|---:|
| Random forest | 0.939 | 0.985 |
| Logistic regression | 0.767 | 0.932 |

Random forest was selected using validation average precision.

## Selected model: held-out test results

| Metric | Result |
|---|---:|
| Average precision | 0.932 |
| ROC AUC | 0.984 |
| Precision at 0.50 | 0.855 |
| Recall at 0.50 | 0.818 |
| F1 at 0.50 | 0.836 |

At a 0.50 threshold, the confusion matrix is **TN 1,656; FP 45; FN 59; TP 266**. Of 325 attrited customers in the test split, the model identified 266; the threshold also flagged 45 of 1,701 existing customers.

## Interpretation and limits

This is a promising baseline on a random split of one historical dataset. It does not establish that the model will generalize to future customers, and the test metrics may not reflect real-world retention costs or capacity. The dataset has no event dates for a time-based validation split. Before operational use, assess calibration, select a threshold against intervention costs and contact capacity, review feature policy/fairness, and validate on a later time period. Do not interpret feature association as causation.

The selected pipeline is in `models/churn_pipeline.joblib`. Machine-readable split details and metrics are in `reports/model_evaluation.json`. `reports/model_test_predictions.csv` contains row-level predictions for the held-out test set only and can feed the dashboard's model validation page; it is ignored by Git because it contains customer identifiers.
