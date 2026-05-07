'use strict';

// ── API ──────────────────────────────────────────────────────────
const api = {
  async req(method, url, body) {
    const opts = { method, credentials: 'include', headers: {} };
    if (body) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    const r = await fetch(url, opts);
    if (r.status === 401) { showLogin(); return null; }
    if (!r.ok) {
      const err = await r.json().catch(() => ({ detail: r.statusText }));
      throw new Error(err.detail || r.statusText);
    }
    return r.json();
  },
  get:  (url)       => api.req('GET',  url, null),
  post: (url, body) => api.req('POST', url, body),
  put:  (url, body) => api.req('PUT',  url, body),
  async loginForm(username, password) {
    const fd = new FormData();
    fd.append('username', username);
    fd.append('password', password);
    const r = await fetch('/auth/login', { method: 'POST', body: fd, credentials: 'include' });
    if (!r.ok) {
      const e = await r.json().catch(() => ({ detail: 'Ошибка' }));
      throw new Error(e.detail);
    }
    return r.json();
  },
};

// ── TOAST ────────────────────────────────────────────────────────
function toast(msg, type = 'ok') {
  const el = document.createElement('div');
  el.className = `toast-item ${type}`;
  el.textContent = msg;
  document.getElementById('toast').appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ── CHART INSTANCE ───────────────────────────────────────────────
let trafficChart = null;

function buildChart(labels, up, down) {
  const ctx = document.getElementById('traffic-chart').getContext('2d');

  const gradUp = ctx.createLinearGradient(0, 0, 0, 280);
  gradUp.addColorStop(0, 'rgba(79,142,247,.22)');
  gradUp.addColorStop(1, 'rgba(79,142,247,.0)');

  const gradDown = ctx.createLinearGradient(0, 0, 0, 280);
  gradDown.addColorStop(0, 'rgba(62,207,142,.18)');
  gradDown.addColorStop(1, 'rgba(62,207,142,.0)');

  const cfg = {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Upload',
          data: up,
          borderColor: '#4f8ef7',
          backgroundColor: gradUp,
          fill: true,
          borderWidth: 2,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: '#4f8ef7',
          pointBorderWidth: 0,
        },
        {
          label: 'Download',
          data: down,
          borderColor: '#3ecf8e',
          backgroundColor: gradDown,
          fill: true,
          borderWidth: 2,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: '#3ecf8e',
          pointBorderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      animation: { duration: 500 },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            font: { family: "'JetBrains Mono', monospace", size: 11 },
            color: '#666c80',
            boxWidth: 10,
            boxHeight: 10,
            borderRadius: 3,
            useBorderRadius: true,
            padding: 16,
          },
        },
        tooltip: {
          backgroundColor: '#191d26',
          borderColor: 'rgba(255,255,255,.1)',
          borderWidth: 1,
          titleColor: '#e2e4ea',
          bodyColor: '#666c80',
          titleFont: { family: "'JetBrains Mono', monospace", size: 11, weight: '600' },
          bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
          padding: 12,
          displayColors: true,
          boxWidth: 8,
          boxHeight: 8,
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} GB`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,.04)' },
          ticks: {
            color: '#666c80',
            font: { family: "'JetBrains Mono', monospace", size: 10 },
            maxRotation: 45,
          },
        },
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(255,255,255,.05)' },
          ticks: {
            color: '#666c80',
            font: { family: "'JetBrains Mono', monospace", size: 10 },
            callback: v => `${v} GB`,
          },
        },
      },
    },
  };

  if (trafficChart) trafficChart.destroy();
  trafficChart = new Chart(ctx, cfg);
}

// ── STATE ────────────────────────────────────────────────────────
let allWeekly = [];
let currentWeeks = 16;

// ── DATA LOAD ────────────────────────────────────────────────────
async function loadWeekly(weeks) {
  const data = await api.get(`/api/weekly?weeks=${weeks}`);
  if (!data) return;
  allWeekly = data;
  renderWeekly(data);
}

function renderWeekly(data) {
  const empty = document.getElementById('chart-empty');
  if (!data.length) { empty.style.display = 'flex'; return; }
  empty.style.display = 'none';

  const labels = data.map(d => d.week);
  const up     = data.map(d => +d.upload_gb.toFixed(3));
  const down   = data.map(d => +d.download_gb.toFixed(3));
  const totals = data.map(d => +d.total_gb.toFixed(3));

  buildChart(labels, up, down);

  const totalAll = totals.reduce((a, b) => a + b, 0);
  const peak     = Math.max(...totals);
  const avg      = totalAll / totals.length;
  const last     = totals.at(-1) || 0;

  document.getElementById('kpi-total').textContent = totalAll.toFixed(1);
  document.getElementById('kpi-week').textContent  = last.toFixed(1);
  document.getElementById('kpi-peak').textContent  = peak.toFixed(1);
  document.getElementById('kpi-avg').textContent   = avg.toFixed(1);
}

async function loadClients() {
  const data = await api.get('/api/clients');
  if (!data) return;

  const tbody = document.getElementById('clients-body');
  tbody.innerHTML = '';

  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:32px">Нет данных</td></tr>';
    return;
  }

  const BYTES = 1073741824;
  const maxTotal = Math.max(...data.map(d => d.total_gb));

  data.forEach(d => {
    const upGb   = (d.upload_bytes   / BYTES).toFixed(2);
    const downGb = (d.download_bytes / BYTES).toFixed(2);
    const total  = d.upload_bytes + d.download_bytes;
    const pct = maxTotal > 0 ? (d.total_gb / maxTotal * 100).toFixed(1) : 0;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${d.email}</td>
      <td>${d.inbound_id}</td>
      <td>${d.upload_gb.toFixed(2)}</td>
      <td>${d.download_gb.toFixed(2)}</td>
      <td>
        <div class="share-bar-wrap">
          <div class="share-bar"><div class="share-bar-fill" style="width:${pct}%"></div></div>
          <span style="color:var(--text-muted);font-size:.75rem;min-width:36px">${pct}%</span>
        </div>
      </td>`;
    tbody.appendChild(tr);
  });
}

async function loadSettings() {
  const data = await api.get('/api/settings');
  if (!data) return;

  document.getElementById('s-xui-db-path').value  = data.xui_db_path  || '';
  document.getElementById('s-app-db-path').value  = data.app_db_path  || '';
  document.getElementById('s-sync-cron').value    = data.sync_cron    || '';
  document.getElementById('s-history').value      = data.history_weeks || 24;
  document.getElementById('info-username').textContent   = data.admin_username || '—';
  document.getElementById('info-cron').textContent       = data.sync_cron      || '—';
  document.getElementById('info-xui-path').textContent   = data.xui_db_path    || '—';
  document.getElementById('info-app-path').textContent   = data.app_db_path    || '—';
}

// ── AUTH ─────────────────────────────────────────────────────────
function showLogin() {
  document.getElementById('login-screen').style.display = 'flex';
  document.getElementById('app').style.display = 'none';
}

function showApp() {
  document.getElementById('login-screen').style.display = 'none';
  document.getElementById('app').style.display = 'flex';
}

async function checkSession() {
  const me = await api.get('/auth/me').catch(() => null);
  if (me && me.username) {
    document.getElementById('header-user').textContent = me.username;
    showApp();
    loadWeekly(currentWeeks);
    loadClients();
    loadSyncStatus();
  } else {
    showLogin();
  }
}

async function loadSyncStatus() {
  const data = await api.get('/api/settings').catch(() => null);
  if (!data) return;
  const badge = document.getElementById('sync-badge');
  if (data.xui_db_path) {
    badge.textContent = 'sync active';
    badge.className = 'sync-badge';
  } else {
    badge.textContent = 'no xui db';
    badge.className = 'sync-badge warn';
  }
}

// ── TABS ─────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.page').forEach(p => p.classList.toggle('active', p.dataset.page === name));
  if (name === 'settings') loadSettings();
  if (name === 'clients')  loadClients();
}

// ── RANGE BUTTONS ────────────────────────────────────────────────
function setRange(weeks) {
  currentWeeks = weeks;
  document.querySelectorAll('.range-btn').forEach(b => b.classList.toggle('active', +b.dataset.w === weeks));
  loadWeekly(weeks);
}

// ── INIT ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // Login
  document.getElementById('login-form').addEventListener('submit', async e => {
    e.preventDefault();
    const btn = e.target.querySelector('button[type=submit]');
    btn.disabled = true;
    try {
      await api.loginForm(
        document.getElementById('login-username').value,
        document.getElementById('login-password').value,
      );
      await checkSession();
    } catch (err) {
      document.getElementById('login-error').textContent = err.message;
    } finally {
      btn.disabled = false;
    }
  });

  // Logout
  document.getElementById('btn-logout').addEventListener('click', async () => {
    await api.post('/auth/logout').catch(() => {});
    showLogin();
  });

  // Tabs
  document.querySelectorAll('.tab').forEach(t =>
    t.addEventListener('click', () => switchTab(t.dataset.tab))
  );

  // Range
  document.querySelectorAll('.range-btn').forEach(b =>
    b.addEventListener('click', () => setRange(+b.dataset.w))
  );

  // Manual sync
  document.getElementById('btn-sync').addEventListener('click', async () => {
    const btn = document.getElementById('btn-sync');
    btn.disabled = true;
    try {
      const r = await api.post('/api/sync');
      toast(`Синхронизировано: ${r.synced} записей`);
      loadWeekly(currentWeeks);
      loadClients();
    } catch (err) {
      toast(err.message, 'err');
    } finally {
      btn.disabled = false;
    }
  });

  // XUI settings
  document.getElementById('form-xui').addEventListener('submit', async e => {
    e.preventDefault();
    try {
      await api.put('/api/settings/xui', {
        db_path:      document.getElementById('s-xui-db-path').value.trim(),
        app_db_path:  document.getElementById('s-app-db-path').value.trim(),
        sync_cron:    document.getElementById('s-sync-cron').value.trim(),
        history_weeks: +document.getElementById('s-history').value,
      });
      toast('Настройки сохранены');
      loadSettings();
    } catch (err) {
      toast(err.message, 'err');
    }
  });

  // Password
  document.getElementById('form-password').addEventListener('submit', async e => {
    e.preventDefault();
    const np = document.getElementById('s-new-pass').value;
    const cp = document.getElementById('s-confirm-pass').value;
    if (np !== cp) { toast('Пароли не совпадают', 'err'); return; }
    try {
      await api.put('/api/settings/password', {
        current_password: document.getElementById('s-cur-pass').value,
        new_password: np,
      });
      toast('Пароль изменён');
      e.target.reset();
    } catch (err) {
      toast(err.message, 'err');
    }
  });

  checkSession();
});
