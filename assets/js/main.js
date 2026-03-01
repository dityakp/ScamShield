/* ─── CUSTOM CURSOR ──────────────────────────── */
const cursor = document.getElementById('cursor');
const cursorRing = document.getElementById('cursor-ring');
let cx = 0, cy = 0, ringX = 0, ringY = 0;

document.addEventListener('mousemove', e => {
  cx = e.clientX; cy = e.clientY;
  cursor.style.left = cx + 'px';
  cursor.style.top = cy + 'px';
});

function lerpCursor() {
  ringX += (cx - ringX) * 0.12;
  ringY += (cy - ringY) * 0.12;
  cursorRing.style.left = ringX + 'px';
  cursorRing.style.top = ringY + 'px';
  requestAnimationFrame(lerpCursor);
}
lerpCursor();

document.querySelectorAll('a, button, .scan-opt, .feature-item, .testi-card, .contact-info-item').forEach(el => {
  el.addEventListener('mouseenter', () => {
    cursor.style.width = '20px';
    cursor.style.height = '20px';
    cursor.style.background = 'rgba(0,229,255,0.5)';
    cursorRing.style.width = '60px';
    cursorRing.style.height = '60px';
    cursorRing.style.borderColor = 'rgba(0,229,255,0.6)';
  });
  el.addEventListener('mouseleave', () => {
    cursor.style.width = '12px';
    cursor.style.height = '12px';
    cursor.style.background = 'var(--accent)';
    cursorRing.style.width = '40px';
    cursorRing.style.height = '40px';
    cursorRing.style.borderColor = 'rgba(0,229,255,0.4)';
  });
});

/* ─── PARTICLE CANVAS ────────────────────────── */
const canvas = document.getElementById('bgCanvas');
const ctx = canvas.getContext('2d');
let W, H, particles = [];

function resize() {
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}

function initParticles() {
  particles = [];
  const count = Math.floor((W * H) / 14000);
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.2 + 0.3,
      dx: (Math.random() - 0.5) * 0.25,
      dy: (Math.random() - 0.5) * 0.25,
      alpha: Math.random() * 0.4 + 0.05,
      pulse: Math.random() * Math.PI * 2
    });
  }
}

function drawParticles() {
  ctx.clearRect(0, 0, W, H);
  const t = Date.now() * 0.001;

  particles.forEach((p, i) => {
    p.pulse += 0.01;
    const a = p.alpha * (0.7 + 0.3 * Math.sin(p.pulse));
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0,229,255,${a})`;
    ctx.fill();
    p.x += p.dx;
    p.y += p.dy;
    if (p.x < 0 || p.x > W) p.dx *= -1;
    if (p.y < 0 || p.y > H) p.dy *= -1;

    // connections
    for (let j = i + 1; j < particles.length; j++) {
      const b = particles[j];
      const d = Math.hypot(p.x - b.x, p.y - b.y);
      if (d < 100) {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(b.x, b.y);
        ctx.strokeStyle = `rgba(0,229,255,${0.05 * (1 - d/100)})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    }
  });

  requestAnimationFrame(drawParticles);
}

resize();
initParticles();
drawParticles();
window.addEventListener('resize', () => { resize(); initParticles(); });

/* ─── HEX RAIN ───────────────────────────────── */
const hexRain = document.getElementById('hexRain');
const chars = '01ABCDEFx0f9e3d2c8b7a'.split('');

function createHexCols() {
  const cols = Math.floor(window.innerWidth / 80);
  for (let i = 0; i < cols; i++) {
    const col = document.createElement('div');
    col.className = 'hex-col';
    col.style.left = (i * 80 + Math.random() * 40) + 'px';
    const duration = 8 + Math.random() * 12;
    col.style.animationDuration = duration + 's';
    col.style.animationDelay = (-Math.random() * duration) + 's';
    let txt = '';
    for (let j = 0; j < 20; j++) txt += chars[Math.floor(Math.random() * chars.length)] + '\n';
    col.textContent = txt;
    hexRain.appendChild(col);
  }
}
createHexCols();

/* ─── FLOATING HERO DATA ─────────────────────── */
const floaterData = [
  'SCAM DETECTED', 'PHISHING LINK', 'RISK: HIGH', '⚠ WARNING',
  'VERIFIED SAFE', 'ANALYZING...', 'PATTERN MATCH', 'THREAT: NULL',
  'SECURE', 'BLOCK SENDER', 'AI SCANNING'
];

const heroFloaters = document.getElementById('heroFloaters');
for (let i = 0; i < 8; i++) {
  const f = document.createElement('div');
  f.className = 'floater';
  f.textContent = floaterData[Math.floor(Math.random() * floaterData.length)];
  f.style.left = (Math.random() * 100) + '%';
  const delay = Math.random() * 12;
  f.style.animationDelay = delay + 's';
  f.style.animationDuration = (10 + Math.random() * 8) + 's';
  heroFloaters.appendChild(f);
}

/* ─── SCROLL REVEAL ──────────────────────────── */
const observer = new IntersectionObserver(entries => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      setTimeout(() => e.target.classList.add('visible'), i * 60);
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

/* ─── COUNT UP ANIMATION ─────────────────────── */
const countObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const el = e.target;
      const target = parseFloat(el.dataset.target);
      const suffix = el.dataset.suffix || '';
      if (!target) return;
      let start = 0;
      const duration = 2000;
      const startTime = performance.now();
      function update(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const val = start + (target - start) * ease;
        el.textContent = Number.isInteger(target) ? Math.floor(val) + suffix : val.toFixed(1) + suffix;
        if (progress < 1) requestAnimationFrame(update);
        else el.textContent = target + suffix;
      }
      requestAnimationFrame(update);
      countObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stat-val[data-target]').forEach(el => countObserver.observe(el));

/* ─── CHAR COUNT ─────────────────────────────── */
const inputText = document.getElementById('inputText');
inputText.addEventListener('input', () => {
  const l = inputText.value.length;
  document.getElementById('charCount').textContent = l + ' char' + (l !== 1 ? 's' : '');
});

/* ─── SCAN TYPE ──────────────────────────────── */
function setType(el, type) {
  document.querySelectorAll('.scan-opt').forEach(o => o.classList.remove('active'));
  el.classList.add('active');
}

/* ─── CLEAR ──────────────────────────────────── */
function clearInput() {
  inputText.value = '';
  document.getElementById('charCount').textContent = '0 chars';
  const r = document.getElementById('result');
  r.className = 'hidden';
  inputText.focus();
}

/* ─── SCAN ───────────────────────────────────── */
async function checkScam() {
  const text = inputText.value.trim();
  if (!text) {
    inputText.style.borderColor = 'rgba(255,51,85,0.5)';
    inputText.style.boxShadow = '0 0 0 4px rgba(255,51,85,0.08)';
    inputText.focus();
    setTimeout(() => {
      inputText.style.borderColor = '';
      inputText.style.boxShadow = '';
    }, 1500);
    return;
  }

  const btn = document.getElementById('scanBtn');
  const def = document.getElementById('btnDefault');
  const load = document.getElementById('btnLoading');
  const beam = document.getElementById('scannerBeam');

  btn.classList.add('loading');
  def.style.display = 'none';
  load.style.display = 'flex';
  beam.classList.add('active');
  document.getElementById('result').className = 'hidden';

  try {
    const res = await fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    showResult(data.risk_level, data.probability);
  } catch (e) {
    showResult('demo', '—');
  } finally {
    btn.classList.remove('loading');
    def.style.display = 'flex';
    load.style.display = 'none';
    beam.classList.remove('active');
  }
}

function showResult(risk, prob) {
  const el = document.getElementById('result');
  const level = (risk || '').toLowerCase();
  el.className = ['high','medium','low'].includes(level) ? level : 'demo';

  const configs = {
    high: {
      emoji: '🚨', name: 'HIGH RISK', chip: 'DANGER',
      bar: '90%',
      desc: 'This content contains strong scam indicators. Do <strong>NOT</strong> click any links, share personal or financial information, or follow any instructions given.',
      tip: '⚠️ Tip: Legitimate organisations never ask for OTPs, passwords, or urgent payments via message. Block and report the sender immediately.'
    },
    medium: {
      emoji: '⚠️', name: 'MEDIUM RISK', chip: 'CAUTION',
      bar: '55%',
      desc: 'Some suspicious patterns detected. Proceed with caution. Verify the sender through official channels before taking any action.',
      tip: '💡 Tip: Search the company name + "scam" online, or call the official number from their real website — never the number given in the message.'
    },
    low: {
      emoji: '✅', name: 'LOW RISK', chip: 'SAFE',
      bar: '12%',
      desc: 'No major scam indicators were found. This content appears to be safe. However, always stay vigilant — no tool is 100% foolproof.',
      tip: '💡 Tip: Even safe-looking links can lead to phishing pages. Always check the URL bar before entering any credentials.'
    },
    demo: {
      emoji: '🔌', name: 'BACKEND OFFLINE', chip: 'DEMO MODE',
      bar: '50%',
      desc: 'Could not connect to <code>localhost:8000</code>. Your Python Flask backend is not running. Start it with <code>python app.py</code> and try again.',
      tip: '⚙️ Once the backend is running, real AI predictions will appear here instead of this demo message.'
    }
  };

  const c = configs[level] || configs.demo;
  document.getElementById('rEmoji').textContent = c.emoji;
  document.getElementById('rName').textContent = c.name;
  document.getElementById('rChip').textContent = c.chip;
  document.getElementById('rDesc').innerHTML = c.desc;
  document.getElementById('rTip').textContent = c.tip;
  document.getElementById('rProb').textContent = prob !== '—' ? `Probability Score: ${prob}` : '';

  const bar = document.getElementById('rBar');
  bar.style.width = '0%';
  el.classList.remove('hidden');
  setTimeout(() => { bar.style.width = c.bar; }, 100);
}

/* ─── CONTACT FORM ───────────────────────────── */
function submitContact(btn) {
  const orig = btn.textContent;
  btn.textContent = 'MESSAGE SENT ✓';
  btn.style.background = 'var(--safe)';
  btn.style.color = 'var(--bg)';
  setTimeout(() => {
    btn.textContent = orig;
    btn.style.background = '';
    btn.style.color = '';
  }, 3000);
}

/* ─── KEYBOARD ───────────────────────────────── */
inputText.addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'Enter') checkScam();
});

/* ─── MOUSE PARALLAX ORBS ────────────────────── */
document.addEventListener('mousemove', e => {
  const xFrac = (e.clientX / window.innerWidth - 0.5);
  const yFrac = (e.clientY / window.innerHeight - 0.5);
  const orbs = document.querySelectorAll('.orb');
  orbs[0].style.transform = `translate(${xFrac * 30}px, ${yFrac * 30}px)`;
  orbs[1].style.transform = `translate(${-xFrac * 20}px, ${-yFrac * 20}px)`;
  orbs[2].style.transform = `translate(${xFrac * 10}px, ${yFrac * 10}px) translate(-50%, -50%)`;
});
