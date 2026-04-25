/**
 * ScamShield – matrix.js
 * Shared: matrix rain canvas + navbar scroll shrink + mobile nav toggle
 * Include on EVERY page right before </body>
 */
(function () {
    'use strict';

    /* ── Matrix rain ─────────────────────────────────── */
    var canvas = document.createElement('canvas');
    canvas.id = 'matrix-bg';
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.cssText = [
        'position:fixed', 'inset:0', 'z-index:0',
        'pointer-events:none', 'opacity:0.22'
    ].join(';');
    document.body.insertBefore(canvas, document.body.firstChild);

    var ctx = canvas.getContext('2d');
    var W, H, cols, drops;
    var FS = 13;
    var CHARS = '01アイウエオカキクケコサシスセソタチツテトナニヌネABCDEFGHIJKL0123456789@#%><';

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
        cols = Math.floor(W / FS);
        drops = Array(cols).fill(1);
    }
    window.addEventListener('resize', resize, { passive: true });
    resize();

    function drawMatrix() {
        ctx.fillStyle = 'rgba(0,0,0,0.055)';
        ctx.fillRect(0, 0, W, H);
        ctx.font = FS + 'px "Courier New",monospace';

        for (var i = 0; i < drops.length; i++) {
            var ch = CHARS[Math.floor(Math.random() * CHARS.length)];
            /* white head, neon blue trail */
            ctx.fillStyle = drops[i] * FS < 90
                ? 'rgba(220,240,255,0.95)'
                : 'rgba(0,183,255,0.5)';
            ctx.fillText(ch, i * FS, drops[i] * FS);
            if (drops[i] * FS > H && Math.random() > 0.974) drops[i] = 0;
            drops[i]++;
        }
    }
    setInterval(drawMatrix, 48);

    /* ── Navbar scroll shrink ────────────────────────── */
    var nb = document.querySelector('.navbar');
    if (nb) {
        window.addEventListener('scroll', function () {
            nb.classList.toggle('scrolled', window.scrollY > 45);
        }, { passive: true });
    }

    /* ── Mobile nav toggle ───────────────────────────── */
    var toggler = document.getElementById('nav-toggle');
    var menu = document.getElementById('nav-menu');
    if (toggler && menu) {
        toggler.addEventListener('click', function () {
            menu.classList.toggle('open');
        });
    }

})();
