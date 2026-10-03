"""
Loan Approval Prediction System - Data Preprocessing Module
Author: AI Pair Programmer & User
Description:
    This module provides clean, modular, and reusable functions to load,
    clean, and preprocess loan application data using scikit-learn.
    It handles invalid values, encodes categorical features, scales numerical
    features, splits data with stratification, and prevents data leakage.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


def load_data(file_path: str = None) -> pd.DataFrame:
    """
    Loads the loan approval dataset and strips whitespace from column names and string values.
    Automatically resolves relative paths whether called from project root or notebooks/.

    Args:
        file_path (str, optional): Path to the CSV file.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if file_path is None:
        # Check standard relative paths
        if os.path.exists(os.path.join("data", "loan_approval_dataset.csv")):
            file_path = os.path.join("data", "loan_approval_dataset.csv")
        elif os.path.exists(os.path.join("..", "data", "loan_approval_dataset.csv")):
            file_path = os.path.join("..", "data", "loan_approval_dataset.csv")
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            file_path = os.path.join(base_dir, "data", "loan_approval_dataset.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")

    df = pd.read_csv(file_path)

    # Strip leading/trailing whitespaces from column headers
    df.columns = df.columns.str.strip()

    # Strip whitespaces from object/string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataset:
    1. Removes 'loan_id' because it is an arbitrary applicant identifier without predictive power.
    2. Inspects and fixes invalid values: clips negative residential asset values (< 0) to 0.

    Args:
        df (pd.DataFrame): Raw DataFrame.

    Returns:
        pd.DataFrame: Cleaned DataFrame ready for feature/target separation.
    """
    df_cleaned = df.copy()

    # 1. Drop loan_id if present
    if "loan_id" in df_cleaned.columns:
        df_cleaned = df_cleaned.drop(columns=["loan_id"])

    # 2. Fix invalid negative residential asset values
    # In banking data, asset market value cannot be negative.
    # Rather than deleting rows (which causes data loss), we clip negative values to 0.
    if "residential_assets_value" in df_cleaned.columns:
        negative_count = (df_cleaned["residential_assets_value"] < 0).sum()
        if negative_count > 0:
            df_cleaned["residential_assets_value"] = df_cleaned["residential_assets_value"].clip(lower=0)

    return df_cleaned


def separate_features_target(df: pd.DataFrame, target_col: str = "loan_status"):
    """
    Separates the input features (X) and the target variable (y).
    Maps binary target: 'Approved' -> 1, 'Rejected' -> 0.

    Args:
        df (pd.DataFrame): Cleaned DataFrame.
        target_col (str): Name of target column.

    Returns:
        tuple[pd.DataFrame, pd.Series]: (X, y)
    """
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in dataframe.")

    X = df.drop(columns=[target_col])

    # Standard positive class convention: 1 = Approved, 0 = Rejected
    target_mapping = {"Approved": 1, "Rejected": 0}
    y = df[target_col].map(target_mapping)

    return X, y


def build_preprocessor(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
    """
    Builds a scikit-learn ColumnTransformer:
    - StandardScaler for numerical features (normalizes mean to 0, std to 1).
    - OneHotEncoder(drop='first') for binary categorical features.

    Args:
        numerical_cols (list): List of numerical column names.
        categorical_cols (list): List of categorical column names.

    Returns:
        ColumnTransformer: Configured preprocessor.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_cols),
            (
                "cat",
                OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )
    return preprocessor


def preprocess_data(
    file_path: str = None,
    test_size: float = 0.2,
    random_state: int = 42,
    save_pipeline_path: str = None,
):
    """
    Complete end-to-end preprocessing pipeline:
    1. Loads dataset.
    2. Cleans dataset (handles invalid values, removes loan_id).
    3. Splits features X and target y.
    4. Performs stratified train-test split (80/20, random_state=42).
    5. Fits preprocessor ONLY on training data to prevent data leakage.
    6. Transforms both X_train and X_test.
    7. Optionally saves fitted preprocessor to disk.

    Returns:
        tuple: (X_train_processed, X_test_processed, y_train, y_test, preprocessor, feature_names)
    """
    # 1. Load data
    df = load_data(file_path)

    # 2. Clean data
    df_cleaned = clean_data(df)

    # 3. Separate X and y
    X, y = separate_features_target(df_cleaned, target_col="loan_status")

    # 4. Train-Test Split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Identify column types
    numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

    # 5. Build preprocessor
    preprocessor = build_preprocessor(numerical_cols, categorical_cols)

    # 6. Fit ONLY on X_train to prevent data leakage!
    preprocessor.fit(X_train)

    # 7. Transform train and test
    X_train_processed = preprocessor.transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    feature_names = preprocessor.get_feature_names_out().tolist()

    # 8. Save preprocessor
    if save_pipeline_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        save_pipeline_path = os.path.join(base_dir, "models", "preprocessor.joblib")

    if save_pipeline_path:
        os.makedirs(os.path.dirname(save_pipeline_path), exist_ok=True)
        joblib.dump(preprocessor, save_pipeline_path)

    return X_train_processed, X_test_processed, y_train, y_test, preprocessor, feature_names


if __name__ == "__main__":
    print("=== Running Data Preprocessing Module ===")
    X_train_p, X_test_p, y_train, y_test, preprocessor, feature_names = preprocess_data()

    print(f"X_train processed shape : {X_train_p.shape}")
    print(f"X_test processed shape  : {X_test_p.shape}")
    print(f"y_train shape           : {y_train.shape}")
    print(f"y_test shape            : {y_test.shape}")
    print(f"Features ({len(feature_names)}): {feature_names}")
    print("Preprocessing completed successfully!")
