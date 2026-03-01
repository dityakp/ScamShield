// ScamShield dashboard logic
// Handles: navigation, year, spinner & toast + populating dummy scan/report history and logout flow.

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

    global.initCommonUI = function () {
        initNav();
        initYear();
    };
    global.showSpinner = showSpinner;
    global.hideSpinner = hideSpinner;
    global.showToast = showToast;

    function loadUser() {
        try {
            const raw = window.localStorage.getItem('scamshieldUser');
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (err) {
            return null;
        }
    }

    function populateHeaderUser() {
        const user = loadUser();
        const nameEl = $('dashboardUserName');
        if (!nameEl) return;
        if (user && (user.name || user.email)) {
            nameEl.textContent = user.name || user.email;
        } else {
            nameEl.textContent = 'Analyst';
        }
    }

    function populateScanHistory() {
        const tbody = $('scanHistoryBody');
        if (!tbody) return;

        const dummyScans = [
            {
                date: '2026-03-01 10:32',
                type: 'SMS',
                snippet: 'Your bank account will be suspended in 24 hours...',
                risk: 'High',
                score: 87,
            },
            {
                date: '2026-02-28 21:10',
                type: 'Email',
                snippet: 'You have won a lottery worth ₹50,00,000...',
                risk: 'High',
                score: 91,
            },
            {
                date: '2026-02-27 16:45',
                type: 'URL',
                snippet: 'https://kyc-update-secure-payments.com',
                risk: 'Medium',
                score: 68,
            },
            {
                date: '2026-02-26 09:12',
                type: 'WhatsApp',
                snippet: 'Hi sir, I am from customer support. Please share OTP...',
                risk: 'High',
                score: 94,
            },
            {
                date: '2026-02-25 18:03',
                type: 'URL',
                snippet: 'https://official-bank.example.com',
                risk: 'Low',
                score: 18,
            },
        ];

        tbody.innerHTML = '';
        dummyScans.forEach(function (scan) {
            const tr = document.createElement('tr');

            const tdDate = document.createElement('td');
            tdDate.textContent = scan.date;

            const tdType = document.createElement('td');
            tdType.textContent = scan.type;

            const tdSnippet = document.createElement('td');
            tdSnippet.textContent = scan.snippet;

            const tdRisk = document.createElement('td');
            const tag = document.createElement('span');
            tag.className =
                'tag ' +
                (scan.risk === 'High' ? 'tag-high' : scan.risk === 'Medium' ? 'tag-medium' : 'tag-low');
            tag.textContent = scan.risk;
            tdRisk.appendChild(tag);

            const tdScore = document.createElement('td');
            tdScore.textContent = scan.score + '%';

            tr.appendChild(tdDate);
            tr.appendChild(tdType);
            tr.appendChild(tdSnippet);
            tr.appendChild(tdRisk);
            tr.appendChild(tdScore);
            tbody.appendChild(tr);
        });

        // Placeholder: replace dummyScans with data from /history
        // fetch('/history')
        //   .then(res => res.json())
        //   .then(scans => { ... });
    }

    function populateReportHistory() {
        const list = $('reportHistoryList');
        if (!list) return;

        const dummyReports = [
            {
                type: 'Phishing (Bank / UPI / KYC)',
                channel: 'SMS',
                when: 'Today · 10:20',
            },
            {
                type: 'Investment / trading scam',
                channel: 'Telegram',
                when: 'Yesterday · 19:05',
            },
            {
                type: 'Fake customer support',
                channel: 'Phone call',
                when: '2 days ago · 14:33',
            },
        ];

        list.innerHTML = '';
        dummyReports.forEach(function (report) {
            const item = document.createElement('div');
            item.className = 'history-item';

            const meta = document.createElement('div');
            meta.className = 'history-meta';
            const title = document.createElement('div');
            title.textContent = report.type;
            const channel = document.createElement('span');
            channel.textContent = 'Channel: ' + report.channel;
            meta.appendChild(title);
            meta.appendChild(channel);

            const time = document.createElement('div');
            time.className = 'history-time';
            time.textContent = report.when;

            item.appendChild(meta);
            item.appendChild(time);
            list.appendChild(item);
        });

        // Placeholder: replace dummyReports with data from /report or /history
        // fetch('/report')
        //   .then(res => res.json())
        //   .then(reports => { ... });
    }

    function setupLogout() {
        const logoutBtn = $('logoutButton');
        if (!logoutBtn) return;

        logoutBtn.addEventListener('click', function () {
            showSpinner();

            // Placeholder: call /logout backend if needed
            // fetch('/logout', { method: 'POST' }).then(...)

            setTimeout(function () {
                hideSpinner();
                try {
                    window.localStorage.removeItem('scamshieldUser');
                } catch (err) {
                    // Ignore storage errors in demo
                }

                showToast({
                    type: 'info',
                    title: 'Logged out (demo)',
                    message: 'You have been signed out of the dashboard.',
                });

                setTimeout(function () {
                    window.location.href = 'login.html';
                }, 800);
            }, 700);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const path = window.location.pathname.toLowerCase();
        if (path.endsWith('dashboard.html') && !isAuthenticated()) {
            window.location.href = 'login.html?from=' + encodeURIComponent('dashboard');
            return;
        }

        global.initCommonUI();
        populateHeaderUser();
        populateScanHistory();
        populateReportHistory();
        setupLogout();
    });
})();

