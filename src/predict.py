"""
Loan Approval Prediction System - Prediction Module
Author: AI Pair Programmer & User
Description:
    This module loads the trained model (best_model.joblib) and
    the fitted preprocessor (preprocessor.joblib) to make predictions
    on new loan application data.
"""

import os
import joblib
import pandas as pd
import numpy as np

# Cache model and preprocessor in memory to avoid reloading on every request
_PREPROCESSOR = None
_MODEL = None


def get_model_paths():
    """Returns absolute paths to saved preprocessor and model artifacts."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    preprocessor_path = os.path.join(base_dir, "models", "preprocessor.joblib")
    model_path = os.path.join(base_dir, "models", "best_model.joblib")
    return preprocessor_path, model_path


def load_artifacts():
    """
    Loads and caches the preprocessor and best model artifacts.

    Returns:
        tuple: (preprocessor, model)
    """
    global _PREPROCESSOR, _MODEL

    if _PREPROCESSOR is None or _MODEL is None:
        preprocessor_path, model_path = get_model_paths()

        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(
                f"Preprocessor artifact not found at '{preprocessor_path}'. Please run preprocessing first."
            )
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model artifact not found at '{model_path}'. Please run model training first."
            )

        _PREPROCESSOR = joblib.load(preprocessor_path)
        _MODEL = joblib.load(model_path)

    return _PREPROCESSOR, _MODEL


def format_application_input(application_data: dict) -> pd.DataFrame:
    """
    Validates and formats incoming applicant dictionary into a single-row DataFrame
    matching the exact feature structure expected by the preprocessor.

    Expected input keys (or form fields):
        - no_of_dependents (int)
        - education (str: 'Graduate' or 'Not Graduate')
        - self_employed (str: 'Yes' or 'No')
        - income_annum (float/int)
        - loan_amount (float/int)
        - loan_term (int/float)
        - cibil_score (int/float)
        - residential_assets_value (float/int)
        - commercial_assets_value (float/int)
        - luxury_assets_value (float/int)
        - bank_asset_value (float/int)
    """
    required_fields = [
        "no_of_dependents",
        "education",
        "self_employed",
        "income_annum",
        "loan_amount",
        "loan_term",
        "cibil_score",
        "residential_assets_value",
        "commercial_assets_value",
        "luxury_assets_value",
        "bank_asset_value",
    ]

    missing = [f for f in required_fields if f not in application_data]
    if missing:
        raise ValueError(f"Missing required application fields: {', '.join(missing)}")

    # Clean string values
    education = str(application_data["education"]).strip()
    self_employed = str(application_data["self_employed"]).strip()

    # Validate categories
    if education not in ["Graduate", "Not Graduate"]:
        raise ValueError(f"Invalid education value '{education}'. Must be 'Graduate' or 'Not Graduate'.")
    if self_employed not in ["Yes", "No"]:
        raise ValueError(f"Invalid self_employed value '{self_employed}'. Must be 'Yes' or 'No'.")

    # Numeric conversion & domain boundary checks
    try:
        no_of_dependents = int(application_data["no_of_dependents"])
        income_annum = float(application_data["income_annum"])
        loan_amount = float(application_data["loan_amount"])
        loan_term = int(application_data["loan_term"])
        cibil_score = int(application_data["cibil_score"])
        residential_assets_value = float(application_data["residential_assets_value"])
        commercial_assets_value = float(application_data["commercial_assets_value"])
        luxury_assets_value = float(application_data["luxury_assets_value"])
        bank_asset_value = float(application_data["bank_asset_value"])
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid numerical input: {e}")

    # Specific business validations
    if no_of_dependents < 0:
        raise ValueError("Number of dependents cannot be negative.")
    if income_annum < 0:
        raise ValueError("Annual income cannot be negative.")
    if loan_amount <= 0:
        raise ValueError("Loan amount must be greater than zero.")
    if loan_term <= 0:
        raise ValueError("Loan term must be a positive integer.")
    if not (300 <= cibil_score <= 900):
        raise ValueError("CIBIL score must be between 300 and 900.")
    if commercial_assets_value < 0 or luxury_assets_value < 0 or bank_asset_value < 0:
        raise ValueError("Asset values cannot be negative.")

    # Consistency with training data preprocessing:
    # Negative residential asset values are clipped to 0
    residential_assets_value = max(0.0, residential_assets_value)

    # Build single-row DataFrame matching training feature columns
    df_input = pd.DataFrame([{
        "no_of_dependents": no_of_dependents,
        "education": education,
        "self_employed": self_employed,
        "income_annum": income_annum,
        "loan_amount": loan_amount,
        "loan_term": loan_term,
        "cibil_score": cibil_score,
        "residential_assets_value": residential_assets_value,
        "commercial_assets_value": commercial_assets_value,
        "luxury_assets_value": luxury_assets_value,
        "bank_asset_value": bank_asset_value,
    }])

    return df_input


def predict_loan(application_data: dict) -> dict:
    """
    Main prediction entry point.
    Accepts applicant data, transforms using saved preprocessor artifact,
    and returns model prediction with probabilities and risk assessment.

    Args:
        application_data (dict): Dictionary of loan application details.

    Returns:
        dict: Prediction results including:
            - prediction (str): 'Approved' or 'Rejected'
            - prediction_code (int): 1 (Approved) or 0 (Rejected)
            - confidence (float): Probability percentage (0 to 100)
            - approved_prob (float): Probability of approval (0.0 to 1.0)
            - rejected_prob (float): Probability of rejection (0.0 to 1.0)
            - total_assets (float): Sum of all assets
            - debt_to_income_ratio (float): loan_amount / income_annum
    """
    # 1. Format and validate input data
    df_input = format_application_input(application_data)

    # 2. Load preprocessor and model artifacts
    preprocessor, model = load_artifacts()

    # 3. Transform features using saved preprocessor pipeline (No duplicate logic)
    X_processed = preprocessor.transform(df_input)

    # 4. Predict class and probabilities
    pred_code = int(model.predict(X_processed)[0])

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_processed)[0]
        # Binary target mapping: 0 = Rejected, 1 = Approved
        rejected_prob = float(probs[0])
        approved_prob = float(probs[1])
    else:
        approved_prob = 1.0 if pred_code == 1 else 0.0
        rejected_prob = 1.0 - approved_prob

    status = "Approved" if pred_code == 1 else "Rejected"
    confidence = (approved_prob if pred_code == 1 else rejected_prob) * 100

    # Calculate helpful summary metrics
    income = float(application_data["income_annum"])
    loan_amt = float(application_data["loan_amount"])
    dti_ratio = round(loan_amt / income, 2) if income > 0 else 0.0

    total_assets = (
        max(0.0, float(application_data.get("residential_assets_value", 0)))
        + float(application_data.get("commercial_assets_value", 0))
        + float(application_data.get("luxury_assets_value", 0))
        + float(application_data.get("bank_asset_value", 0))
    )

    return {
        "status": status,
        "prediction_code": pred_code,
        "confidence": round(confidence, 2),
        "approved_prob": round(approved_prob, 4),
        "rejected_prob": round(rejected_prob, 4),
        "cibil_score": int(application_data["cibil_score"]),
        "loan_amount": loan_amt,
        "loan_term": int(application_data["loan_term"]),
        "income_annum": income,
        "debt_to_income_ratio": dti_ratio,
        "total_assets": total_assets,
    }


if __name__ == "__main__":
    print("Testing predict_loan with sample applicant...")
    sample_approved = {
        "no_of_dependents": 2,
        "education": "Graduate",
        "self_employed": "No",
        "income_annum": 9600000,
        "loan_amount": 29900000,
        "loan_term": 12,
        "cibil_score": 778,
        "residential_assets_value": 2400000,
        "commercial_assets_value": 17600000,
        "luxury_assets_value": 22700000,
        "bank_asset_value": 8000000,
    }
    result = predict_loan(sample_approved)
    print("Sample Approved Test Result:", result)

    sample_rejected = {
        "no_of_dependents": 0,
        "education": "Not Graduate",
        "self_employed": "Yes",
        "income_annum": 4100000,
        "loan_amount": 12200000,
        "loan_term": 8,
        "cibil_score": 417,
        "residential_assets_value": 2700000,
        "commercial_assets_value": 2200000,
        "luxury_assets_value": 8800000,
        "bank_asset_value": 3300000,
    }
    result2 = predict_loan(sample_rejected)
    print("Sample Rejected Test Result:", result2)
