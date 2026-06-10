/**
 * VN Stock Dashboard — Frontend Logic
 */

const API = '';

// ===== STATE =====
let currentView = 'dashboard';
let watchlist = [];

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initClock();
  initSearch();
  initAnalyzer();
  initWatchlistControls();
  loadDashboard();
});

// ===== NAVIGATION =====
function initNav() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const view = item.dataset.view;
      switchView(view);
    });
  });
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`.nav-item[data-view="${view}"]`).classList.add('active');

  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(`view-${view}`).classList.add('active');

  const titles = { dashboard: 'Dashboard', analyzer: 'Buffett Analyzer', watchlist: 'Watchlist', reports: 'Lịch sử Báo cáo' };
  document.getElementById('breadcrumb').textContent = titles[view] || 'Dashboard';

  if (view === 'watchlist') loadWatchlistTable();
  if (view === 'reports') loadReportsList();
}

// ===== CLOCK =====
function initClock() {
  const el = document.getElementById('clock');
  function update() {
    const now = new Date();
    el.textContent = now.toLocaleString('vi-VN', {
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      day: '2-digit', month: '2-digit', year: 'numeric'
    });
  }
  update();
  setInterval(update, 1000);
}

// ===== SEARCH =====
function initSearch() {
  const input = document.getElementById('globalSearch');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const ticker = input.value.trim().toUpperCase();
      if (ticker) {
        switchView('analyzer');
        document.getElementById('analyzerTicker').value = ticker;
        runAnalysis(ticker);
        input.value = '';
      }
    }
  });
}

// ===== DASHBOARD =====
async function loadDashboard() {
  loadMarket();
  loadWatchlistCards();
  loadRecentReports();
}

async function loadMarket() {
  const statusEl = document.getElementById('marketStatus');
  try {
    const res = await fetch(`${API}/api/market`);
    const data = await res.json();
    statusEl.textContent = data.date;

    Object.entries(data.indices).forEach(([name, info]) => {
      const card = document.querySelector(`.index-card[data-index="${name}"]`);
      if (!card) return;
      card.classList.remove('skeleton');
      card.querySelector('.index-value').textContent = formatNumber(info.value);
      const changeEl = card.querySelector('.index-change');
      const sign = info.change >= 0 ? '+' : '';
      changeEl.textContent = `${sign}${info.change.toFixed(2)} (${sign}${info.change_pct.toFixed(2)}%)`;
      changeEl.className = `index-change ${info.change >= 0 ? 'up' : 'down'}`;
    });
  } catch (e) {
    statusEl.textContent = 'Offline';
    statusEl.className = 'badge';
    console.error('Market load error:', e);
  }
}

async function loadWatchlistCards() {
  const container = document.getElementById('dashboardWatchlist');
  try {
    const res = await fetch(`${API}/api/watchlist`);
    const data = await res.json();
    watchlist = data.tickers;

    if (watchlist.length === 0) {
      container.innerHTML = '<div class="empty-state">Chưa có mã nào trong watchlist</div>';
      return;
    }

    container.innerHTML = watchlist.map(t => `
      <div class="stock-card skeleton" id="card-${t}" onclick="analyzeFromCard('${t}')">
        <div class="stock-card-header">
          <div><div class="stock-ticker">${t}</div><div class="stock-name">Loading...</div></div>
          <div><div class="stock-price">---</div><div class="stock-change flat">---</div></div>
        </div>
        <div class="stock-metrics">
          <div class="metric"><div class="metric-label">P/E</div><div class="metric-value">-</div></div>
          <div class="metric"><div class="metric-label">ROE</div><div class="metric-value">-</div></div>
          <div class="metric"><div class="metric-label">D/E</div><div class="metric-value">-</div></div>
        </div>
      </div>
    `).join('');

    // Load cards sequentially to avoid rate limits
    for (const t of watchlist) {
      await loadStockCard(t);
    }
  } catch (e) {
    container.innerHTML = '<div class="empty-state">Không tải được watchlist</div>';
  }
}

async function loadStockCard(ticker) {
  const card = document.getElementById(`card-${ticker}`);
  if (!card) return;
  try {
    const res = await fetch(`${API}/api/stock/${ticker}`);
    const d = await res.json();
    card.classList.remove('skeleton');

    card.querySelector('.stock-name').textContent = d.name;
    card.querySelector('.stock-price').textContent = d.last_close ? formatNumber(d.last_close) : 'N/A';

    const changeEl = card.querySelector('.stock-change');
    if (d.change !== undefined && d.change !== 0) {
      const sign = d.change >= 0 ? '+' : '';
      changeEl.textContent = `${sign}${formatNumber(d.change)} (${sign}${d.change_pct}%)`;
      changeEl.className = `stock-change ${d.change >= 0 ? 'up' : 'down'}`;
    } else {
      changeEl.textContent = '0 (0%)';
      changeEl.className = 'stock-change flat';
    }

    const metrics = card.querySelectorAll('.metric-value');
    metrics[0].textContent = d.pe ? d.pe.toFixed(1) : '-';
    metrics[1].textContent = d.roe ? `${d.roe}%` : '-';
    metrics[2].textContent = d.de ? d.de.toFixed(2) : '-';
  } catch (e) {
    card.classList.remove('skeleton');
    card.querySelector('.stock-name').textContent = 'Error loading';
  }
}

function analyzeFromCard(ticker) {
  switchView('analyzer');
  document.getElementById('analyzerTicker').value = ticker;
  runAnalysis(ticker);
}

// ===== ANALYZER =====
function initAnalyzer() {
  document.getElementById('analyzerRun').addEventListener('click', () => {
    const ticker = document.getElementById('analyzerTicker').value.trim().toUpperCase();
    if (ticker) runAnalysis(ticker);
  });

  document.getElementById('analyzerTicker').addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const ticker = e.target.value.trim().toUpperCase();
      if (ticker) runAnalysis(ticker);
    }
  });

  document.querySelectorAll('.chip[data-ticker]').forEach(chip => {
    chip.addEventListener('click', () => {
      const ticker = chip.dataset.ticker;
      document.getElementById('analyzerTicker').value = ticker;
      runAnalysis(ticker);
    });
  });
}

async function runAnalysis(ticker) {
  const btn = document.getElementById('analyzerRun');
  const btnText = btn.querySelector('.btn-text');
  const btnLoader = btn.querySelector('.btn-loader');
  const resultsDiv = document.getElementById('analyzerResults');

  btnText.textContent = 'Đang phân tích...';
  btnLoader.style.display = 'inline-block';
  btn.disabled = true;
  resultsDiv.style.display = 'block';
  resultsDiv.innerHTML = `
    <div class="result-header">
      <div style="text-align:center; padding: 40px;">
        <div class="btn-loader" style="display:inline-block; width:32px; height:32px; border-width:3px;"></div>
        <p style="margin-top:16px; color: var(--text-muted);">Đang chạy Buffett Rubric cho <strong style="color:var(--accent-emerald)">${ticker}</strong>...</p>
      </div>
    </div>`;

  try {
    const res = await fetch(`${API}/api/buffett/${ticker}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    renderAnalysisResult(data);
    toast(`✅ Phân tích ${ticker} hoàn tất — ${data.verdict}`, 'success');
  } catch (e) {
    resultsDiv.innerHTML = `
      <div class="result-header pass">
        <p style="color:var(--accent-red);">❌ Lỗi phân tích ${ticker}: ${e.message}</p>
      </div>`;
    toast(`❌ Lỗi: ${e.message}`, 'error');
  } finally {
    btnText.textContent = 'Phân tích';
    btnLoader.style.display = 'none';
    btn.disabled = false;
  }
}

function renderAnalysisResult(data) {
  const v = data.verdict.toLowerCase();
  const resultsDiv = document.getElementById('analyzerResults');

  const criteriaHtml = data.criteria.map(c => `
    <div class="criterion ${c.passed ? 'passed' : 'failed'}">
      <span class="criterion-icon">${c.passed ? '✅' : '❌'}</span>
      <span>${c.label}</span>
    </div>
  `).join('');

  resultsDiv.innerHTML = `
    <div class="result-header ${v}">
      <div class="result-verdict">
        <div class="verdict-score ${v}">${data.score_pct}%</div>
        <div class="verdict-text">
          <h3>${data.ticker} — ${data.name}</h3>
          <p>${data.verdict_reason}</p>
        </div>
        <span class="verdict-label badge badge-${v}">${data.verdict}</span>
      </div>
      <div style="display:flex; gap:8px; font-size:13px; color:var(--text-muted);">
        <span>📅 ${data.date}</span>
        <span>•</span>
        <span>${data.is_bank ? '🏦 Bank rubric' : '📊 Non-bank rubric'}</span>
        <span>•</span>
        <span>${data.passed}/${data.total} criteria passed</span>
      </div>
    </div>

    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-label">P/E</div>
        <div class="metric-value">${data.ratios.pe?.toFixed(2) || 'N/A'}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">P/B</div>
        <div class="metric-value">${data.ratios.pb?.toFixed(2) || 'N/A'}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">ROE</div>
        <div class="metric-value">${data.ratios.roe}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">ROE 3Y</div>
        <div class="metric-value">${data.ratios.roe_3y}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">ROA</div>
        <div class="metric-value">${data.ratios.roa}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">D/E</div>
        <div class="metric-value">${data.ratios.de?.toFixed(2) || 'N/A'}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">EPS CAGR 5Y</div>
        <div class="metric-value">${data.ratios.eps_cagr_5y}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Price</div>
        <div class="metric-value">${data.ratios.last_close ? formatNumber(data.ratios.last_close) : 'N/A'}</div>
      </div>
    </div>

    <section class="section">
      <h2 class="section-title"><span class="section-icon">📋</span> Buffett Criteria</h2>
      <div class="criteria-grid">${criteriaHtml}</div>
    </section>
  `;
}

// ===== WATCHLIST =====
function initWatchlistControls() {
  const addBtn = document.getElementById('addWatchlistBtn');
  const form = document.getElementById('addWatchlistForm');
  const input = document.getElementById('addWatchlistInput');
  const confirm = document.getElementById('addWatchlistConfirm');
  const cancel = document.getElementById('addWatchlistCancel');

  addBtn.addEventListener('click', () => {
    form.style.display = form.style.display === 'none' ? 'flex' : 'none';
    if (form.style.display === 'flex') input.focus();
  });

  cancel.addEventListener('click', () => { form.style.display = 'none'; });

  const doAdd = async () => {
    const ticker = input.value.trim().toUpperCase();
    if (!ticker) return;
    try {
      const res = await fetch(`${API}/api/watchlist/add?ticker=${ticker}`, { method: 'POST' });
      const data = await res.json();
      watchlist = data.tickers;
      input.value = '';
      form.style.display = 'none';
      loadWatchlistTable();
      toast(`✅ Đã thêm ${ticker} vào watchlist`, 'success');
    } catch (e) {
      toast('❌ Lỗi thêm mã', 'error');
    }
  };

  confirm.addEventListener('click', doAdd);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') doAdd(); });
}

async function loadWatchlistTable() {
  const tbody = document.getElementById('watchlistBody');
  try {
    const res = await fetch(`${API}/api/watchlist`);
    const data = await res.json();
    watchlist = data.tickers;

    if (watchlist.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" class="empty-state">Chưa có mã nào trong watchlist</td></tr>';
      return;
    }

    tbody.innerHTML = watchlist.map(t => `
      <tr id="wl-row-${t}">
        <td class="ticker-cell">${t}</td>
        <td class="name-cell">Loading...</td>
        <td>-</td>
        <td class="price-cell">---</td>
        <td class="change-cell">---</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>
          <button class="btn btn-sm btn-primary" onclick="analyzeFromCard('${t}')" style="margin-right:4px">🔬</button>
          <button class="btn btn-sm btn-danger" onclick="removeFromWatchlist('${t}')">✕</button>
        </td>
      </tr>
    `).join('');

    // Load rows sequentially to avoid rate limits
    for (const t of watchlist) {
      await loadWatchlistRow(t);
    }
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-state">Lỗi tải watchlist</td></tr>';
  }
}

async function loadWatchlistRow(ticker) {
  const row = document.getElementById(`wl-row-${ticker}`);
  if (!row) return;
  try {
    const res = await fetch(`${API}/api/stock/${ticker}`);
    const d = await res.json();
    const cells = row.querySelectorAll('td');
    cells[1].textContent = d.name || '-';
    cells[2].textContent = d.industry || '-';
    cells[3].textContent = d.last_close ? formatNumber(d.last_close) : '-';

    const sign = d.change >= 0 ? '+' : '';
    cells[4].textContent = d.change ? `${sign}${d.change_pct}%` : '0%';
    cells[4].className = `change-cell ${d.change > 0 ? 'up' : d.change < 0 ? 'down' : ''}`;

    cells[5].textContent = d.pe ? d.pe.toFixed(1) : '-';
    cells[6].textContent = d.roe ? `${d.roe}%` : '-';
    cells[7].textContent = d.de ? d.de.toFixed(2) : '-';
  } catch (e) {
    // silently fail row
  }
}

async function removeFromWatchlist(ticker) {
  try {
    const res = await fetch(`${API}/api/watchlist/remove?ticker=${ticker}`, { method: 'POST' });
    const data = await res.json();
    watchlist = data.tickers;
    loadWatchlistTable();
    toast(`Đã xóa ${ticker}`, 'success');
  } catch (e) {
    toast('❌ Lỗi xóa mã', 'error');
  }
}

// ===== REPORTS =====
async function loadRecentReports() {
  const container = document.getElementById('recentReports');
  try {
    const res = await fetch(`${API}/api/reports`);
    const data = await res.json();
    if (data.reports.length === 0) {
      container.innerHTML = '<div class="empty-state">Chưa có báo cáo. Chạy Analyzer để tạo!</div>';
      return;
    }
    container.innerHTML = data.reports.slice(0, 5).map(r => `
      <div class="report-item" onclick="viewReport('${r.filename}')">
        <div class="report-item-left">
          <span class="report-ticker">${r.ticker}</span>
          <span class="report-date">${r.date}</span>
        </div>
        <span class="report-arrow">→</span>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = '<div class="empty-state">Không tải được báo cáo</div>';
  }
}

async function loadReportsList() {
  const grid = document.getElementById('reportsGrid');
  try {
    const res = await fetch(`${API}/api/reports`);
    const data = await res.json();
    if (data.reports.length === 0) {
      grid.innerHTML = '<div class="empty-state">Chưa có báo cáo nào</div>';
      return;
    }
    grid.innerHTML = data.reports.map(r => `
      <div class="report-item" onclick="viewReport('${r.filename}')">
        <div class="report-item-left">
          <span class="report-ticker">${r.ticker}</span>
          <span class="report-date">${r.date}</span>
        </div>
        <span class="report-arrow">→</span>
      </div>
    `).join('');
  } catch (e) {
    grid.innerHTML = '<div class="empty-state">Lỗi tải danh sách báo cáo</div>';
  }
}

async function viewReport(filename) {
  const viewer = document.getElementById('reportViewer');
  const content = document.getElementById('reportContent');
  const title = document.getElementById('reportViewerTitle');

  viewer.style.display = 'block';
  content.textContent = 'Loading...';
  title.textContent = filename;

  document.getElementById('closeReport').onclick = () => { viewer.style.display = 'none'; };

  try {
    const res = await fetch(`${API}/api/reports/${filename}`);
    const data = await res.json();
    content.textContent = data.content;
  } catch (e) {
    content.textContent = 'Lỗi đọc báo cáo';
  }

  viewer.scrollIntoView({ behavior: 'smooth' });
}

// ===== UTILS =====
function formatNumber(n) {
  if (n == null) return '-';
  return new Intl.NumberFormat('vi-VN').format(Math.round(n));
}

function toast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(12px)';
    el.style.transition = '0.3s ease';
    setTimeout(() => el.remove(), 300);
  }, 4000);
}
