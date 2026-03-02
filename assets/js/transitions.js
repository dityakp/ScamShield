/**
 * ScamShield – Professional Curtain Transition System
 *
 * How it works:
 *  EXIT  (link click): A full-screen branded curtain sweeps DOWN to cover the
 *         current page. The ScamShield logo blooms in the centre with a glowing
 *         pulse and a neon progress bar animates along the bottom. After the
 *         curtain fully covers the screen, the browser navigates.
 *
 *  ENTER (new page load): If the transition flag is set in sessionStorage the
 *         curtain starts in the fully-covering position, then sweeps UP to
 *         reveal the fresh page beneath it.
 */

(function () {
    'use strict';

    /* ── Timing constants (ms) ──────────────────────────────────────── */
    var EXIT_COVER_MS = 600;  // curtain sweeps down
    var EXIT_HOLD_MS = 500;   // brand visible just long enough to register
    var ENTER_DELAY_MS = 80;  // brief pause before curtain sweeps up on new page

    /* ── Build curtain DOM ──────────────────────────────────────────── */
    var curtain = document.createElement('div');
    curtain.className = 'ss-curtain';
    curtain.setAttribute('aria-hidden', 'true');
    curtain.innerHTML =
        '<div class="ss-curtain-brand">' +
        '<div class="ss-curtain-mark"></div>' +
        '<div>' +
        '<div class="ss-curtain-name">ScamShield</div>' +
        '<span class="ss-curtain-sub">AI scam firewall</span>' +
        '</div>' +
        '</div>' +
        '<div class="ss-curtain-bar"></div>';

    document.body.appendChild(curtain);

    /* ── Determine enter vs idle state ─────────────────────────────── */
    if (sessionStorage.getItem('ss-in-transition') === '1') {
        sessionStorage.removeItem('ss-in-transition');

        /* Start with curtain visible (came from an exit transition) */
        curtain.style.transform = 'translateY(0)';

        /* Small delay lets the browser paint the page before revealing */
        setTimeout(function () {
            curtain.classList.add('enter-phase');
        }, ENTER_DELAY_MS);
    }

    /* ── Navigate with curtain ──────────────────────────────────────── */
    function navigateTo(href) {
        /* Prevent double-firing */
        if (curtain.classList.contains('exit-phase')) return;

        /* Mark next page to start covered */
        sessionStorage.setItem('ss-in-transition', '1');

        /* Trigger exit animation */
        curtain.classList.add('exit-phase');
        curtain.style.pointerEvents = 'all'; /* block clicks during transition */

        /* Navigate once curtain has fully covered + brand has shown */
        setTimeout(function () {
            window.location.href = href;
        }, EXIT_COVER_MS + EXIT_HOLD_MS);
    }

    /* ── Intercept internal anchor clicks ───────────────────────────── */
    document.addEventListener('click', function (e) {
        var anchor = e.target.closest('a[href]');
        if (!anchor) return;

        var href = anchor.getAttribute('href');

        /* Skip external, hash, protocol, and blank-target links */
        if (
            !href ||
            href === '#' ||
            href.indexOf('#') === 0 ||
            href.indexOf('http') === 0 ||
            href.indexOf('//') === 0 ||
            href.indexOf('mailto:') === 0 ||
            href.indexOf('tel:') === 0 ||
            href.indexOf('javascript:') === 0 ||
            anchor.target === '_blank'
        ) return;

        e.preventDefault();
        navigateTo(href);
    });

    /* ── Also intercept browser Back/Forward (popstate) ─────────────── */
    window.addEventListener('popstate', function () {
        curtain.classList.remove('exit-phase', 'enter-phase');
        curtain.style.transform = 'translateY(0)';
        setTimeout(function () {
            curtain.classList.add('enter-phase');
        }, 20);
    });

})();
