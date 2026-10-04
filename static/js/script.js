/**
 * Loan Approval Prediction System - Client-Side Validation & Dynamics
 * Author: AI Pair Programmer & User
 * Description:
 *   Handles instant real-time inline input validation, CIBIL credit meter updates,
 *   Indian currency previews (Lakhs / Crores), quick tenure chips, preset profiles,
 *   and smooth submit handling without disruptive browser alert() dialogs.
 */

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('loanForm');
  const btnApprovedSample = document.getElementById('btnSampleApproved');
  const btnModerateSample = document.getElementById('btnSampleModerate');
  const btnRejectedSample = document.getElementById('btnSampleRejected');
  const btnReset = document.getElementById('btnResetForm');
  const validationAlert = document.getElementById('validationAlert');
  const validationAlertText = document.getElementById('validationAlertText');
  const btnSubmit = document.getElementById('btnSubmitForm');
  const btnSubmitText = document.getElementById('btnSubmitText');
  const btnSubmitArrow = document.getElementById('btnSubmitArrow');

  // Input Elements
  const cibilInput = document.getElementById('cibil_score');
  const cibilBadge = document.getElementById('cibilBadge');
  const cibilDesc = document.getElementById('cibilDesc');

  const incomeInput = document.getElementById('income_annum');
  const loanInput = document.getElementById('loan_amount');
  const termInput = document.getElementById('loan_term');

  const resAssetInput = document.getElementById('residential_assets_value');
  const comAssetInput = document.getElementById('commercial_assets_value');
  const luxAssetInput = document.getElementById('luxury_assets_value');
  const bnkAssetInput = document.getElementById('bank_asset_value');

  const dependentsInput = document.getElementById('no_of_dependents');
  const educationInput = document.getElementById('education');
  const selfEmployedInput = document.getElementById('self_employed');

  // Currency preview target IDs
  const currencyFields = [
    'income_annum',
    'loan_amount',
    'residential_assets_value',
    'commercial_assets_value',
    'luxury_assets_value',
    'bank_asset_value',
  ];

  // All inputs to monitor for validation
  const allFieldIds = [
    'no_of_dependents',
    'education',
    'self_employed',
    'cibil_score',
    'income_annum',
    'loan_amount',
    'loan_term',
    'residential_assets_value',
    'commercial_assets_value',
    'luxury_assets_value',
    'bank_asset_value',
  ];

  /**
   * Safe parser for numeric strings containing commas, spaces, or currency symbols.
   */
  function parseCleanNumber(val) {
    if (val === null || val === undefined) return NaN;
    const cleanStr = val.toString().replace(/,/g, '').replace(/[₹$\s]/g, '').trim();
    if (cleanStr === '') return NaN;
    return parseFloat(cleanStr);
  }

  /**
   * Currency Formatter for Indian Numbering System (Lakhs and Crores).
   */
  function formatINR(val) {
    const num = parseCleanNumber(val);
    if (isNaN(num) || num <= 0) return '₹0';

    if (num >= 10000000) {
      return `₹${(num / 10000000).toFixed(2)} Cr`;
    } else if (num >= 100000) {
      return `₹${(num / 100000).toFixed(2)} Lakh`;
    } else if (num >= 1000) {
      return `₹${(num / 1000).toFixed(1)}k`;
    }
    return `₹${Math.round(num).toLocaleString('en-IN')}`;
  }

  /**
   * Updates currency preview badges underneath currency inputs.
   */
  function updateCurrencyPreviews() {
    currencyFields.forEach(function (id) {
      const input = document.getElementById(id);
      const preview = document.getElementById(id + '_preview');
      if (input && preview) {
        preview.textContent = formatINR(input.value);
      }
    });
  }

  /**
   * Updates CIBIL tier gauge badge and explanatory description.
   */
  function updateCibilWidget() {
    if (!cibilInput || !cibilBadge) return;
    const rawVal = cibilInput.value.trim();
    const score = parseInt(rawVal, 10);

    if (isNaN(score) || rawVal === "") {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-good';
      cibilBadge.textContent = '● Credit Standing (300 - 900)';
      if (cibilDesc) cibilDesc.textContent = 'Enter your credit score between 300 and 900. Higher scores increase approval chances.';
      return;
    }

    if (score < 300 || score > 900) {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-poor';
      cibilBadge.textContent = '✕ Invalid Range';
      if (cibilDesc) cibilDesc.textContent = 'CIBIL score must be between 300 and 900.';
      return;
    }

    if (score >= 750) {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-excellent';
      cibilBadge.textContent = '★ Prime Credit (750+)';
      if (cibilDesc) cibilDesc.textContent = 'Excellent credit history. Signifies minimal default risk and fastest approval.';
    } else if (score >= 650) {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-good';
      cibilBadge.textContent = '● Good Credit (650–749)';
      if (cibilDesc) cibilDesc.textContent = 'Strong credit standing with favorable terms from standard financial institutions.';
    } else if (score >= 550) {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-fair';
      cibilBadge.textContent = '▲ Moderate Credit (550–649)';
      if (cibilDesc) cibilDesc.textContent = 'Moderate risk tier. Requires supportive income and declared asset backing.';
    } else {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-poor';
      cibilBadge.textContent = '✕ High Risk Credit (< 550)';
      if (cibilDesc) cibilDesc.textContent = 'Sub-prime tier. Higher likelihood of decline or requirement of additional collateral.';
    }
  }

  /**
   * Display inline error for a specific input field.
   */
  function setFieldError(fieldId, errorMsg) {
    const input = document.getElementById(fieldId);
    const errBox = document.getElementById('err_' + fieldId);

    if (input) {
      input.classList.add('is-invalid');
      input.classList.remove('is-valid');
    }
    if (errBox) {
      errBox.innerHTML = `<span>⚠️</span> <span>${errorMsg}</span>`;
      errBox.classList.add('visible');
    }
  }

  /**
   * Clear inline error for a specific input field.
   */
  function clearFieldError(fieldId) {
    const input = document.getElementById(fieldId);
    const errBox = document.getElementById('err_' + fieldId);

    if (input) {
      input.classList.remove('is-invalid');
      input.classList.add('is-valid');
    }
    if (errBox) {
      errBox.innerHTML = '';
      errBox.classList.remove('visible');
    }
  }

  /**
   * Validates a single field by ID.
   * Returns true if valid, false if invalid.
   */
  function validateField(fieldId) {
    const el = document.getElementById(fieldId);
    if (!el) return true;

    const rawVal = el.value.trim();

    // 1. Dependents (default 0 if empty)
    if (fieldId === 'no_of_dependents') {
      if (rawVal === '') {
        clearFieldError(fieldId);
        return true;
      }
      const dep = parseInt(rawVal, 10);
      if (isNaN(dep) || dep < 0 || dep > 10) {
        setFieldError(fieldId, 'Please select a valid number of dependents (0 to 10).');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    // 2. Education
    if (fieldId === 'education') {
      if (rawVal !== 'Graduate' && rawVal !== 'Not Graduate') {
        setFieldError(fieldId, 'Please select your educational qualification.');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    // 3. Self Employed
    if (fieldId === 'self_employed') {
      if (rawVal !== 'Yes' && rawVal !== 'No') {
        setFieldError(fieldId, 'Please select your employment type.');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    // 4. CIBIL Score
    if (fieldId === 'cibil_score') {
      if (rawVal === '') {
        setFieldError(fieldId, 'Please enter your CIBIL score (300 to 900).');
        return false;
      }
      const cibil = parseInt(rawVal, 10);
      if (isNaN(cibil) || cibil < 300 || cibil > 900) {
        setFieldError(fieldId, 'CIBIL credit score must be an integer between 300 and 900.');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    // 5. Annual Income (Any positive amount)
    if (fieldId === 'income_annum') {
      if (rawVal === '') {
        setFieldError(fieldId, 'Please enter your annual gross income.');
        return false;
      }
      const income = parseCleanNumber(rawVal);
      if (isNaN(income) || income <= 0) {
        setFieldError(fieldId, 'Annual income must be a valid positive number.');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    // 6. Loan Amount (Any positive amount)
    if (fieldId === 'loan_amount') {
      if (rawVal === '') {
        setFieldError(fieldId, 'Please enter the requested loan amount.');
        return false;
      }
      const loan = parseCleanNumber(rawVal);
      if (isNaN(loan) || loan <= 0) {
        setFieldError(fieldId, 'Loan amount must be a valid positive number.');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    // 7. Loan Term
    if (fieldId === 'loan_term') {
      if (rawVal === '') {
        setFieldError(fieldId, 'Please enter repayment tenure (1 to 30 years).');
        return false;
      }
      const term = parseInt(rawVal, 10);
      if (isNaN(term) || term < 1 || term > 30) {
        setFieldError(fieldId, 'Loan repayment tenure must be between 1 and 30 years.');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    // 8. Asset Values (Residential, Commercial, Luxury, Bank) - Optional
    if (
      fieldId === 'residential_assets_value' ||
      fieldId === 'commercial_assets_value' ||
      fieldId === 'luxury_assets_value' ||
      fieldId === 'bank_asset_value'
    ) {
      if (rawVal === '') {
        // Empty is valid and safely treated as 0
        clearFieldError(fieldId);
        return true;
      }
      const assetVal = parseCleanNumber(rawVal);
      if (isNaN(assetVal) || assetVal < 0) {
        setFieldError(fieldId, 'Asset valuation cannot be negative (enter 0 or leave blank).');
        return false;
      }
      clearFieldError(fieldId);
      return true;
    }

    clearFieldError(fieldId);
    return true;
  }

  /**
   * Validates all form inputs. Returns boolean indicating complete validity.
   */
  function validateEntireForm() {
    let isValid = true;
    let firstInvalidEl = null;

    allFieldIds.forEach(function (fieldId) {
      const fieldValid = validateField(fieldId);
      if (!fieldValid) {
        isValid = false;
        if (!firstInvalidEl) {
          firstInvalidEl = document.getElementById(fieldId);
        }
      }
    });

    if (!isValid) {
      if (validationAlert) {
        validationAlert.style.display = 'flex';
        if (validationAlertText) {
          validationAlertText.textContent = 'Please correct the highlighted inputs above before proceeding.';
        }
      }
      if (firstInvalidEl) {
        firstInvalidEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalidEl.focus();
      }
    } else {
      if (validationAlert) {
        validationAlert.style.display = 'none';
      }
    }

    return isValid;
  }

  // Bind live change and blur listeners on all inputs
  allFieldIds.forEach(function (fieldId) {
    const el = document.getElementById(fieldId);
    if (el) {
      el.addEventListener('input', function () {
        validateField(fieldId);
        updateCurrencyPreviews();
        if (fieldId === 'cibil_score') updateCibilWidget();
        if (fieldId === 'loan_term') syncChipStates(el.value);
      });
      el.addEventListener('blur', function () {
        validateField(fieldId);
      });
    }
  });

  // Tenure quick chips
  const chipButtons = document.querySelectorAll('.chip-btn');
  function syncChipStates(currentVal) {
    chipButtons.forEach(function (btn) {
      if (btn.getAttribute('data-tenure') === currentVal.toString()) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  chipButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const tenure = this.getAttribute('data-tenure');
      if (termInput) {
        termInput.value = tenure;
        validateField('loan_term');
        syncChipStates(tenure);
      }
    });
  });

  // Sample Data Profiles
  const sampleApproved = {
    no_of_dependents: '2',
    education: 'Graduate',
    self_employed: 'No',
    cibil_score: 780,
    income_annum: 1800000,
    loan_amount: 3500000,
    loan_term: 15,
    residential_assets_value: 2500000,
    commercial_assets_value: 1000000,
    luxury_assets_value: 800000,
    bank_asset_value: 600000,
  };

  const sampleModerate = {
    no_of_dependents: '1',
    education: 'Graduate',
    self_employed: 'No',
    cibil_score: 710,
    income_annum: 900000,
    loan_amount: 1800000,
    loan_term: 10,
    residential_assets_value: 1500000,
    commercial_assets_value: 0,
    luxury_assets_value: 300000,
    bank_asset_value: 250000,
  };

  const sampleRejected = {
    no_of_dependents: '3',
    education: 'Not Graduate',
    self_employed: 'Yes',
    cibil_score: 420,
    income_annum: 450000,
    loan_amount: 2500000,
    loan_term: 8,
    residential_assets_value: 200000,
    commercial_assets_value: 0,
    luxury_assets_value: 150000,
    bank_asset_value: 50000,
  };

  function fillForm(data) {
    for (const [key, value] of Object.entries(data)) {
      const el = document.getElementById(key);
      if (el) {
        el.value = value;
        clearFieldError(key);
      }
    }
    if (validationAlert) validationAlert.style.display = 'none';
    updateCurrencyPreviews();
    updateCibilWidget();
    if (data.loan_term) syncChipStates(data.loan_term);
  }

  if (btnApprovedSample) {
    btnApprovedSample.addEventListener('click', function () {
      fillForm(sampleApproved);
    });
  }

  if (btnModerateSample) {
    btnModerateSample.addEventListener('click', function () {
      fillForm(sampleModerate);
    });
  }

  if (btnRejectedSample) {
    btnRejectedSample.addEventListener('click', function () {
      fillForm(sampleRejected);
    });
  }

  if (btnReset) {
    btnReset.addEventListener('click', function () {
      if (form) {
        form.reset();
        allFieldIds.forEach(function (fieldId) {
          const el = document.getElementById(fieldId);
          if (el) {
            el.classList.remove('is-invalid');
            el.classList.remove('is-valid');
          }
          const errBox = document.getElementById('err_' + fieldId);
          if (errBox) {
            errBox.innerHTML = '';
            errBox.classList.remove('visible');
          }
        });
        if (validationAlert) validationAlert.style.display = 'none';
        setTimeout(function () {
          updateCurrencyPreviews();
          updateCibilWidget();
          if (termInput) syncChipStates(termInput.value);
        }, 10);
      }
    });
  }

  // Intercept form submission for validation
  if (form) {
    form.addEventListener('submit', function (e) {
      const isFormValid = validateEntireForm();
      if (!isFormValid) {
        e.preventDefault();
        return false;
      }

      // If valid, show loading indicator on submit button
      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.style.opacity = '0.85';
        if (btnSubmitText) {
          btnSubmitText.innerHTML = '<span class="btn-spinner"></span> Evaluating Application...';
        }
        if (btnSubmitArrow) {
          btnSubmitArrow.style.display = 'none';
        }
      }
      return true;
    });
  }

  // Initialize display states on page load
  updateCurrencyPreviews();
  updateCibilWidget();
  if (termInput) syncChipStates(termInput.value);
});
