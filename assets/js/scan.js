// ScamShield scan & shared UI logic
// Handles: navigation toggle, year, loading spinner, toast notifications and the Scan page dummy /predict flow.

(function () {
    const global = (window.ScamShield = window.ScamShield || {});

    function $(id) {
        return document.getElementById(id);
    }

    function initNav() {
        const toggle = $('nav-toggle');
        const menu = $('nav-menu');
        if (!toggle || !menu) return;
        toggle.addEventListener('click', function () {
            menu.classList.toggle('open');
        });
    }

    function initYear() {
        const yearEl = $('year');
        if (yearEl) {
            yearEl.textContent = new Date().getFullYear();
        }
    }

    function showSpinner() {
        const spinner = $('global-spinner');
        if (spinner) spinner.classList.add('visible');
    }

    function hideSpinner() {
        const spinner = $('global-spinner');
        if (spinner) spinner.classList.remove('visible');
    }

    function isAuthenticated() {
        try {
            return !!window.localStorage.getItem('scamshieldUser');
        } catch (err) {
            return false;
        }
    }

    function showToast(options) {
        const { type = 'info', title = '', message = '', timeout = 3500 } = options || {};
        const container = $('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = 'toast toast-' + type;

        const pill = document.createElement('div');
        pill.className = 'toast-pill';
        pill.textContent = type === 'success' ? '✓' : type === 'error' ? '!' : 'ℹ';

        const body = document.createElement('div');
        body.className = 'toast-body';
        const titleEl = document.createElement('div');
        titleEl.className = 'toast-title';
        titleEl.textContent = title || (type === 'success' ? 'Success' : type === 'error' ? 'Error' : 'Notice');
        const msgEl = document.createElement('div');
        msgEl.className = 'toast-message';
        msgEl.textContent = message;
        body.appendChild(titleEl);
        body.appendChild(msgEl);

        const close = document.createElement('button');
        close.type = 'button';
        close.className = 'toast-close';
        close.textContent = '×';
        close.addEventListener('click', function () {
            container.removeChild(toast);
        });

        toast.appendChild(pill);
        toast.appendChild(body);
        toast.appendChild(close);
        container.appendChild(toast);

        if (timeout > 0) {
            setTimeout(function () {
                if (toast.parentNode === container) {
                    container.removeChild(toast);
                }
            }, timeout);
        }
    }

    // Expose shared helpers for other pages
    global.initCommonUI = function () {
        initNav();
        initYear();
    };
    global.showSpinner = showSpinner;
    global.hideSpinner = hideSpinner;
    global.showToast = showToast;

    // Dummy AI prediction to simulate /predict backend response
    function simulatePredictApi(payload) {
        showSpinner();
        return new Promise(function (resolve) {
            setTimeout(function () {
                const text = (payload && payload.text) || '';
                const lowered = text.toLowerCase();
                const indicators = [];

                function hasWord(word) {
                    return lowered.indexOf(word) !== -1;
                }

                if (hasWord('kyc') || hasWord('account suspension') || hasWord('verification')) {
                    indicators.push('KYC / verification pressure');
                }
                if (hasWord('otp') || hasWord('one time password')) {
                    indicators.push('OTP harvesting attempt');
                }
                if (hasWord('click') || hasWord('tap')) {
                    indicators.push('Call-to-action clickbait');
                }
                if (hasWord('lottery') || hasWord('prize') || hasWord('winner')) {
                    indicators.push('Unsolicited reward / lottery');
                }
                if (hasWord('upi') || hasWord('imps') || hasWord('rtgs')) {
                    indicators.push('UPI / bank transfer request');
                }

                let baseScore = Math.min(95, Math.max(5, Math.round(text.length / 4)));
                if (indicators.length >= 3) {
                    baseScore = Math.max(baseScore, 80);
                } else if (indicators.length === 2) {
                    baseScore = Math.max(baseScore, 60);
                } else if (indicators.length === 1) {
                    baseScore = Math.max(baseScore, 45);
                }

                let level = 'Low';
                if (baseScore >= 75) level = 'High';
                else if (baseScore >= 45) level = 'Medium';

                const explanation =
                    level === 'High'
                        ? 'Multiple high‑risk patterns detected including urgency, suspicious links and requests for sensitive actions.'
                        : level === 'Medium'
                            ? 'Some scam‑like indicators found. Advise the user to independently verify using official channels.'
                            : 'Limited scam markers detected, but users should still avoid sharing OTPs, passwords or PINs.';

                const response = {
                    risk_level: level,
                    risk_score: baseScore,
                    explanation: explanation,
                    indicators: indicators,
                    type: payload.type,
                    created_at: new Date().toISOString(),
                };

                hideSpinner();
                resolve(response);
            }, 850);
        });
    }

    function handleScanSubmit(event) {
        event.preventDefault();
        const typeEl = $('scanType');
        const inputEl = $('scanInput');
        const typeError = $('scanTypeError');
        const inputError = $('scanInputError');
        const emptyState = $('scanResultEmpty');
        const resultCard = $('scanResult');
        const riskPill = $('riskPill');
        const riskLevelText = $('riskLevelText');
        const riskScoreEl = $('riskScore');
        const explanationEl = $('riskExplanation');
        const jsonPreview = $('scanJsonPreview');

        if (!typeEl || !inputEl || !typeError || !inputError) return;

        typeError.textContent = '';
        inputError.textContent = '';

        const type = typeEl.value;
        const text = inputEl.value.trim();
        let valid = true;

        if (!type) {
            typeError.textContent = 'Please choose what you are scanning.';
            valid = false;
        }
        if (!text) {
            inputError.textContent = 'Paste the suspicious message or URL you want to scan.';
            valid = false;
        } else if (text.length < 10) {
            inputError.textContent = 'Please provide a bit more context (at least 10 characters).';
            valid = false;
        }

        if (!valid) return;

        const payload = { type: type, text: text };

        simulatePredictApi(payload).then(function (res) {
            if (!riskPill || !riskLevelText || !riskScoreEl || !explanationEl || !jsonPreview) return;

            riskPill.classList.remove('low', 'medium', 'high');
            const levelClass = res.risk_level.toLowerCase();
            if (levelClass === 'low' || levelClass === 'medium' || levelClass === 'high') {
                riskPill.classList.add(levelClass);
            }

            riskLevelText.textContent = res.risk_level;
            riskScoreEl.textContent = res.risk_score;
            explanationEl.textContent = res.explanation;

            jsonPreview.textContent = JSON.stringify(res, null, 2);

            if (emptyState) emptyState.style.display = 'none';
            if (resultCard) resultCard.style.display = 'block';

            showToast({
                type: res.risk_level === 'High' ? 'error' : res.risk_level === 'Medium' ? 'info' : 'success',
                title: 'Scan complete',
                message: 'Risk level: ' + res.risk_level + ' (' + res.risk_score + '%)',
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const path = window.location.pathname.toLowerCase();
        const isScanPage = path.endsWith('scan.html');
        const isReportPage = path.endsWith('report.html');

        if ((isScanPage || isReportPage) && !isAuthenticated()) {
            const from = isScanPage ? 'scan' : 'report';
            window.location.href = 'login.html?from=' + encodeURIComponent(from);
            return;
        }

        global.initCommonUI();

        const scanForm = $('scan-form');
        if (scanForm) {
            scanForm.addEventListener('submit', handleScanSubmit);
        }
    });
})();

