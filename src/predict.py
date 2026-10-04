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


def _clean_numeric(value, field_label: str, is_integer: bool = False, min_val: float = None, max_val: float = None, default_val: float = None):
    """
    Cleans string representation of numbers (removes commas, currency signs, whitespace)
    and validates boundary ranges. If value is empty and default_val is provided, returns default_val.
    """
    if value is None or str(value).strip() == "":
        if default_val is not None:
            return default_val
        raise ValueError(f"{field_label} is required.")

    # Remove commas, currency symbols, spaces
    val_str = str(value).strip().replace(",", "").replace("₹", "").replace("$", "").replace(" ", "")
    try:
        num = int(round(float(val_str))) if is_integer else float(val_str)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid input for '{field_label}'. Please enter a valid number.")

    if min_val is not None and num < min_val:
        raise ValueError(f"{field_label} must be at least {min_val:g}.")
    if max_val is not None and num > max_val:
        raise ValueError(f"{field_label} cannot exceed {max_val:g}.")

    return num


def format_application_input(application_data: dict) -> pd.DataFrame:
    """
    Validates and formats incoming applicant dictionary into a single-row DataFrame
    matching the exact feature structure expected by the preprocessor.

    Expected input keys (or form fields):
        - no_of_dependents (int, 0 to 10, default: 0)
        - education (str: 'Graduate' or 'Not Graduate')
        - self_employed (str: 'Yes' or 'No')
        - income_annum (float, > 0)
        - loan_amount (float, > 0)
        - loan_term (int, 1 to 30)
        - cibil_score (int, 300 to 900)
        - residential_assets_value (float, >= 0, default: 0.0)
        - commercial_assets_value (float, >= 0, default: 0.0)
        - luxury_assets_value (float, >= 0, default: 0.0)
        - bank_asset_value (float, >= 0, default: 0.0)
    """
    # Core mandatory fields
    required_fields = [
        "education",
        "self_employed",
        "income_annum",
        "loan_amount",
        "loan_term",
        "cibil_score",
    ]

    missing = [f for f in required_fields if f not in application_data or str(application_data[f]).strip() == ""]
    if missing:
        field_labels = {
            "education": "Education",
            "self_employed": "Employment type",
            "income_annum": "Annual income",
            "loan_amount": "Requested loan amount",
            "loan_term": "Repayment tenure",
            "cibil_score": "CIBIL score",
        }
        missing_names = ", ".join(field_labels.get(f, f) for f in missing)
        raise ValueError(f"Please fill in all required fields: {missing_names}.")

    # Clean & normalize categorical values
    education = str(application_data["education"]).strip()
    self_employed = str(application_data["self_employed"]).strip()

    if "not graduate" in education.lower():
        education = "Not Graduate"
    elif "graduate" in education.lower():
        education = "Graduate"

    if self_employed.lower() in ["no", "salaried", "salaried employee"]:
        self_employed = "No"
    elif self_employed.lower() in ["yes", "self-employed", "business"]:
        self_employed = "Yes"

    if education not in ["Graduate", "Not Graduate"]:
        raise ValueError(f"Invalid education value '{education}'. Must be 'Graduate' or 'Not Graduate'.")
    if self_employed not in ["Yes", "No"]:
        raise ValueError(f"Invalid employment type '{self_employed}'. Must be 'Salaried' or 'Self-Employed'.")

    # Validate numerical fields with flexible, unconstrained boundaries
    no_of_dependents = _clean_numeric(
        application_data.get("no_of_dependents"), "Number of dependents", is_integer=True, min_val=0, max_val=10, default_val=0
    )
    cibil_score = _clean_numeric(
        application_data.get("cibil_score"), "CIBIL credit score", is_integer=True, min_val=300, max_val=900
    )
    income_annum = _clean_numeric(
        application_data.get("income_annum"), "Annual income", is_integer=False, min_val=1
    )
    loan_amount = _clean_numeric(
        application_data.get("loan_amount"), "Requested loan amount", is_integer=False, min_val=1
    )
    loan_term = _clean_numeric(
        application_data.get("loan_term"), "Repayment tenure (years)", is_integer=True, min_val=1, max_val=30
    )

    # Assets default to 0.0 if not owned or left empty by the applicant
    residential_assets_value = _clean_numeric(
        application_data.get("residential_assets_value"), "Residential property value", is_integer=False, min_val=0, default_val=0.0
    )
    commercial_assets_value = _clean_numeric(
        application_data.get("commercial_assets_value"), "Commercial property value", is_integer=False, min_val=0, default_val=0.0
    )
    luxury_assets_value = _clean_numeric(
        application_data.get("luxury_assets_value"), "Luxury assets value", is_integer=False, min_val=0, default_val=0.0
    )
    bank_asset_value = _clean_numeric(
        application_data.get("bank_asset_value"), "Bank balance & savings", is_integer=False, min_val=0, default_val=0.0
    )

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
            - status (str): 'Approved' or 'Rejected'
            - prediction_code (int): 1 (Approved) or 0 (Rejected)
            - confidence (float): Probability percentage (0 to 100)
            - approved_prob (float): Probability of approval (0.0 to 1.0)
            - rejected_prob (float): Probability of rejection (0.0 to 1.0)
            - total_assets (float): Sum of all assets
            - debt_to_income_ratio (float): loan_amount / income_annum
            - applicant (dict): Cleaned and typed applicant dictionary
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

    # Extract cleaned values directly from df_input
    income = float(df_input["income_annum"].iloc[0])
    loan_amt = float(df_input["loan_amount"].iloc[0])
    dti_ratio = round(loan_amt / income, 2) if income > 0 else 0.0

    total_assets = (
        float(df_input["residential_assets_value"].iloc[0])
        + float(df_input["commercial_assets_value"].iloc[0])
        + float(df_input["luxury_assets_value"].iloc[0])
        + float(df_input["bank_asset_value"].iloc[0])
    )

    applicant_clean = {
        "no_of_dependents": int(df_input["no_of_dependents"].iloc[0]),
        "education": str(df_input["education"].iloc[0]),
        "self_employed": str(df_input["self_employed"].iloc[0]),
        "income_annum": income,
        "loan_amount": loan_amt,
        "loan_term": int(df_input["loan_term"].iloc[0]),
        "cibil_score": int(df_input["cibil_score"].iloc[0]),
        "residential_assets_value": float(df_input["residential_assets_value"].iloc[0]),
        "commercial_assets_value": float(df_input["commercial_assets_value"].iloc[0]),
        "luxury_assets_value": float(df_input["luxury_assets_value"].iloc[0]),
        "bank_asset_value": float(df_input["bank_asset_value"].iloc[0]),
    }

    return {
        "status": status,
        "prediction_code": pred_code,
        "confidence": round(confidence, 2),
        "approved_prob": round(approved_prob, 4),
        "rejected_prob": round(rejected_prob, 4),
        "cibil_score": applicant_clean["cibil_score"],
        "loan_amount": loan_amt,
        "loan_term": applicant_clean["loan_term"],
        "income_annum": income,
        "debt_to_income_ratio": dti_ratio,
        "total_assets": round(total_assets, 2),
        "applicant": applicant_clean,
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
