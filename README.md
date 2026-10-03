# 🏦 Loan Approval Prediction System
*An End-to-End Machine Learning Web Application for Credit Risk Assessment*

---

## 1. Project Title
**Loan Approval Prediction System (LoanIQ)**

## 2. Project Overview
The **Loan Approval Prediction System** is an end-to-end Machine Learning web application designed to evaluate loan applicants based on personal demographics, financial assets, and credit scores. It transforms raw financial attributes through a rigorous preprocessing pipeline and provides real-time, probabilistic approval recommendations via an interactive Flask web interface.

## 3. Problem Statement
Retail lending institutions (banks, credit unions, and NBFCs) receive thousands of loan applications daily. Manual credit underwriting is labor-intensive, slow, and prone to human inconsistency. Furthermore, approving high-risk borrowers leads to costly loan defaults, while improperly denying creditworthy applicants leads to lost business. 

## 4. Objective
To build an automated, transparent, and accurate machine learning classification system that:
* Accurately categorizes loan applications into **Approved** or **Rejected**.
* Eliminates data leakage during preprocessing and evaluation.
* Provides clear explainability regarding feature importance.
* Deploys the winning model as a responsive, modern web application.

---

## 5. Dataset Description
The model was trained and evaluated on an authentic credit underwriting dataset consisting of:
* **Total Instances:** 4,269 records
* **Total Attributes:** 13 columns (1 identifier + 11 predictor features + 1 target)
* **Missing Values:** 0 null values across all columns
* **Duplicate Rows:** 0 duplicate entries

## 6. Features
The 11 predictor features represent key lending criteria:

| Feature Name | Type | Description |
|:---|:---|:---|
| `no_of_dependents` | Integer | Number of dependent family members (0 to 5) |
| `education` | Categorical | Highest education level (`Graduate`, `Not Graduate`) |
| `self_employed` | Categorical | Employment nature (`Yes` = Self-Employed, `No` = Salaried) |
| `income_annum` | Numerical (₹) | Annual gross income of the applicant |
| `loan_amount` | Numerical (₹) | Principal loan amount requested |
| `loan_term` | Numerical (Years) | Repayment duration (2 to 20 years) |
| `cibil_score` | Numerical (Score) | Credit bureau score (300 to 900) |
| `residential_assets_value` | Numerical (₹) | Market value of residential properties owned |
| `commercial_assets_value` | Numerical (₹) | Market value of commercial properties owned |
| `luxury_assets_value` | Numerical (₹) | Market value of luxury items (cars, jewelry) |
| `bank_asset_value` | Numerical (₹) | Total liquid deposits across bank accounts |

## 7. Target Variable
* **Column:** `loan_status`
* **Values:** 
  * `Approved` $\rightarrow$ Encoded as **`1`** (Positive Class, 2,656 records / 62.22%)
  * `Rejected` $\rightarrow$ Encoded as **`0`** (Negative Class, 1,613 records / 37.78%)

---

## 8. Machine Learning Approach
We adopted a disciplined, production-grade machine learning workflow:
1. **Exploratory Data Analysis (EDA):** Verifying distributions, categorical unique values, and boundary values.
2. **Data Sanitization:** Trimming column whitespaces and handling negative asset anomalies.
3. **Leakage-Free Splitting:** Stratified 80/20 train-test split (`random_state=42`) executed prior to fitting transformers.
4. **Scikit-Learn Pipeline:** Constructing a persistent `ColumnTransformer`.
5. **Model Benchmarking:** Training and evaluating 4 classification algorithms on the identical test split.
6. **Persistence & Deployment:** Exporting the preprocessor and winning model via `joblib`.

## 9. Data Preprocessing
* **Identifier Dropping:** `loan_id` removed (arbitrary index with zero predictive validity).
* **Anomaly Handling:** 28 records containing negative residential asset values (`-100,000`) were clipped to `0` (`clip(lower=0)`), avoiding data loss while maintaining physical consistency.
* **Numerical Scaling:** Standardized with `StandardScaler()` ($\mu = 0, \sigma = 1$).
* **Categorical Encoding:** `OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')` applied to prevent multicollinearity (dummy variable trap).
* **Fitted solely on `X_train`** to strictly prevent test data leakage.

---

## 10. Models Tested
1. **Logistic Regression** (Linear baseline)
2. **Decision Tree Classifier** (Non-linear rule-based tree)
3. **Random Forest Classifier** (Bagged ensemble of 100 decision trees)
4. **XGBoost Classifier** (Gradient boosted sequential decision trees)

## 11. Evaluation Metrics
Evaluated on **854 held-out test instances**:
* **Accuracy:** Overall correctness ($\frac{TP+TN}{Total}$)
* **Precision:** Accuracy of positive approval predictions ($\frac{TP}{TP+FP}$)
* **Recall:** Coverage of eligible loan applicants identified ($\frac{TP}{TP+FN}$)
* **F1-Score:** Harmonic balance between Precision and Recall
* **ROC-AUC:** Area under the ROC curve (discrimination capacity)
* **Confusion Matrix:** True/False Positives and Negatives

## 12. Actual Model Results

| Rank | Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 🥇 | **XGBoost** *(Selected)* | **98.48%** | **0.9868** | **0.9887** | **0.9878** | **0.9981** |
| 🥈 | **Decision Tree** | 98.36% | 0.9832 | 0.9906 | 0.9869 | 0.9814 |
| 🥉 | **Random Forest** | 98.01% | 0.9813 | 0.9868 | 0.9840 | 0.9988 |
| 4 | **Logistic Regression** | 91.45% | 0.9210 | 0.9435 | 0.9321 | 0.9726 |

### Selected Model Confusion Matrix (854 Test Samples)
```text
                     Predicted: Rejected (0)    Predicted: Approved (1)
Actual: Rejected (0)        316 (TN)                    7 (FP)
Actual: Approved (1)          6 (FN)                  525 (TP)
```
* Only **13 errors** out of 854 test applications (1.52% error rate).

---

## 13. Feature Importance
Measured from the trained XGBoost model:

| Rank | Feature | Importance Weight | Business Insight |
|:---:|:---|:---:|:---|
| 1 | `cibil_score` | **66.50%** | Single largest approval factor (credit reputation). |
| 2 | `loan_term` | **22.01%** | Loan duration directly impacts repayment risk. |
| 3 | `income_annum` | **3.33%** | Capacity to service monthly installments. |
| 4 | `loan_amount` | **2.64%** | Exposure volume. |
| 5 | `commercial_assets_value` | **1.10%** | Commercial property collateral. |
| 6 | `residential_assets_value` | **1.09%** | Real estate collateral equity. |
| 7 | `luxury_assets_value` | **1.07%** | Secondary asset cushion. |
| 8 | `no_of_dependents` | **0.85%** | Household expenditure pressure. |
| 9 | `education` | **0.60%** | Earning potential signal. |
| 10 | `bank_asset_value` | **0.59%** | Immediate liquidity. |
| 11 | `self_employed` | **0.21%** | Cash flow predictability. |

---

## 14. Web Application
The system features a web portal built with **Flask**, **HTML5**, **CSS3**, and **JavaScript**:
* **Applicant Form:** Responsive, card-based form with 11 inputs and built-in sanity checks.
* **Instant Demo Presets:** Quick 1-click test buttons (`High-Credit Sample`, `High-Risk Sample`) to demonstrate both outcomes immediately.
* **Prediction Result Page:** Clear decision banner, dynamic probability gauge, applicant summary table, and educational notice.
* **Model Analytics Dashboard:** Transparent presentation of empirical evaluation tables, confusion matrix, and feature importance bars.
* **Session Prediction History:** Tracks recent predictions within the active user session without storing sensitive information.

---

## 15. Technologies Used
* **Backend & ML Core:** Python 3.13, Scikit-learn, XGBoost, Pandas, NumPy, Joblib
* **Data Visualization:** Matplotlib, Seaborn
* **Web Framework:** Flask, Jinja2
* **Frontend:** HTML5, Modern CSS3, JavaScript (Vanilla ES6)

---

## 16. Project Structure
```text
Loan-Approval-Prediction/
│
├── data/
│   └── loan_approval_dataset.csv       # Original dataset (4,269 records)
│
├── notebooks/
│   ├── 01_data_exploration.ipynb       # EDA, distributions & data profiling
│   ├── 02_data_preprocessing.ipynb     # Preprocessing pipeline & leakage prevention
│   └── 03_model_training.ipynb         # Model training, comparisons & ROC curves
│
├── src/
│   ├── data_preprocessing.py           # Modular data cleaning & ColumnTransformer
│   ├── train_model.py                  # Model training, benchmarking & serialization
│   └── predict.py                      # Production inference module using saved artifacts
│
├── models/
│   ├── preprocessor.joblib             # Fitted ColumnTransformer pipeline
│   └── best_model.joblib               # Serialized top-performing XGBoost model
│
├── templates/
│   ├── index.html                      # Main applicant intake form & session history
│   ├── result.html                     # Prediction result, confidence & applicant recap
│   └── about.html                      # Technical evaluation dashboard & analytics
│
├── static/
│   ├── css/
│   │   └── style.css                   # Custom modern stylesheet
│   └── js/
│       └── script.js                   # Client-side validation & demo prefill
│
├── app.py                              # Flask application entry point
├── requirements.txt                    # Project dependency specification
├── README.md                           # Complete documentation
└── .gitignore                          # Git ignore specification
```

---

## 17. Installation Instructions

### Step 1: Clone or Navigate to the Repository
```bash
cd Loan-Approval-Prediction
```

### Step 2: (Optional) Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 18. How to Run

### Run the Web Application
```bash
python app.py
```

### Access in Your Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```

### (Optional) Retrain Models or Re-run Notebooks
```bash
# Run preprocessing
python src/data_preprocessing.py

# Run model training & evaluation
python src/train_model.py
```

---

## 19. Example Prediction Workflow

1. Navigate to `http://127.0.0.1:5000/`.
2. Click **"✨ High-Credit Sample (Approved)"** to auto-fill a prime borrower profile:
   * CIBIL Score: 778
   * Annual Income: ₹9,600,000
   * Loan Amount: ₹29,900,000
   * Loan Term: 12 Years
3. Click **"Run Loan Approval Prediction"**.
4. The system routes to `/predict` and renders the **Approved** result banner with ~99.98% confidence.
5. Click **"Predict Another Application"**, then click **"⚠️ High-Risk Sample (Rejected)"**:
   * CIBIL Score: 417
   * Annual Income: ₹4,100,000
   * Loan Amount: ₹12,200,000
   * Loan Term: 8 Years
6. The system accurately returns **Rejected** with ~99.95% confidence.

---

## 20. Limitations
* **Synthetic / Benchmark Artifacts:** The dataset exhibits clean linear relationships between CIBIL score and approval which makes models highly confident. Real-world underwriting involves messy, non-linear bureau reports.
* **Geographic / Demographic Scope:** Does not incorporate macroeconomic factors, inflation rates, or localized property valuation variations.
* **Unobserved Variables:** Does not capture debt-to-burden ratios, existing active loans (EMI outflow), or bank statement banking behavior.

## 21. Disclaimer
> ⚠️ **Educational & Portfolio Demonstration Notice:**  
> This project is for educational and portfolio demonstration purposes only. It is not an authorized credit assessment instrument or real financial lending decision system. It should never be used for actual credit underwriting or regulatory compliance.

## 22. Future Improvements
* Integration of SHAP (SHapley Additive exPlanations) values for real-time waterfall plots explaining individual customer decisions.
* Integration of multi-scenario simulations (e.g. "What CIBIL score or downpayment would change this to Approved?").
* RESTful JSON API endpoints (`/api/v1/predict`) with API token authentication for automated system integration.
* Containerization using Docker for cloud deployment (AWS ECS, Google Cloud Run, or Azure App Service).
