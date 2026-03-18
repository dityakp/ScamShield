// ScamShield Auth Guard
// Include this script as the FIRST script on any protected page (scan, report, dashboard).
// If user is not logged in, page content is hidden and a centered modal is shown.

(function () {
    function isAuthenticated() {
        try {
            return !!window.localStorage.getItem('scamshieldUser');
        } catch (e) {
            return false;
        }
    }

    function showAuthModal(pageName) {
        // Blurs & hides everything behind the modal
        var style = document.createElement('style');
        style.textContent =
            'body > *:not(#ss-auth-overlay) { filter: blur(6px) brightness(0.35); pointer-events: none; user-select: none; }' +
            '#ss-auth-overlay { position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.72);backdrop-filter:blur(3px);padding:1.5rem; }' +
            '#ss-auth-modal { background:rgba(0,8,30,0.97);border:1px solid rgba(0,183,255,0.4);border-radius:22px;padding:2.5rem 2.2rem;max-width:420px;width:100%;box-shadow:0 0 60px rgba(0,183,255,0.18),0 30px 80px rgba(0,0,0,0.85);text-align:center;animation:ssGrd .35s cubic-bezier(.22,1,.36,1) both; }' +
            '@keyframes ssGrd{from{opacity:0;transform:scale(.88) translateY(-20px)}to{opacity:1;transform:scale(1) translateY(0)}}' +
            '#ss-auth-modal .ss-modal-icon{width:64px;height:64px;border-radius:50%;background:rgba(0,183,255,0.1);border:1px solid rgba(0,183,255,0.35);display:flex;align-items:center;justify-content:center;margin:0 auto 1.2rem;font-size:1.8rem;box-shadow:0 0 30px rgba(0,183,255,0.2);}' +
            '#ss-auth-modal h2{margin:0 0 .5rem;font-size:1.35rem;font-weight:800;color:#fff;letter-spacing:-.02em;}' +
            '#ss-auth-modal p{margin:0 0 1.8rem;font-size:.9rem;color:rgba(226,232,240,.6);line-height:1.6;}' +
            '#ss-auth-modal .ss-modal-btns{display:flex;flex-direction:column;gap:.75rem;}' +
            '#ss-auth-modal .ss-btn-login{display:block;padding:.7rem 1.5rem;border-radius:999px;background:linear-gradient(135deg,#0ea5e9,#00d4ff);color:#000;font-weight:700;font-size:.95rem;border:none;cursor:pointer;text-decoration:none;box-shadow:0 0 0 1px rgba(0,183,255,.35),0 6px 28px rgba(0,183,255,.5);transition:transform .18s ease,box-shadow .18s ease;}' +
            '#ss-auth-modal .ss-btn-login:hover{transform:translateY(-2px) scale(1.02);box-shadow:0 0 0 1px rgba(0,183,255,.7),0 10px 40px rgba(0,183,255,.75);}' +
            '#ss-auth-modal .ss-btn-reg{display:block;padding:.65rem 1.5rem;border-radius:999px;border:1px solid rgba(0,183,255,.4);color:#00d4ff;font-size:.9rem;font-weight:600;cursor:pointer;text-decoration:none;background:transparent;transition:border-color .18s,background .18s,color .18s;}' +
            '#ss-auth-modal .ss-btn-reg:hover{border-color:rgba(0,183,255,.8);background:rgba(0,183,255,.08);color:#fff;}' +
            '#ss-auth-modal .ss-kicker{font-size:.68rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#00d4ff;margin-bottom:.65rem;display:flex;align-items:center;justify-content:center;gap:.4rem;}' +
            '#ss-auth-modal .ss-kicker::before{content:"";width:5px;height:5px;border-radius:50%;background:#00d4ff;box-shadow:0 0 8px #00d4ff;}';
        document.head.appendChild(style);

        var labels = {
            scan: 'the AI Scan tool',
            report: 'Report Scam',
            dashboard: 'your Dashboard'
        };
        var featureName = labels[pageName] || 'this page';

        var overlay = document.createElement('div');
        overlay.id = 'ss-auth-overlay';

        overlay.innerHTML =
            '<div id="ss-auth-modal">' +
                '<div class="ss-kicker"><span>Access Restricted</span></div>' +
                '<div class="ss-modal-icon">🔒</div>' +
                '<h2>You\'re not logged in</h2>' +
                '<p>You need to <strong>register or login</strong> to access ' + featureName + '. Join ScamShield to start protecting yourself from scams.</p>' +
                '<div class="ss-modal-btns">' +
                    '<a class="ss-btn-login" href="login.html?from=' + encodeURIComponent(pageName) + '">Login to your account</a>' +
                    '<a class="ss-btn-reg" href="register.html">Create a free account</a>' +
                '</div>' +
            '</div>';

        document.body.appendChild(overlay);
    }

    // Run as soon as DOM is ready — before any page JS initialises
    document.addEventListener('DOMContentLoaded', function () {
        if (isAuthenticated()) return; // Logged in — let the page load normally

        var path = window.location.pathname.toLowerCase();
        var pageName = 'page';
        if (path.endsWith('scan.html'))      pageName = 'scan';
        else if (path.endsWith('report.html'))  pageName = 'report';
        else if (path.endsWith('dashboard.html')) pageName = 'dashboard';

        showAuthModal(pageName);

        // Stop all other scripts from running by preventing event propagation
        // (the modal makes the page inert via CSS pointer-events)
    }, true); // capture phase — fires before other DOMContentLoaded listeners
})();
