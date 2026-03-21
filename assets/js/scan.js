// ScamShield scan & shared UI logic
// Handles: navigation toggle, year, loading spinner, toast notifications and the Scan page.
// Connected to real /api/predict backend endpoint.

(function () {
    const global = (window.ScamShield = window.ScamShield || {});

    // ── Backend base URL ──
    const API_BASE = window.SCAMSHIELD_API_BASE || 'http://127.0.0.1:8000';

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

    function getAuthToken() {
        try {
            return window.localStorage.getItem('scamshieldToken') || '';
        } catch (err) {
            return '';
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
    global.API_BASE = API_BASE;
    global.initCommonUI = function () {
        initNav();
        initYear();
    };
    global.showSpinner = showSpinner;
    global.hideSpinner = hideSpinner;
    global.showToast = showToast;
    global.getAuthToken = getAuthToken;

    // ── Real API call to /api/predict ──
    function callPredictApi(payload) {
        showSpinner();
        var token = getAuthToken();

        return fetch(API_BASE + '/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            },
            body: JSON.stringify(payload),
        })
            .then(function (res) {
                if (!res.ok) {
                    return res.text().then(function (text) {
                        console.error('API Error Response:', text);
                        try {
                            const err = JSON.parse(text);
                            throw new Error(err.detail || 'Prediction failed.');
                        } catch (e) {
                            throw new Error('Prediction failed. Status: ' + res.status);
                        }
                    });
                }
                return res.json();
            })
            .catch(function (error) {
                console.error('Fetch caught error:', error);
                throw error;
            })
            .finally(function () {
                hideSpinner();
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

        if (!typeEl || !inputEl || !typeError || !inputError) return;

        typeError.textContent = '';
        inputError.textContent = '';

        const rawType = typeEl.value;
        const text = inputEl.value.trim();
        let valid = true;

        if (!rawType) {
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
        
        // Map frontend dropdown value to backend regex requirement: ^(message|url|other)$
        let backendType = 'other';
        if (rawType.toLowerCase().includes('message')) backendType = 'message';
        if (rawType.toLowerCase().includes('url')) backendType = 'url';

        const payload = { type: backendType, text: text };

        callPredictApi(payload)
            .then(function (res) {
                if (!riskPill || !riskLevelText || !riskScoreEl || !explanationEl) return;

                riskPill.classList.remove('low', 'medium', 'high');
                const levelClass = res.risk_level.toLowerCase();
                if (levelClass === 'low' || levelClass === 'medium' || levelClass === 'high') {
                    riskPill.classList.add(levelClass);
                }

                riskLevelText.textContent = res.risk_level;
                riskScoreEl.textContent = res.risk_score;
                explanationEl.textContent = res.explanation;

                // ── Render Gemini precaution advice ──
                var precautionPanel = $('precautionPanel');
                var precautionList  = $('precautionList');
                if (precautionPanel && precautionList && res.precaution) {
                    precautionList.innerHTML = '';
                    // Gemini returns a numbered list; split by newlines and strip leading numbers
                    var lines = res.precaution.split('\n').filter(function(l) { return l.trim(); });
                    lines.forEach(function (line) {
                        // Strip leading "1. ", "2. " etc.
                        var clean = line.replace(/^\s*\d+\.\s*/, '').trim();
                        if (clean) {
                            var li = document.createElement('li');
                            li.textContent = clean;
                            precautionList.appendChild(li);
                        }
                    });
                    precautionPanel.style.display = 'block';
                } else if (precautionPanel) {
                    precautionPanel.style.display = 'none';
                }

                if (emptyState) emptyState.style.display = 'none';
                if (resultCard) resultCard.style.display = 'block';

                showToast({
                    type: res.risk_level === 'High' ? 'error' : res.risk_level === 'Medium' ? 'info' : 'success',
                    title: 'Scan complete',
                    message: 'Risk level: ' + res.risk_level + ' (' + res.risk_score + '%)',
                });
            })
            .catch(function (err) {
                showToast({
                    type: 'error',
                    title: 'Scan failed',
                    message: err.message || 'Could not reach backend. Is the server running?',
                });
            });
    }

    document.addEventListener('DOMContentLoaded', function () {
        global.initCommonUI();

        const scanForm = $('scan-form');
        if (scanForm) {
            scanForm.addEventListener('submit', handleScanSubmit);
        }
    });
})();
