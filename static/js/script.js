/**
 * Loan Approval Prediction System - Modern Interactive Scripts
 * Provides live currency conversion (Lakhs/Crores), CIBIL tier meter,
 * real-time financial ratio calculation, and demo preset loading.
 */

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('loanForm');
  const btnApprovedSample = document.getElementById('btnSampleApproved');
  const btnRejectedSample = document.getElementById('btnSampleRejected');
  const btnReset = document.getElementById('btnResetForm');

  // Input elements
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

  // Live Summary Elements
  const liveTotalAssets = document.getElementById('liveTotalAssets');
  const liveDti = document.getElementById('liveDti');
  const liveCibilScore = document.getElementById('liveCibilScore');

  // Currency Formatter (Indian Numbering System - Lakhs & Crores)
  function formatINR(val) {
    const num = parseFloat(val);
    if (isNaN(num) || num <= 0) return '₹0';
    if (num >= 10000000) {
      return `₹${(num / 10000000).toFixed(2)} Cr`;
    } else if (num >= 100000) {
      return `₹${(num / 100000).toFixed(2)} Lakh`;
    } else if (num >= 1000) {
      return `₹${(num / 1000).toFixed(1)}k`;
    }
    return `₹${num.toLocaleString('en-IN')}`;
  }

  // Bind live currency preview beneath inputs
  const currencyFieldIds = [
    'income_annum',
    'loan_amount',
    'residential_assets_value',
    'commercial_assets_value',
    'luxury_assets_value',
    'bank_asset_value',
  ];

  function updateCurrencyPreviews() {
    currencyFieldIds.forEach(function (id) {
      const input = document.getElementById(id);
      const preview = document.getElementById(id + '_preview');
      if (input && preview) {
        preview.textContent = formatINR(input.value);
      }
    });
  }

  // Update CIBIL Score Gauge
  function updateCibilWidget() {
    if (!cibilInput || !cibilBadge) return;
    const score = parseInt(cibilInput.value, 10);

    if (isNaN(score)) {
      cibilBadge.textContent = 'Invalid';
      cibilBadge.className = 'cibil-rating';
      if (cibilDesc) cibilDesc.textContent = 'Enter a valid score (300 - 900)';
      return;
    }

    if (liveCibilScore) liveCibilScore.textContent = score;

    cibilBadge.className = 'cibil-rating';
    if (score >= 750) {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-excellent';
      cibilBadge.textContent = '★ Prime Credit (750+)';
      if (cibilDesc) cibilDesc.textContent = 'Very low default risk. Highest likelihood of fast approval.';
    } else if (score >= 650) {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-good';
      cibilBadge.textContent = '● Good Credit (650–749)';
      if (cibilDesc) cibilDesc.textContent = 'Favorable credit history with manageable risk.';
    } else if (score >= 550) {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-fair';
      cibilBadge.textContent = '▲ Moderate Credit (550–649)';
      if (cibilDesc) cibilDesc.textContent = 'Moderate risk tier. Collateral and income are closely weighed.';
    } else {
      cibilBadge.className = 'cibil-tier-indicator cibil-tier-poor';
      cibilBadge.textContent = '✕ Low Credit (< 550)';
      if (cibilDesc) cibilDesc.textContent = 'High risk flag. May require guarantor or lower loan amount.';
    }
  }

  // Update Live Financial Metrics Bar
  function updateLiveSummary() {
    const income = parseFloat(incomeInput ? incomeInput.value : 0) || 0;
    const loan = parseFloat(loanInput ? loanInput.value : 0) || 0;

    const res = Math.max(0, parseFloat(resAssetInput ? resAssetInput.value : 0) || 0);
    const com = parseFloat(comAssetInput ? comAssetInput.value : 0) || 0;
    const lux = parseFloat(luxAssetInput ? luxAssetInput.value : 0) || 0;
    const bnk = parseFloat(bnkAssetInput ? bnkAssetInput.value : 0) || 0;

    const totalAssets = res + com + lux + bnk;
    if (liveTotalAssets) {
      liveTotalAssets.textContent = formatINR(totalAssets);
    }

    if (liveDti) {
      if (income > 0 && loan > 0) {
        const dti = (loan / income).toFixed(2);
        liveDti.textContent = `${dti}x Income`;
      } else {
        liveDti.textContent = '—';
      }
    }
  }

  // Listen to input changes
  const allWatchedInputs = [
    cibilInput,
    incomeInput,
    loanInput,
    termInput,
    resAssetInput,
    comAssetInput,
    luxAssetInput,
    bnkAssetInput,
  ];

  allWatchedInputs.forEach(function (inp) {
    if (inp) {
      inp.addEventListener('input', function () {
        updateCurrencyPreviews();
        updateCibilWidget();
        updateLiveSummary();
      });
    }
  });

  // Sample profiles from real dataset
  const sampleApproved = {
    no_of_dependents: 2,
    education: 'Graduate',
    self_employed: 'No',
    income_annum: 9600000,
    loan_amount: 29900000,
    loan_term: 12,
    cibil_score: 778,
    residential_assets_value: 2400000,
    commercial_assets_value: 17600000,
    luxury_assets_value: 22700000,
    bank_asset_value: 8000000,
  };

  const sampleRejected = {
    no_of_dependents: 0,
    education: 'Not Graduate',
    self_employed: 'Yes',
    income_annum: 4100000,
    loan_amount: 12200000,
    loan_term: 8,
    cibil_score: 417,
    residential_assets_value: 2700000,
    commercial_assets_value: 2200000,
    luxury_assets_value: 8800000,
    bank_asset_value: 3300000,
  };

  function fillForm(data) {
    for (const [key, value] of Object.entries(data)) {
      const el = document.getElementById(key);
      if (el) {
        el.value = value;
      }
    }
    updateCurrencyPreviews();
    updateCibilWidget();
    updateLiveSummary();
  }

  if (btnApprovedSample) {
    btnApprovedSample.addEventListener('click', function () {
      fillForm(sampleApproved);
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
        setTimeout(function () {
          updateCurrencyPreviews();
          updateCibilWidget();
          updateLiveSummary();
        }, 10);
      }
    });
  }

  // Initial calculation on page load
  updateCurrencyPreviews();
  updateCibilWidget();
  updateLiveSummary();

  // Client-side validation
  if (form) {
    form.addEventListener('submit', function (e) {
      const cibil = parseInt(cibilInput ? cibilInput.value : 0, 10);
      if (isNaN(cibil) || cibil < 300 || cibil > 900) {
        e.preventDefault();
        alert('CIBIL score must be between 300 and 900.');
        if (cibilInput) cibilInput.focus();
        return false;
      }

      const income = parseFloat(incomeInput ? incomeInput.value : 0);
      if (isNaN(income) || income < 0) {
        e.preventDefault();
        alert('Annual income cannot be negative.');
        if (incomeInput) incomeInput.focus();
        return false;
      }

      const loan = parseFloat(loanInput ? loanInput.value : 0);
      if (isNaN(loan) || loan <= 0) {
        e.preventDefault();
        alert('Loan amount must be greater than zero.');
        if (loanInput) loanInput.focus();
        return false;
      }

      const term = parseInt(termInput ? termInput.value : 0, 10);
      if (isNaN(term) || term <= 0) {
        e.preventDefault();
        alert('Loan term must be a positive integer.');
        if (termInput) termInput.focus();
        return false;
      }
    });
  }
});
