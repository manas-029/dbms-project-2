function numbers(value) {
    if (!value) return [];
    return value.split(",").filter(Boolean).map((item) => Number(item.trim()));
}

function labels(value) {
    if (!value) return [];
    return value.split(",").filter(Boolean).map((item) => item.trim());
}

function renderTrend(canvas) {
    const risk = numbers(canvas.dataset.risk);
    const exposure = numbers(canvas.dataset.exposure);
    const chartLabels = labels(canvas.dataset.labels);
    new Chart(canvas, {
        type: "line",
        data: {
            labels: chartLabels,
            datasets: [
                { label: "Risk score", data: risk, borderColor: "#fb7185", backgroundColor: "rgba(251,113,133,.18)", tension: 0.35, fill: true },
                { label: "Exposure score", data: exposure, borderColor: "#2dd4bf", backgroundColor: "rgba(45,212,191,.14)", tension: 0.35, fill: true },
            ],
        },
        options: chartOptions(),
    });
}

function renderConsent(canvas) {
    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["Granted", "Revoked"],
            datasets: [{ data: [Number(canvas.dataset.granted || 0), Number(canvas.dataset.revoked || 0)], backgroundColor: ["#34d399", "#fb7185"] }],
        },
        options: chartOptions(false),
    });
}

function renderPlatforms(canvas) {
    const grouped = {};
    labels(canvas.dataset.labels).forEach((label) => { grouped[label] = (grouped[label] || 0) + 1; });
    new Chart(canvas, {
        type: "bar",
        data: {
            labels: Object.keys(grouped),
            datasets: [{ label: "Platforms", data: Object.values(grouped), backgroundColor: "#60a5fa" }],
        },
        options: chartOptions(),
    });
}

function chartOptions(showScales = true) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: "#edf6ff" } } },
        scales: showScales ? {
            x: { ticks: { color: "#9fb3c8" }, grid: { color: "rgba(255,255,255,.08)" } },
            y: { ticks: { color: "#9fb3c8" }, grid: { color: "rgba(255,255,255,.08)" }, beginAtZero: true, max: 100 },
        } : {},
    };
}

window.addEventListener("load", () => {
    document.querySelectorAll("canvas[data-chart]").forEach((canvas) => {
        if (canvas.dataset.chart === "trend") renderTrend(canvas);
        if (canvas.dataset.chart === "consent") renderConsent(canvas);
        if (canvas.dataset.chart === "platforms") renderPlatforms(canvas);
    });

    document.querySelectorAll(".flash").forEach((flash) => {
        setTimeout(() => flash.remove(), 4500);
    });

    const autoRefresh = document.querySelector("[data-auto-refresh]");
    if (autoRefresh) {
        const interval = Number(autoRefresh.dataset.autoRefresh || 10000);
        setTimeout(() => window.location.reload(), interval);
    }
});
