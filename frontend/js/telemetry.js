/**
 * UNEX OS - Real-time Hardware & Desktop Telemetry Poller
 */
class TelemetryManager {
    constructor() {
        this.metricsInterval = null;
        this.windowInterval = null;
        this.securityInterval = null;
        this.init();
    }

    init() {
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);

        this.pollMetrics();
        this.pollActiveWindow();
        this.pollSecurityPending();
        this.pollAuditLogs();
        this.pollMemories();

        // Loop intervals
        setInterval(() => this.pollMetrics(), 2000);
        setInterval(() => this.pollActiveWindow(), 1500);
        setInterval(() => this.pollSecurityPending(), 1500);
    }

    updateClock() {
        const timeEl = document.getElementById('live-time');
        if (timeEl) {
            const now = new Date();
            timeEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        }
    }

    async pollMetrics() {
        try {
            const res = await fetch('/api/metrics');
            if (!res.ok) return;
            const data = await res.json();

            // CPU
            if (data.cpu) {
                const cpuPct = data.cpu.percent || 0;
                document.getElementById('cpu-val').textContent = `${cpuPct}%`;
                document.getElementById('cpu-bar').style.width = `${Math.min(100, cpuPct)}%`;
            }

            // RAM
            if (data.memory) {
                const usedGb = (data.memory.used_mb / 1024).toFixed(1);
                const totalGb = (data.memory.total_mb / 1024).toFixed(1);
                const memPct = data.memory.percent || 0;
                document.getElementById('ram-val').textContent = `${usedGb} / ${totalGb} GB`;
                document.getElementById('ram-bar').style.width = `${Math.min(100, memPct)}%`;
            }

            // GPU
            if (data.gpu && data.gpu.length > 0) {
                const gpu = data.gpu[0];
                document.getElementById('gpu-device-name').textContent = gpu.name.replace('NVIDIA GeForce ', '').replace(' Laptop GPU', '');
                const usedGb = (gpu.memory_used_mb / 1024).toFixed(1);
                const totalGb = (gpu.memory_total_mb / 1024).toFixed(1);
                const vramPct = gpu.memory_percent || 0;
                document.getElementById('vram-val').textContent = `${usedGb} / ${totalGb} GB`;
                document.getElementById('vram-bar').style.width = `${Math.min(100, Math.max(5, vramPct))}%`;
            }
        } catch (e) {
            // Silently handle transient network disconnect
        }
    }

    async pollActiveWindow() {
        try {
            const res = await fetch('/api/desktop/active-window');
            if (!res.ok) return;
            const data = await res.json();
            const win = data.active_window;

            if (win) {
                document.getElementById('win-title').textContent = win.title || 'Untitled Window';
                document.getElementById('win-pid').textContent = win.pid || '-';
                document.getElementById('win-proc').textContent = win.process_name || 'unknown';
                document.getElementById('win-quadrant').textContent = win.quadrant || 'center';
                document.getElementById('win-coords').textContent = `Bounds: (${win.left}, ${win.top}) — ${win.width}x${win.height}`;
            }
        } catch (e) {
            // Transient fetch failure
        }
    }

    async pollSecurityPending() {
        try {
            const res = await fetch('/api/security/pending');
            if (!res.ok) return;
            const data = await res.json();
            const banner = document.getElementById('approval-banner');

            if (data.pending) {
                const p = data.pending;
                document.getElementById('approval-title').textContent = `${p.risk_level} Risk Action Requires Confirmation`;
                document.getElementById('approval-tool').textContent = p.tool_name;
                document.getElementById('approval-args').textContent = JSON.stringify(p.tool_args);
                banner.style.display = 'flex';
            } else {
                banner.style.display = 'none';
            }
        } catch (e) {
            // Ignore
        }
    }

    async pollAuditLogs() {
        try {
            const res = await fetch('/api/audit/logs?limit=8');
            if (!res.ok) return;
            const data = await res.json();
            const container = document.getElementById('audit-items');

            if (data.logs && data.logs.length > 0) {
                container.innerHTML = data.logs.map(log => {
                    const riskClass = `risk-${(log.risk_level || 'low').toLowerCase()}`;
                    const time = log.timestamp ? log.timestamp.split('T')[1].split('.')[0] : '';
                    return `
                        <div class="audit-row">
                            <span class="audit-time">${time}</span>
                            <span class="audit-tool">${log.tool_name}</span>
                            <span class="audit-risk ${riskClass}">${log.risk_level}</span>
                            <span class="audit-status">${log.status}</span>
                        </div>
                    `;
                }).join('');
            }
        } catch (e) {
            // Ignore
        }
    }

    async pollMemories() {
        try {
            const res = await fetch('/api/memory');
            if (!res.ok) return;
            const memories = await res.json();
            const container = document.getElementById('memory-items');

            if (Array.isArray(memories) && memories.length > 0) {
                container.innerHTML = memories.slice(0, 10).map(m => {
                    return `
                        <div class="memory-pill">
                            <span class="memory-type-tag">[${m.memory_type}]</span>
                            <span>${m.content}</span>
                        </div>
                    `;
                }).join('');
            } else {
                container.innerHTML = '<div class="drawer-empty-state">No long-term memories indexed yet.</div>';
            }
        } catch (e) {
            // Ignore
        }
    }
}

window.TelemetryManager = TelemetryManager;
