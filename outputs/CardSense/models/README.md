# Churn baseline

The training script compares logistic regression and random forest using stratified train, validation, and test splits. It drops `CLIENTNUM` and any `Naive_Bayes_Classifier*` columns, uses preprocessing pipelines for numeric and categorical features, selects by validation average precision, refits the winner on the training split, and evaluates it once on the untouched test split. Threshold-based metrics use 0.50 for reporting only.

Run `python scripts/train_churn_model.py` from the project root. The selected pipeline is saved as `models/churn_pipeline.joblib`; metrics and split metadata are saved as `reports/model_evaluation.json`; row-level predictions for the held-out test split are saved as `reports/model_test_predictions.csv`. These generated files are excluded from Git. The test prediction export contains customer identifiers, so handle it as sensitive data. Review the model evaluation notes before treating the baseline as suitable for a business decision.
