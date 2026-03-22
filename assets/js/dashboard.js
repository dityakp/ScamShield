// ScamShield dashboard logic
// Handles: navigation, year, spinner & toast + fetching real scan/report history and logout flow.
// Connected to real /api/history, /api/report, and /api/logout backend endpoints.

(function () {
    const global = (window.ScamShield = window.ScamShield || {});

    // ── Backend base URL ──
    const API_BASE = window.SCAMSHIELD_API_BASE || '';

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

    global.API_BASE = API_BASE;
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

        var token = getAuthToken();

        fetch(API_BASE + '/api/history', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token,
            },
        })
            .then(function (res) {
                if (!res.ok) throw new Error('Failed to load scan history.');
                return res.json();
            })
            .then(function (scans) {
                tbody.innerHTML = '';

                if (scans.length === 0) {
                    var tr = document.createElement('tr');
                    var td = document.createElement('td');
                    td.colSpan = 5;
                    td.textContent = 'No scans yet. Go to the Scan page to analyze a message.';
                    td.style.textAlign = 'center';
                    td.style.opacity = '0.6';
                    tr.appendChild(td);
                    tbody.appendChild(tr);
                    return;
                }

                scans.forEach(function (scan) {
                    var tr = document.createElement('tr');

                    var tdDate = document.createElement('td');
                    tdDate.textContent = scan.date;

                    var tdType = document.createElement('td');
                    tdType.textContent = scan.type;

                    var tdSnippet = document.createElement('td');
                    tdSnippet.textContent = scan.snippet;

                    var tdRisk = document.createElement('td');
                    var tag = document.createElement('span');
                    tag.className =
                        'tag ' +
                        (scan.risk === 'High' ? 'tag-high' : scan.risk === 'Medium' ? 'tag-medium' : 'tag-low');
                    tag.textContent = scan.risk;
                    tdRisk.appendChild(tag);

                    var tdScore = document.createElement('td');
                    tdScore.textContent = scan.score + '%';

                    tr.appendChild(tdDate);
                    tr.appendChild(tdType);
                    tr.appendChild(tdSnippet);
                    tr.appendChild(tdRisk);
                    tr.appendChild(tdScore);
                    tbody.appendChild(tr);
                });
            })
            .catch(function (err) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;opacity:0.6">Could not load scan history.</td></tr>';
            });
    }

    function populateReportHistory() {
        const list = $('reportHistoryList');
        if (!list) return;

        var token = getAuthToken();

        fetch(API_BASE + '/api/report', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token,
            },
        })
            .then(function (res) {
                if (!res.ok) throw new Error('Failed to load report history.');
                return res.json();
            })
            .then(function (reports) {
                list.innerHTML = '';

                if (reports.length === 0) {
                    var empty = document.createElement('div');
                    empty.style.textAlign = 'center';
                    empty.style.opacity = '0.6';
                    empty.style.padding = '1rem';
                    empty.textContent = 'No reports yet. Help the community by reporting scams.';
                    list.appendChild(empty);
                    return;
                }

                reports.forEach(function (report) {
                    var item = document.createElement('div');
                    item.className = 'history-item';

                    var meta = document.createElement('div');
                    meta.className = 'history-meta';
                    var title = document.createElement('div');
                    title.textContent = report.type;
                    var channel = document.createElement('span');
                    channel.textContent = 'Channel: ' + report.channel;
                    meta.appendChild(title);
                    meta.appendChild(channel);

                    var time = document.createElement('div');
                    time.className = 'history-time';
                    time.textContent = report.when;

                    item.appendChild(meta);
                    item.appendChild(time);
                    list.appendChild(item);
                });
            })
            .catch(function (err) {
                list.innerHTML = '<div style="text-align:center;opacity:0.6;padding:1rem">Could not load report history.</div>';
            });
    }

    function setupLogout() {
        const logoutBtn = $('logoutButton');
        if (!logoutBtn) return;

        logoutBtn.addEventListener('click', function () {
            showSpinner();
            var token = getAuthToken();

            fetch(API_BASE + '/api/logout', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + token,
                },
            })
                .then(function () {
                    // Always clear local state regardless of response
                })
                .catch(function () {
                    // Continue with logout even on error
                })
                .finally(function () {
                    hideSpinner();
                    try {
                        window.localStorage.removeItem('scamshieldUser');
                        window.localStorage.removeItem('scamshieldToken');
                    } catch (err) {
                        // Ignore storage errors
                    }

                    showToast({
                        type: 'info',
                        title: 'Logged out',
                        message: 'You have been signed out of the dashboard.',
                    });

                    setTimeout(function () {
                        window.location.href = 'login.html';
                    }, 800);
                });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        global.initCommonUI();
        populateHeaderUser();
        populateScanHistory();
        populateReportHistory();
        setupLogout();
    });
})();
