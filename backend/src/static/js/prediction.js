async function loadPrediction(matchId) {
    const container = document.getElementById('prediction-content');
    try {
        const data = await apiGet(`/predictions/${matchId}`);
        const pred = data.data;

        if (!pred) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-warning">Predicción no disponible</div></div>';
            return;
        }

        const result = pred.result;
        const goals = pred.goals;
        const ou = pred.over_under || {};

        // Build prediction UI
        container.innerHTML = `
            <div class="col-md-8">
                <div class="match-card">
                    <div class="match-teams">
                        <div class="team">
                            <span class="team-name text-primary">${pred.match_id || 'Local'}</span>
                            <span class="team-rank">Local</span>
                        </div>
                        <div class="text-center">
                            <div class="display-5 fw-bold text-muted mb-1">VS</div>
                            <div class="text-success fs-4">${goals.most_likely_score || '?'}</div>
                            <small class="text-muted">Marcador más probable</small>
                        </div>
                        <div class="team">
                            <span class="team-name text-danger">Visitante</span>
                            <span class="team-rank">Visitante</span>
                        </div>
                    </div>
                    <div class="probability-bar mt-3">
                        <div class="prob-bar-home" style="width:${result.home_win}%">${result.home_win.toFixed(1)}%</div>
                        <div class="prob-bar-draw" style="width:${result.draw}%">${result.draw.toFixed(1)}%</div>
                        <div class="prob-bar-away" style="width:${result.away_win}%">${result.away_win.toFixed(1)}%</div>
                    </div>
                    <div class="stats-preview mt-3">
                        <div class="stat-item">
                            <small>Predicción</small>
                            <strong class="text-${result.predicted === 'H' ? 'primary' : result.predicted === 'D' ? 'secondary' : 'danger'}">${result.predicted === 'H' ? 'Local' : result.predicted === 'D' ? 'Empate' : 'Visitante'}</strong>
                        </div>
                        <div class="stat-item">
                            <small>Confianza</small>
                            <strong>${result.confidence.toFixed(1)}%</strong>
                        </div>
                        <div class="stat-item">
                            <small>Acuerdo Modelos</small>
                            <strong>${pred.model_info?.agreement?.toFixed(1) || '--'}%</strong>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-header border-secondary">
                        <h6 class="mb-0"><i class="bi bi-bar-chart"></i> Over / Under</h6>
                    </div>
                    <div class="card-body">
                        ${['over_0.5', 'over_1.5', 'over_2.5', 'over_3.5', 'over_4.5'].map(k => {
                            const label = k.replace('_', ' ').toUpperCase();
                            const val = ou[k];
                            return val !== undefined ? `
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <small>${label}</small>
                                    <div class="d-flex align-items-center gap-2">
                                        <div class="progress" style="width: 80px; height: 8px;">
                                            <div class="progress-bar bg-info" style="width: ${val}%"></div>
                                        </div>
                                        <small class="fw-bold">${val.toFixed(1)}%</small>
                                    </div>
                                </div>
                            ` : '';
                        }).join('')}
                        <hr class="border-secondary">
                        <div class="text-center">
                            <small class="text-muted">Goles Esperados</small>
                            <h3 class="mb-0">${goals.total_expected?.toFixed(2) || '--'}</h3>
                            <small class="text-muted">Local ${goals.home_expected?.toFixed(2) || '--'} / Visitante ${goals.away_expected?.toFixed(2) || '--'}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Probability chart
        const ctx1 = document.getElementById('probabilityChart');
        if (ctx1) {
            new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: ['Victoria Local', 'Empate', 'Victoria Visitante'],
                    datasets: [{
                        data: [result.home_win, result.draw, result.away_win],
                        backgroundColor: ['rgba(74, 125, 255, 0.8)', 'rgba(99, 110, 114, 0.8)', 'rgba(255, 71, 87, 0.8)'],
                    }],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#e0e0ff' } },
                    },
                },
            });
        }

        // Goal distribution chart
        const ctx2 = document.getElementById('goalDistributionChart');
        if (ctx2) {
            const scores = goals.exact_scores || {};
            const labels = Object.keys(scores).slice(0, 8);
            const values = labels.map(k => (scores[k] || 0) * 100);

            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{ label: 'Probabilidad (%)', data: values, backgroundColor: 'rgba(0, 212, 170, 0.7)' }],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#2a2a4a' }, ticks: { color: '#8888aa' } },
                        x: { grid: { display: false }, ticks: { color: '#e0e0ff' } },
                    },
                },
            });
        }

        // Explanation
        const explanationEl = document.getElementById('explanation-content');
        if (explanationEl) {
            const topFeatures = pred.explanation?.top_features || [];
            explanationEl.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="text-muted mb-3"><i class="bi bi-star"></i> Factores Más Influyentes</h6>
                        ${topFeatures.length > 0 ? topFeatures.map((f, i) => `
                            <div class="shap-bar">
                                <small class="text-muted" style="min-width: 120px;">${f.name}</small>
                                <div class="flex-grow-1">
                                    <div class="shap-bar-fill ${f.importance > 0 ? 'shap-positive' : 'shap-negative'}"
                                         style="width: ${Math.min(100, Math.abs(f.importance) * 200)}%"></div>
                                </div>
                                <small class="fw-bold">${(f.importance * 100).toFixed(1)}%</small>
                            </div>
                        `).join('') : '<p class="text-muted">Factores no disponibles</p>'}
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-muted mb-3"><i class="bi bi-info-circle"></i> Detalles Técnicos</h6>
                        <div class="mb-2">
                            <small class="text-muted">Método de explicación:</small>
                            <strong class="ms-2">${pred.explanation?.method || 'N/A'}</strong>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted">Modelos utilizados:</small>
                            <strong class="ms-2">${pred.model_info?.models_used || 'N/A'}</strong>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted">Desviación entre modelos:</small>
                            <strong class="ms-2">${(pred.model_info?.std_dev * 100).toFixed(2) || 'N/A'}%</strong>
                        </div>
                        <hr class="border-secondary">
                        <p class="small text-muted mb-0">
                            <i class="bi bi-lightbulb text-warning"></i>
                            ${pred.explanation?.summary || 'SHAP values muestran contribución de cada feature al resultado final.'}
                        </p>
                    </div>
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error: ${e.message}</div></div>`;
    }
}
