/**
 * ScamShield Admin Panel – admin.js
 * Handles authentication guard, data loading, and all admin actions.
 */

const API = window.SCAMSHIELD_API_BASE || 'http://127.0.0.1:8000';

// ── Auth Guard ───────────────────────────────────────────────────────────────
const adminToken = localStorage.getItem('adminToken');
const adminUser  = (() => {
  try { return JSON.parse(localStorage.getItem('adminUser') || '{}'); }
  catch { return {}; }
})();

if (!adminToken) {
  window.location.href = 'admin-login.html';
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function authHeaders() {
  return { 'Authorization': `Bearer ${adminToken}`, 'Content-Type': 'application/json' };
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, { ...options, headers: { ...authHeaders(), ...(options.headers || {}) } });
  if (res.status === 401 || res.status === 403) {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    window.location.href = 'admin-login.html';
    return null;
  }
  return res;
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) +
    ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function riskBadge(level) {
  const map = { High: '#f87171', Medium: '#fbbf24', Low: '#34d399' };
  const bg = map[level] || '#94a3b8';
  return `<span style="background:${bg}22;color:${bg};border:1px solid ${bg}44;
    padding:.18rem .55rem;border-radius:999px;font-size:.7rem;font-weight:700;
    font-family:'Courier New',monospace;letter-spacing:.06em;">${level}</span>`;
}

function pill(text, color) {
  return `<span style="background:${color}22;color:${color};border:1px solid ${color}44;
    padding:.15rem .5rem;border-radius:999px;font-size:.68rem;font-weight:600;
    font-family:'Courier New',monospace;">${text}</span>`;
}

function showToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = 'adm-toast';
  t.style.cssText = `
    position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;
    background:${type === 'error' ? 'rgba(248,113,113,.15)' : 'rgba(52,211,153,.15)'};
    border:1px solid ${type === 'error' ? 'rgba(248,113,113,.4)' : 'rgba(52,211,153,.4)'};
    color:${type === 'error' ? '#f87171' : '#34d399'};
    padding:.75rem 1.25rem;border-radius:10px;font-size:.85rem;font-weight:600;
    backdrop-filter:blur(12px);animation:toast-in .25s ease;max-width:320px;`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function confirm_action(msg) {
  return window.confirm(msg);
}

// ── Tab Switching ─────────────────────────────────────────────────────────────
function switchTab(tabId) {
  document.querySelectorAll('.adm-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.adm-tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
  const pane = document.getElementById(`tab-${tabId}`);
  if (pane) pane.classList.add('active');

  const loaders = { stats: loadStats, users: loadUsers, scans: loadScans, reports: loadReports };
  if (loaders[tabId]) loaders[tabId]();
}

// ── Overview / Stats ──────────────────────────────────────────────────────────
async function loadStats() {
  const pane = document.getElementById('tab-stats');
  pane.innerHTML = '<div class="adm-loading">Loading stats…</div>';

  try {
    const res = await apiFetch('/api/admin/stats');
    if (!res) return;
    const s = await res.json();

    pane.innerHTML = `
      <div class="adm-stats-grid">
        ${statCard('👥', 'Total Users', s.total_users, '#00d4ff', '+' + s.new_users_today + ' today')}
        ${statCard('🔍', 'Total Scans', s.total_scans, '#a78bfa', '+' + s.scans_today + ' today')}
        ${statCard('🚨', 'Scam Reports', s.total_reports, '#f59e0b', '+' + s.reports_today + ' today')}
        ${statCard('⚠️', 'High Risk Scans', s.high_risk_count, '#f87171', Math.round(s.high_risk_count / Math.max(s.total_scans, 1) * 100) + '% of all scans')}
        ${statCard('🟡', 'Medium Risk', s.medium_risk_count, '#fbbf24', '')}
        ${statCard('🟢', 'Low Risk', s.low_risk_count, '#34d399', '')}
      </div>

      <div class="adm-section-title">Risk Distribution</div>
      <div class="adm-risk-bar-wrap">
        <div class="adm-risk-bar">
          <div class="adm-risk-seg" style="width:${pct(s.high_risk_count, s.total_scans)}%;background:#f87171;" title="High Risk"></div>
          <div class="adm-risk-seg" style="width:${pct(s.medium_risk_count, s.total_scans)}%;background:#fbbf24;" title="Medium Risk"></div>
          <div class="adm-risk-seg" style="width:${pct(s.low_risk_count, s.total_scans)}%;background:#34d399;" title="Low Risk"></div>
        </div>
        <div class="adm-risk-legend">
          <span class="adm-leg-item"><span style="background:#f87171"></span> High (${s.high_risk_count})</span>
          <span class="adm-leg-item"><span style="background:#fbbf24"></span> Medium (${s.medium_risk_count})</span>
          <span class="adm-leg-item"><span style="background:#34d399"></span> Low (${s.low_risk_count})</span>
        </div>
      </div>`;
  } catch {
    pane.innerHTML = '<div class="adm-error-msg">Failed to load stats. Is the backend running?</div>';
  }
}

function pct(val, total) {
  return total ? Math.round(val / total * 100) : 0;
}

function statCard(icon, label, value, color, sub) {
  return `<div class="adm-stat-card" style="--c:${color}">
    <div class="adm-stat-icon">${icon}</div>
    <div class="adm-stat-val">${value.toLocaleString()}</div>
    <div class="adm-stat-lbl">${label}</div>
    ${sub ? `<div class="adm-stat-sub">${sub}</div>` : ''}
  </div>`;
}

// ── Users ─────────────────────────────────────────────────────────────────────
async function loadUsers() {
  const pane = document.getElementById('tab-users');
  pane.innerHTML = '<div class="adm-loading">Loading users…</div>';

  try {
    const res = await apiFetch('/api/admin/users');
    if (!res) return;
    const users  = await res.json();

    if (!users.length) {
      pane.innerHTML = '<div class="adm-empty">No users found.</div>';
      return;
    }

    pane.innerHTML = `
      <div class="adm-table-wrap">
        <table class="adm-table">
          <thead>
            <tr>
              <th>#</th><th>Name</th><th>Email</th><th>Joined</th>
              <th>Scans</th><th>Reports</th><th>Role</th><th>Status</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${users.map(u => `
              <tr id="user-row-${u.id}">
                <td class="adm-muted">${u.id}</td>
                <td>${u.name}</td>
                <td class="adm-email">${u.email}</td>
                <td class="adm-muted">${formatDate(u.created_at)}</td>
                <td>${u.scan_count}</td>
                <td>${u.report_count}</td>
                <td>${u.is_admin ? pill('Admin','#f59e0b') : pill('User','#94a3b8')}</td>
                <td>${u.is_active ? pill('Active','#34d399') : pill('Inactive','#f87171')}</td>
                <td>
                  <div class="adm-action-btns">
                    <button class="adm-act-btn adm-act-warning" onclick="toggleAdmin(${u.id})" title="Toggle admin">
                      ${u.is_admin ? '🔓 Revoke' : '🔑 Make Admin'}
                    </button>
                    <button class="adm-act-btn adm-act-danger" onclick="deleteUser(${u.id}, '${u.email}')" title="Delete user">
                      🗑 Delete
                    </button>
                  </div>
                </td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="adm-count">${users.length} user${users.length !== 1 ? 's' : ''} total</div>`;
  } catch {
    pane.innerHTML = '<div class="adm-error-msg">Failed to load users.</div>';
  }
}

async function deleteUser(id, email) {
  if (!confirm_action(`Delete user "${email}" and ALL their data? This cannot be undone.`)) return;
  try {
    const res = await apiFetch(`/api/admin/users/${id}`, { method: 'DELETE' });
    if (!res) return;
    if (res.ok) {
      document.getElementById(`user-row-${id}`)?.remove();
      showToast(`User ${email} deleted.`);
    } else {
      const e = await res.json();
      showToast(e.detail || 'Delete failed.', 'error');
    }
  } catch { showToast('Request failed.', 'error'); }
}

async function toggleAdmin(id) {
  try {
    const res = await apiFetch(`/api/admin/users/${id}/toggle-admin`, { method: 'PATCH' });
    if (!res) return;
    const data = await res.json();
    if (res.ok) { showToast(data.message); loadUsers(); }
    else showToast(data.detail || 'Failed.', 'error');
  } catch { showToast('Request failed.', 'error'); }
}

// ── Scans ─────────────────────────────────────────────────────────────────────
async function loadScans() {
  const pane = document.getElementById('tab-scans');
  pane.innerHTML = '<div class="adm-loading">Loading scans…</div>';

  try {
    const res = await apiFetch('/api/admin/scans?limit=200');
    if (!res) return;
    const scans = await res.json();

    if (!scans.length) {
      pane.innerHTML = '<div class="adm-empty">No scans found.</div>';
      return;
    }

    pane.innerHTML = `
      <div class="adm-table-wrap">
        <table class="adm-table">
          <thead>
            <tr><th>#</th><th>User</th><th>Type</th><th>Content (preview)</th><th>Risk</th><th>Score</th><th>Date</th></tr>
          </thead>
          <tbody>
            ${scans.map(s => `
              <tr>
                <td class="adm-muted">${s.id}</td>
                <td class="adm-email">${s.user_email}</td>
                <td>${pill(s.scan_type, '#a78bfa')}</td>
                <td class="adm-snippet">${escHtml(s.snippet)}</td>
                <td>${riskBadge(s.risk_level)}</td>
                <td>${s.risk_score}%</td>
                <td class="adm-muted">${formatDate(s.created_at)}</td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="adm-count">${scans.length} scan${scans.length !== 1 ? 's' : ''} (showing latest 200)</div>`;
  } catch {
    pane.innerHTML = '<div class="adm-error-msg">Failed to load scans.</div>';
  }
}

// ── Reports ───────────────────────────────────────────────────────────────────
async function loadReports() {
  const pane = document.getElementById('tab-reports');
  pane.innerHTML = '<div class="adm-loading">Loading reports…</div>';

  try {
    const res = await apiFetch('/api/admin/reports?limit=200');
    if (!res) return;
    const reports = await res.json();

    if (!reports.length) {
      pane.innerHTML = '<div class="adm-empty">No reports found.</div>';
      return;
    }

    pane.innerHTML = `
      <div class="adm-table-wrap">
        <table class="adm-table">
          <thead>
            <tr><th>#</th><th>User</th><th>Type</th><th>Channel</th><th>Identifier</th><th>Description</th><th>Date</th><th>Action</th></tr>
          </thead>
          <tbody>
            ${reports.map(r => `
              <tr id="report-row-${r.id}">
                <td class="adm-muted">${r.id}</td>
                <td class="adm-email">${r.user_email}</td>
                <td>${pill(r.scam_type, '#f59e0b')}</td>
                <td>${r.channel || '—'}</td>
                <td class="adm-snippet">${escHtml(r.identifier || '—')}</td>
                <td class="adm-snippet">${escHtml(r.description.substring(0, 60))}${r.description.length > 60 ? '…' : ''}</td>
                <td class="adm-muted">${formatDate(r.created_at)}</td>
                <td>
                  <button class="adm-act-btn adm-act-danger" onclick="deleteReport(${r.id})">🗑 Delete</button>
                </td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="adm-count">${reports.length} report${reports.length !== 1 ? 's' : ''} (showing latest 200)</div>`;
  } catch {
    pane.innerHTML = '<div class="adm-error-msg">Failed to load reports.</div>';
  }
}

async function deleteReport(id) {
  if (!confirm_action(`Delete report #${id}? This cannot be undone.`)) return;
  try {
    const res = await apiFetch(`/api/admin/reports/${id}`, { method: 'DELETE' });
    if (!res) return;
    if (res.ok) {
      document.getElementById(`report-row-${id}`)?.remove();
      showToast(`Report #${id} deleted.`);
    } else {
      const e = await res.json();
      showToast(e.detail || 'Delete failed.', 'error');
    }
  } catch { showToast('Request failed.', 'error'); }
}

// ── Admin Logout ──────────────────────────────────────────────────────────────
function adminLogout() {
  if (!confirm_action('Sign out of the admin panel?')) return;
  localStorage.removeItem('adminToken');
  localStorage.removeItem('adminUser');
  window.location.href = 'admin-login.html';
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Populate admin name in sidebar
  const nameEl = document.getElementById('admin-name');
  const emailEl = document.getElementById('admin-email');
  if (nameEl) nameEl.textContent = adminUser.name || 'Admin';
  if (emailEl) emailEl.textContent = adminUser.email || '';

  // Load default tab
  switchTab('stats');
});
