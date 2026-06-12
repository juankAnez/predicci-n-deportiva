// Dashboard charts and functionality
async function loadDashboard() {
    try {
        const [modelsData, predHistory] = await Promise.all([
            apiGet('/models/metrics').catch(() => ({ data: {} })),
            apiGet('/predictions/history').catch(() => ({ data: [] })),
        ]);

        const models = modelsData.data || {};
        const predictions = predHistory.data || [];

        // Update stats
        const accEl = document.getElementById('global-accuracy');
        if (accEl && models.xgboost) {
            accEl.textContent = (models.xgboost.accuracy * 100).toFixed(1) + '%';
        }

        const totalEl = document.getElementById('total-matches');
        if (totalEl) totalEl.textContent = predictions.length || '0';

        const logLossEl = document.getElementById('avg-log-loss');
        if (logLossEl && models.xgboost) {
            logLossEl.textContent = models.xgboost.log_loss?.toFixed(4) || '--';
        }

        // Model comparison chart
        const ctx1 = document.getElementById('modelComparisonChart');
        if (ctx1) {
            const labels = Object.keys(models);
            const accuracies = labels.map(k => (models[k]?.accuracy || 0) * 100);
            const f1s = labels.map(k => (models[k]?.f1_score || 0) * 100);

            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: labels.map(k => k.toUpperCase()),
                    datasets: [
                        { label: 'Accuracy (%)', data: accuracies, backgroundColor: 'rgba(74, 125, 255, 0.7)' },
                        { label: 'F1-Score (%)', data: f1s, backgroundColor: 'rgba(0, 212, 170, 0.7)' },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { labels: { color: '#e0e0ff' } },
                    },
                    scales: {
                        y: { beginAtZero: true, max: 100, grid: { color: '#2a2a4a' }, ticks: { color: '#8888aa' } },
                        x: { grid: { display: false }, ticks: { color: '#e0e0ff' } },
                    },
                },
            });
        }

        // Prediction history
        const historyList = document.getElementById('prediction-history-list');
        if (historyList) {
            if (predictions.length === 0) {
                historyList.innerHTML = '<p class="text-muted text-center">No hay predicciones aún</p>';
            } else {
                historyList.innerHTML = predictions.slice(0, 10).map(p => `
                    <div class="d-flex justify-content-between align-items-center border-bottom border-secondary py-2">
                        <div>
                            <small class="text-muted">#${p.match_id}</small>
                            <span class="badge bg-${p.predicted === 'H' ? 'primary' : p.predicted === 'D' ? 'secondary' : 'danger'} ms-1">${p.predicted}</span>
                        </div>
                        <small class="text-${p.confidence > 60 ? 'success' : 'warning'}">${p.confidence}%</small>
                    </div>
                `).join('');
            }
        }

        // Accuracy trend chart
        const ctx3 = document.getElementById('accuracyTrendChart');
        if (ctx3) {
            const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
            new Chart(ctx3, {
                type: 'line',
                data: {
                    labels: months,
                    datasets: [
                        { label: 'Precisión', data: [68, 70, 72, 71, 74, 73], borderColor: '#4a7dff', tension: 0.4, fill: false },
                        { label: 'Log Loss', data: [0.58, 0.57, 0.55, 0.56, 0.54, 0.55], borderColor: '#ff4757', tension: 0.4, fill: false, yAxisID: 'y1' },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#e0e0ff' } } },
                    scales: {
                        y: { beginAtZero: false, min: 60, max: 80, grid: { color: '#2a2a4a' }, ticks: { color: '#8888aa' } },
                        y1: { position: 'right', beginAtZero: false, min: 0.5, max: 0.6, grid: { display: false }, ticks: { color: '#8888aa' } },
                        x: { grid: { display: false }, ticks: { color: '#e0e0ff' } },
                    },
                },
            });
        }
    } catch (e) {
        console.error('Dashboard error:', e);
    }
}

// Distribution chart for home page
async function loadDistributionChart() {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    try {
        const data = await apiGet('/predictions/history');
        const predictions = data.data || [];
        if (predictions.length === 0) return;

        const home = predictions.filter(p => p.predicted === 'H').length;
        const draw = predictions.filter(p => p.predicted === 'D').length;
        const away = predictions.filter(p => p.predicted === 'A').length;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Victoria Local', 'Empate', 'Victoria Visitante'],
                datasets: [{
                    data: [home, draw, away],
                    backgroundColor: ['rgba(74, 125, 255, 0.8)', 'rgba(99, 110, 114, 0.8)', 'rgba(255, 71, 87, 0.8)'],
                }],
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#e0e0ff' } } },
            },
        });
    } catch (e) {
        console.error('Distribution chart error:', e);
    }
}

// Team comparison
async function loadTeams() {
    try {
        const data = await apiGet('/teams');
        const teams = data.data || [];
        const select1 = document.getElementById('team1-select');
        const select2 = document.getElementById('team2-select');
        if (!select1 || !select2) return;

        const options = teams.map(t =>
            `<option value="${t.id}">${t.name} (${t.confederation || '—'})</option>`
        ).join('');

        select1.innerHTML = '<option value="">Seleccionar equipo...</option>' + options;
        select2.innerHTML = '<option value="">Seleccionar equipo...</option>' + options;

        select1.addEventListener('change', loadComparison);
        select2.addEventListener('change', loadComparison);
    } catch (e) {
        console.error('Load teams error:', e);
    }
}

async function loadComparison() {
    const team1 = document.getElementById('team1-select')?.value;
    const team2 = document.getElementById('team2-select')?.value;
    if (!team1 || !team2) return;

    const ctx = document.getElementById('compareRadarChart');
    if (!ctx) return;

    try {
        const [d1, d2] = await Promise.all([
            apiGet(`/stats/team/${team1}?limit=5`).catch(() => ({ data: [] })),
            apiGet(`/stats/team/${team2}?limit=5`).catch(() => ({ data: [] })),
        ]);

        const stats1 = d1.data || [];
        const stats2 = d2.data || [];

        const avg1 = stats1.length ? {
            goles: stats1.reduce((s, m) => s + (m.goals || 0), 0) / stats1.length,
            xg: stats1.reduce((s, m) => s + (m.xg || 0), 0) / stats1.length,
            posesion: stats1.reduce((s, m) => s + (m.possession || 0), 0) / stats1.length,
            precision: stats1.reduce((s, m) => s + (m.passing_accuracy || 0), 0) / stats1.length,
            ppda: stats1.reduce((s, m) => s + (m.ppda || 15), 0) / stats1.length,
        } : { goles: 0, xg: 0, posesion: 0, precision: 0, ppda: 0 };

        const avg2 = stats2.length ? {
            goles: stats2.reduce((s, m) => s + (m.goals || 0), 0) / stats2.length,
            xg: stats2.reduce((s, m) => s + (m.xg || 0), 0) / stats2.length,
            posesion: stats2.reduce((s, m) => s + (m.possession || 0), 0) / stats2.length,
            precision: stats2.reduce((s, m) => s + (m.passing_accuracy || 0), 0) / stats2.length,
            ppda: stats2.reduce((s, m) => s + (m.ppda || 15), 0) / stats2.length,
        } : { goles: 0, xg: 0, posesion: 0, precision: 0, ppda: 0 };

        const maxGoals = Math.max(avg1.goles, avg2.goles, 1);
        const maxXg = Math.max(avg1.xg, avg2.xg, 1);

        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Goles', 'xG', 'Posesión (%)', 'Precisión Pase (%)', 'PPDA (inverso)'],
                datasets: [
                    { label: 'Equipo 1', data: [
                        (avg1.goles / maxGoals) * 100,
                        (avg1.xg / maxXg) * 100,
                        avg1.posesion,
                        avg1.precision,
                        Math.min(100, (15 / (avg1.ppda || 15)) * 100),
                    ], borderColor: '#4a7dff', backgroundColor: 'rgba(74, 125, 255, 0.2)' },
                    { label: 'Equipo 2', data: [
                        (avg2.goles / maxGoals) * 100,
                        (avg2.xg / maxXg) * 100,
                        avg2.posesion,
                        avg2.precision,
                        Math.min(100, (15 / (avg2.ppda || 15)) * 100),
                    ], borderColor: '#ff4757', backgroundColor: 'rgba(255, 71, 87, 0.2)' },
                ],
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#e0e0ff' } } },
                scales: {
                    r: { grid: { color: '#2a2a4a' }, angleLines: { color: '#2a2a4a' }, pointLabels: { color: '#e0e0ff' }, ticks: { display: false } },
                },
            },
        });
    } catch (e) {
        console.error('Comparison error:', e);
    }
}

// Bootstrap
if (document.getElementById('distributionChart')) loadDistributionChart();
