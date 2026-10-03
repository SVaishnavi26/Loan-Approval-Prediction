"""
Loan Approval Prediction System - Model Training Module
Author: AI Pair Programmer & User
Description:
    This module trains, evaluates, and compares multiple classification models:
    1. Logistic Regression
    2. Decision Tree Classifier
    3. Random Forest Classifier
    4. XGBoost Classifier (if available)

    It computes key performance metrics:
    - Accuracy
    - Precision
    - Recall
    - F1-Score
    - ROC-AUC
    - Confusion Matrix

    It selects and saves the best performing model for deployment.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Check if XGBoost is available
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

# Ensure local imports work when run as script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_preprocessing import preprocess_data


def get_models(random_state: int = 42) -> dict:
    """
    Initializes the classification models to be evaluated.

    Args:
        random_state (int): Seed for reproducibility.

    Returns:
        dict: Mapping of model name to instantiated model object.
    """
    models = {
        "Logistic Regression": LogisticRegression(random_state=random_state, max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=random_state),
        "Random Forest": RandomForestClassifier(random_state=random_state, n_estimators=100),
    }

    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            random_state=random_state,
            eval_metric="logloss",
            n_estimators=100,
        )

    return models


def evaluate_model(model, X_test, y_test) -> dict:
    """
    Evaluates a trained model on the unseen test dataset.

    Args:
        model: Trained scikit-learn or XGBoost classifier.
        X_test: Processed test features.
        y_test: True test labels.

    Returns:
        dict: Performance metrics and confusion matrix.
    """
    y_pred = model.predict(X_test)

    # Compute predicted probabilities for ROC-AUC if supported
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        y_prob = y_pred

    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1-Score": f1_score(y_test, y_pred),
        "ROC-AUC": roc_auc_score(y_test, y_prob),
        "Confusion Matrix": confusion_matrix(y_test, y_pred),
        "Classification Report": classification_report(y_test, y_pred),
    }
    return metrics


def train_and_compare(X_train, X_test, y_train, y_test, random_state: int = 42):
    """
    Trains all candidate models, evaluates them on test data, and returns a summary.

    Returns:
        tuple: (results_df, trained_models, best_model_name)
    """
    models = get_models(random_state=random_state)
    results = []
    trained_models = {}

    print("=" * 70)
    print(">>> TRAINING & EVALUATING CANDIDATE MODELS")
    print("=" * 70)

    for name, model in models.items():
        print(f"\nTraining [{name}]...")
        # Train ONLY on training set to prevent data leakage
        model.fit(X_train, y_train)

        # Evaluate on test set
        metrics = evaluate_model(model, X_test, y_test)

        print(f"  + Accuracy : {metrics['Accuracy']:.4f}")
        print(f"  + Precision: {metrics['Precision']:.4f}")
        print(f"  + Recall   : {metrics['Recall']:.4f}")
        print(f"  + F1-Score : {metrics['F1-Score']:.4f}")
        print(f"  + ROC-AUC  : {metrics['ROC-AUC']:.4f}")
        print(f"  Confusion Matrix:\n{metrics['Confusion Matrix']}")

        results.append({
            "Model": name,
            "Accuracy": round(metrics["Accuracy"], 4),
            "Precision": round(metrics["Precision"], 4),
            "Recall": round(metrics["Recall"], 4),
            "F1-Score": round(metrics["F1-Score"], 4),
            "ROC-AUC": round(metrics["ROC-AUC"], 4),
        })
        trained_models[name] = model

    results_df = pd.DataFrame(results)

    # Rank by F1-Score, then ROC-AUC
    results_df = results_df.sort_values(by=["F1-Score", "ROC-AUC"], ascending=False).reset_index(drop=True)
    best_model_name = results_df.iloc[0]["Model"]

    return results_df, trained_models, best_model_name


def save_model(model, filepath: str = os.path.join("models", "best_model.joblib")):
    """
    Saves the trained model to disk.

    Args:
        model: Trained model object.
        filepath: Destination path.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"\n[INFO] Model successfully saved to: {filepath}")


def get_feature_importances(model, feature_names: list) -> pd.DataFrame:
    """
    Extracts feature importances if available from tree-based models.

    Args:
        model: Trained tree model.
        feature_names: List of processed feature names.

    Returns:
        pd.DataFrame: Sorted feature importances.
    """
    if hasattr(model, "feature_importances_"):
        fi_df = pd.DataFrame({
            "Feature": feature_names,
            "Importance": model.feature_importances_,
        }).sort_values(by="Importance", ascending=False).reset_index(drop=True)
        return fi_df
    return pd.DataFrame()


def run_pipeline():
    """
    End-to-end execution of preprocessing, training, model comparison, and saving.
    """
    # 1. Load preprocessed data
    print("1. Loading and preprocessing data...")
    X_train, X_test, y_train, y_test, preprocessor, feature_names = preprocess_data()

    # 2. Train and compare models
    results_df, trained_models, best_model_name = train_and_compare(
        X_train, X_test, y_train, y_test
    )

    print("\n" + "=" * 70)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 70)
    print(results_df.to_string(index=False))

    print(f"\n[WINNER] Best Model Selected: {best_model_name}")

    # 3. Feature importance
    best_model = trained_models[best_model_name]
    fi_df = get_feature_importances(best_model, feature_names)
    if not fi_df.empty:
        print("\nTop Feature Importances:")
        print(fi_df.to_string(index=False))

    # 4. Save best model
    best_model_path = os.path.join("models", "best_model.joblib")
    save_model(best_model, best_model_path)

    return results_df, best_model_name


if __name__ == "__main__":
    run_pipeline()
