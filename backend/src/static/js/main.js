const API_BASE = '/api/v1';

function showError(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) el.innerHTML = `<div class="alert alert-danger mt-2"><i class="bi bi-exclamation-triangle"></i> ${message}</div>`;
}

function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div> Cargando...</div>';
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });
}

async function apiGet(url) {
    const response = await fetch(`${API_BASE}${url}`);
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Error de conexión' }));
        throw new Error(error.error || `HTTP ${response.status}`);
    }
    return response.json();
}

async function apiPost(url, body = {}) {
    const response = await fetch(`${API_BASE}${url}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Error de conexión' }));
        throw new Error(error.error || `HTTP ${response.status}`);
    }
    return response.json();
}

async function loadUpcomingMatches() {
    const container = document.getElementById('match-cards');
    const countBadge = document.getElementById('matches-count');
    try {
        const data = await apiGet('/predictions/upcoming');
        const matches = data.data || [];

        if (countBadge) countBadge.textContent = `${matches.length} partidos`;

        if (matches.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-info">No hay próximos partidos disponibles.</div></div>';
            return;
        }

        container.innerHTML = '';
        for (const m of matches) {
            const card = document.createElement('div');
            card.className = 'col-md-6 col-lg-3 mb-3';
            card.innerHTML = `
                <div class="match-card" onclick="location.href='/prediction/${m.match_id}'">
                    <div class="match-teams">
                        <div class="team">
                            <span class="team-name">${m.home_team_id || 'Local'}</span>
                        </div>
                        <div class="text-center text-muted fw-bold">VS</div>
                        <div class="team">
                            <span class="team-name">${m.away_team_id || 'Visitante'}</span>
                        </div>
                    </div>
                    <div class="probability-bar mt-2" id="probs-${m.match_id}"></div>
                    <div class="stats-preview">
                        <div class="stat-item">
                            <small>Fecha</small>
                            <strong>${formatDate(m.match_date)}</strong>
                        </div>
                        <div class="stat-item">
                            <small>Confianza</small>
                            <strong>${m.confidence || '--'}%</strong>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(card);

            if (m.home_win !== undefined) {
                renderProbabilityBar(`probs-${m.match_id}`, m.home_win, m.draw, m.away_win);
            }
        }
    } catch (e) {
        container.innerHTML = `<div class="col-12"><div class="alert alert-warning">Error cargando partidos: ${e.message}</div></div>`;
    }
}

function renderProbabilityBar(elementId, home, draw, away) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = `
        <div class="prob-bar-home" style="width:${home}%">${home.toFixed(0)}%</div>
        <div class="prob-bar-draw" style="width:${draw}%">${draw.toFixed(0)}%</div>
        <div class="prob-bar-away" style="width:${away}%">${away.toFixed(0)}%</div>
    `;
}

// Admin functions
async function scrapeRankings() {
    const result = document.getElementById('scraping-result');
    result.innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div> Scraping en curso...';
    try {
        const data = await apiPost('/admin/scrape/rankings');
        result.innerHTML = `<div class="alert alert-success">${data.data.message}</div>`;
    } catch (e) {
        result.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    }
}

async function trainModels() {
    const result = document.getElementById('model-result');
    result.innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div> Entrenando modelos (puede tomar varios minutos)...';
    try {
        const data = await apiPost('/models/train');
        result.innerHTML = `<div class="alert alert-success">${data.data.message}. Modelos: ${data.data.models.join(', ')}</div>`;
    } catch (e) {
        result.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    }
}

async function refreshLogs() {
    const tbody = document.getElementById('logs-table-body');
    try {
        const data = await apiGet('/admin/scrape/logs?per_page=20');
        const logs = data.data || [];
        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-muted text-center">No hay logs disponibles</td></tr>';
            return;
        }
        tbody.innerHTML = logs.map(log => `
            <tr>
                <td>${log.source}</td>
                <td>${log.data_type || '—'}</td>
                <td><span class="badge bg-${log.status === 'success' ? 'success' : log.status === 'failed' ? 'danger' : 'warning'}">${log.status}</span></td>
                <td>${log.items_count ?? '—'}</td>
                <td>${log.duration_ms ? (log.duration_ms / 1000).toFixed(1) + 's' : '—'}</td>
                <td>${log.created_at ? formatDate(log.created_at) : '—'}</td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-danger text-center">${e.message}</td></tr>`;
    }
}

async function initDatabase() {
    const result = document.getElementById('db-result');
    result.innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div> Inicializando...';
    try {
        const response = await fetch('/api/v1/admin/db/init', { method: 'POST' });
        const data = await response.json();
        result.innerHTML = `<div class="alert alert-success">${data.message || 'Base de datos inicializada'}</div>`;
    } catch (e) {
        result.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    }
}
