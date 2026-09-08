// Utility chart functions
function createDoughnut(ctx, labels, data, colors) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data, backgroundColor: colors }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#e0e0ff', padding: 15 } },
            },
            cutout: '65%',
        },
    });
}

function createBarChart(ctx, labels, datasets) {
    return new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#e0e0ff' } },
            },
            scales: {
                y: { beginAtZero: true, grid: { color: '#2a2a4a' }, ticks: { color: '#8888aa' } },
                x: { grid: { display: false }, ticks: { color: '#e0e0ff' } },
            },
        },
    });
}

function createRadar(ctx, labels, datasets) {
    return new Chart(ctx, {
        type: 'radar',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#e0e0ff' } },
            },
            scales: {
                r: {
                    grid: { color: '#2a2a4a' },
                    angleLines: { color: '#2a2a4a' },
                    pointLabels: { color: '#e0e0ff', font: { size: 11 } },
                    ticks: { display: false, stepSize: 20 },
                    min: 0,
                    max: 100,
                },
            },
        },
    });
}

function createLineChart(ctx, labels, datasets) {
    return new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#e0e0ff' } },
            },
            scales: {
                y: { beginAtZero: false, grid: { color: '#2a2a4a' }, ticks: { color: '#8888aa' } },
                x: { grid: { display: false }, ticks: { color: '#e0e0ff' } },
            },
            elements: {
                point: { radius: 3, hoverRadius: 6 },
                line: { tension: 0.4 },
            },
        },
    });
}
