"""
Loan Approval Prediction System - Flask Web Application
Author: AI Pair Programmer & User
Description:
    Entry point for the web application. Serves the applicant intake form,
    validates user inputs, passes data to the prediction module, and
    displays prediction results with model confidence and risk metrics.
"""

import os
import sys
from datetime import datetime
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, session

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.predict import predict_loan, load_artifacts

app = Flask(__name__)
# Secret key for session management (used for prediction history)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "loan-approval-ml-secret-key-2026")


@app.before_request
def ensure_artifacts_loaded():
    """Ensures model and preprocessor are loaded into memory without retraining."""
    try:
        load_artifacts()
    except Exception as e:
        app.logger.error(f"Error loading model artifacts: {e}")


@app.route("/", methods=["GET"])
def home():
    """Renders the applicant input form and displays recent session predictions."""
    session_history = session.get("prediction_history", [])
    return render_template(
        "index.html",
        session_history=session_history,
        form_data={},
        error_message=None,
    )


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles form submission, validates all input fields,
    calls predict_loan(), stores prediction in session history,
    and displays the result page.
    """
    form_data = request.form.to_dict()

    try:
        # Validate and predict using our saved pipeline
        result = predict_loan(form_data)
        applicant_info = result["applicant"]

        # Record prediction into session history
        history = session.get("prediction_history", [])
        history.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "loan_amount": applicant_info["loan_amount"],
            "cibil_score": applicant_info["cibil_score"],
            "status": result["status"],
            "confidence": result["confidence"],
        })
        # Keep only the last 10 entries in session
        session["prediction_history"] = history[:10]

        return render_template("result.html", result=result, applicant=applicant_info)

    except ValueError as ve:
        # User-friendly validation error without stack trace
        session_history = session.get("prediction_history", [])
        return render_template(
            "index.html",
            error_message=str(ve),
            form_data=form_data,
            session_history=session_history,
        ), 400

    except Exception as e:
        # Catch unexpected errors gracefully
        app.logger.error(f"Unexpected prediction error: {e}")
        session_history = session.get("prediction_history", [])
        return render_template(
            "index.html",
            error_message="An unexpected system error occurred during prediction. Please verify your inputs and try again.",
            form_data=form_data,
            session_history=session_history,
        ), 500


@app.route("/about", methods=["GET"])
def about():
    """Renders the About and Model Analytics page."""
    return render_template("about.html")


@app.errorhandler(404)
def not_found(error):
    return render_template(
        "index.html",
        error_message="The requested page was not found. Redirected to home.",
        form_data={},
        session_history=session.get("prediction_history", []),
    ), 404


@app.errorhandler(500)
def server_error(error):
    return render_template(
        "index.html",
        error_message="An internal server error occurred. Please try again.",
        form_data={},
        session_history=session.get("prediction_history", []),
    ), 500


if __name__ == "__main__":
    # Bind to 0.0.0.0 and dynamic PORT for cloud hosting (Render, Railway, Docker, etc.)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
