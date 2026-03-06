import gradio as gr
import subprocess
import shutil


def get_gpu_stats(*args):
    if not shutil.which("nvidia-smi"):
        return {"hasNvidiaSmi": False, "gpus": []}

    try:
        cmd = "nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used,power.draw,power.limit,clocks.current.graphics,clocks.current.memory,fan.speed --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd, shell=True, text=True)
        
        gpus = []
        for line in output.strip().split('\n'):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 13:
                gpus.append({
                    "index": int(parts[0]), "name": parts[1], "temperature": int(parts[2]),
                    "utilization": {"gpu": int(parts[3]), "memory": int(parts[4])},
                    "memory": {"total": int(parts[5]), "free": int(parts[6]), "used": int(parts[7])},
                    "power": {"draw": float(parts[8]), "limit": float(parts[9])},
                    "clocks": {"graphics": int(parts[10]), "memory": int(parts[11])},
                    "fan": {"speed": int(parts[12]) if parts[12].isdigit() else 0}
                })
        return {"hasNvidiaSmi": True, "gpus": gpus, "error": None}
    except Exception as e:
        return {"hasNvidiaSmi": False, "gpus": [], "error": str(e)}

class GPUMonitor(gr.HTML):
    def __init__(self, update_interval=1000, show_last_updated=True, **kwargs):
        html_template = """
        <div class="gpu-monitor-container">
            <div class="gpu-header">
                <h1 class="gpu-title">GPU Monitor</h1>
                ${show_last_updated === 'true' ? `<div class="gpu-time">Last updated: <span id="gpu-time-val">Loading...</span></div>` : ''}
            </div>
            <div id="gpu-alert"></div>
            <div id="gpu-root" class="gpu-grid"></div>
        </div>
        """
        
        css_template = """
            .gpu-monitor-container {
                font-family: "Inter", sans-serif;
                width: 100%;
            }

            .gpu-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }

            .gpu-title {
                font-size: 1.125rem;
                margin: 0;
                font-weight: 500;
                color: var(--body-text-color);
            }

            .gpu-time {
                font-size: 0.75rem;
                color: var(--body-text-color-subdued);
            }

            .gpu-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 1rem;
            }

            .gpu-card {
                background-color: var(--background-fill-secondary);
                border-radius: 0.75rem;
                box-shadow: var(--shadow-drop-md);
                border: 1px solid var(--border-color-primary);
                overflow: hidden;
                transition: box-shadow 0.3s ease;
            }

            .gpu-card:hover {
                box-shadow: var(--shadow-drop-lg);
            }

            .gpu-card-header {
                background-color: var(--background-fill-primary);
                padding: 0.75rem 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border-color-primary);
            }

            .gpu-name {
                font-weight: 600;
                color: var(--body-text-color);
                margin: 0;
                font-size: 0.9rem;
            }

            .gpu-badge {
                padding: 0.125rem 0.5rem;
                background-color: var(--background-fill-secondary);
                border-radius: 9999px;
                font-size: 0.75rem;
                color: var(--body-text-color);
            }

            .gpu-body {
                padding: 1rem;
            }

            .gpu-metrics-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
            }

            .metric-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 0.75rem;
            }

            .metric-label {
                font-size: 0.75rem;
                color: var(--body-text-color-subdued);
                margin: 0;
            }

            .metric-value {
                font-size: 0.875rem;
                font-weight: 500;
                margin: 0;
                color: var(--body-text-color);
            }

            .progress-header {
                display: flex;
                align-items: center;
                margin-bottom: 0.25rem;
            }

            .progress-header span {
                margin-left: auto;
                font-size: 0.75rem;
                color: var(--body-text-color);
            }

            .progress-track {
                width: 100%;
                background-color: var(--neutral-200);
                border-radius: 9999px;
                height: 0.35rem;
                margin-bottom: 0.75rem;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                border-radius: 9999px;
                transition:
                    width 0.3s ease,
                    background-color 0.3s ease;
            }

            .progress-footer {
                font-size: 0.75rem;
                color: var(--body-text-color-subdued);
                margin-top: -0.5rem;
            }

            .gpu-footer {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                padding-top: 0.5rem;
                margin-top: 0.5rem;
                border-top: 1px solid var(--border-color-primary);
            }

            .text-emerald-500 {
                color: #10b981 !important;
                stroke: #10b981 !important;
            }

            .bg-emerald-500 {
                background-color: #10b981 !important;
            }

            .text-amber-500 {
                color: #f59e0b !important;
                stroke: #f59e0b !important;
            }

            .bg-amber-500 {
                background-color: #f59e0b !important;
            }

            .text-rose-500 {
                color: #f43f5e !important;
                stroke: #f43f5e !important;
            }

            .bg-rose-500 {
                background-color: #f43f5e !important;
            }

            .text-blue-500 {
                color: #3b82f6 !important;
                stroke: #3b82f6 !important;
            }

            .bg-blue-500 {
                background-color: #3b82f6 !important;
            }

            .text-purple-500 {
                color: #a855f7 !important;
                stroke: #a855f7 !important;
            }

            .icon-muted {
                color: var(--body-text-color-subdued) !important;
                stroke: var(--body-text-color-subdued) !important;
            }

            .icon {
                width: 16px;
                height: 16px;
                stroke-width: 2.2;
            }

            .alert-box {
                background-color: rgba(245, 158, 11, 0.1);
                border: 1px solid #f59e0b;
                color: #d97706;
                padding: 0.75rem 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
                font-size: 0.875rem;
            }
        """

        js_on_load = """
        const root = element.querySelector("#gpu-root");
        const timeVal = element.querySelector("#gpu-time-val");
        const alertBox = element.querySelector("#gpu-alert");
        let renderedGpuCount = -1;

        const MOCK_DATA = {
        hasNvidiaSmi: false,
        isMock: true,
        gpus: [
            {
            index: 0,
            name: "NVIDIA GeForce RTX 4090 (Demo)",
            temperature: 55,
            fan: { speed: 35 },
            utilization: { gpu: 42, memory: 30 },
            memory: { total: 24576, used: 8192 },
            power: { draw: 150.5, limit: 450.0 },
            clocks: { graphics: 2520 },
            },
            {
            index: 1,
            name: "NVIDIA GeForce RTX 4090 (Demo)",
            temperature: 38,
            fan: { speed: 0 },
            utilization: { gpu: 0, memory: 5 },
            memory: { total: 24576, used: 1024 },
            power: { draw: 30.0, limit: 450.0 },
            clocks: { graphics: 210 },
            },
        ],
        };

        const formatMemory = (mb) =>
        mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb} MB`;
        const getUtilColor = (val) =>
        val < 30 ? "bg-emerald-500" : val < 70 ? "bg-amber-500" : "bg-rose-500";
        const getTempColor = (temp) =>
        temp < 50
            ? "text-emerald-500"
            : temp < 80
            ? "text-amber-500"
            : "text-rose-500";

        function initLucide(retries = 8, delay = 200) {
        if (window.lucide) {
            window.lucide.createIcons({ root: root });
        } else if (retries > 0) {
            setTimeout(() => initLucide(retries - 1, delay), delay);
        }
        }

        const generateGPUCard = (gpu) => `
                    <div class="gpu-card" id="gpu-card-${gpu.index}">
                        <div class="gpu-card-header">
                            <h2 class="gpu-name">${gpu.name}</h2>
                            <span class="gpu-badge"># ${gpu.index}</span>
                        </div>
                        <div class="gpu-body">
                            <div class="gpu-metrics-grid">
                                <div>
                                    <div class="metric-item">
                                        <i data-lucide="thermometer" id="icon-temp-${gpu.index}" class="icon ${getTempColor(gpu.temperature)}"></i>
                                        <div><p class="metric-label">Temperature</p><p class="metric-value ${getTempColor(gpu.temperature)}" id="val-temp-${gpu.index}">${gpu.temperature}°C</p></div>
                                    </div>
                                    <div class="metric-item">
                                        <i data-lucide="fan" class="icon text-blue-500"></i>
                                        <div><p class="metric-label">Fan Speed</p><p class="metric-value text-blue-500" id="val-fan-${gpu.index}">${gpu.fan.speed}%</p></div>
                                    </div>
                                </div>
                                <div>
                                    <div class="progress-header"><i data-lucide="cpu" class="icon icon-muted" style="margin-right:4px;"></i><p class="metric-label">GPU Load</p><span id="val-util-${gpu.index}">${gpu.utilization.gpu}%</span></div>
                                    <div class="progress-track"><div id="bar-util-${gpu.index}" class="progress-fill ${getUtilColor(gpu.utilization.gpu)}" style="width: ${gpu.utilization.gpu}%"></div></div>
                                    <div class="progress-header" style="margin-top: 12px;"><i data-lucide="hard-drive" class="icon text-blue-500" style="margin-right:4px;"></i><p class="metric-label">Memory</p><span id="val-mem-pct-${gpu.index}">${((gpu.memory.used / gpu.memory.total) * 100).toFixed(1)}%</span></div>
                                    <div class="progress-track"><div id="bar-mem-${gpu.index}" class="progress-fill bg-blue-500" style="width: ${(gpu.memory.used / gpu.memory.total) * 100}%"></div></div>
                                    <p class="progress-footer" id="val-mem-text-${gpu.index}">${formatMemory(gpu.memory.used)} / ${formatMemory(gpu.memory.total)}</p>
                                </div>
                            </div>
                            <div class="gpu-footer">
                                <div class="metric-item" style="margin:0"><i data-lucide="clock" class="icon text-purple-500"></i><div><p class="metric-label">Clock Speed</p><p class="metric-value" id="val-clock-${gpu.index}">${gpu.clocks.graphics} MHz</p></div></div>
                                <div class="metric-item" style="margin:0"><i data-lucide="zap" class="icon text-amber-500"></i><div><p class="metric-label">Power Draw</p><p class="metric-value"><span id="val-power-${gpu.index}">${gpu.power.draw.toFixed(1)}</span>W <span style="font-size:0.7rem; color:var(--body-text-color-subdued)">/ ${gpu.power.limit}W</span></p></div></div>
                            </div>
                        </div>
                    </div>
                `;

        function updateGpuDOM(gpus) {
        gpus.forEach((gpu) => {
            const els = {
            t: document.getElementById(`val-temp-${gpu.index}`),
            f: document.getElementById(`val-fan-${gpu.index}`),
            u: document.getElementById(`val-util-${gpu.index}`),
            mp: document.getElementById(`val-mem-pct-${gpu.index}`),
            mt: document.getElementById(`val-mem-text-${gpu.index}`),
            c: document.getElementById(`val-clock-${gpu.index}`),
            p: document.getElementById(`val-power-${gpu.index}`),
            ub: document.getElementById(`bar-util-${gpu.index}`),
            mb: document.getElementById(`bar-mem-${gpu.index}`),
            it: document.getElementById(`icon-temp-${gpu.index}`),
            };
            if (els.t) els.t.innerText = `${gpu.temperature}°C`;
            if (els.f) els.f.innerText = `${gpu.fan.speed}%`;
            if (els.u) els.u.innerText = `${gpu.utilization.gpu}%`;
            if (els.mp)
            els.mp.innerText = `${((gpu.memory.used / gpu.memory.total) * 100).toFixed(1)}%`;
            if (els.mt)
            els.mt.innerText = `${formatMemory(gpu.memory.used)} / ${formatMemory(gpu.memory.total)}`;
            if (els.c) els.c.innerText = `${gpu.clocks.graphics} MHz`;
            if (els.p) els.p.innerText = `${gpu.power.draw.toFixed(1)}`;
            if (els.ub) {
            els.ub.style.width = `${gpu.utilization.gpu}%`;
            els.ub.className = `progress-fill ${getUtilColor(gpu.utilization.gpu)}`;
            }
            if (els.mb)
            els.mb.style.width = `${(gpu.memory.used / gpu.memory.total) * 100}%`;
            if (els.it)
            els.it.setAttribute(
                "class",
                `lucide lucide-thermometer icon ${getTempColor(gpu.temperature)}`,
            );
            if (els.t)
            els.t.className = `metric-value ${getTempColor(gpu.temperature)}`;
        });
        }

        async function fetchAndUpdate() {
        let data;
        try {
            if (typeof server !== "undefined" && server.get_gpu_stats) {
            data = await server.get_gpu_stats();
            } else {
            data = MOCK_DATA;
            }

            if (timeVal) timeVal.innerText = new Date().toLocaleTimeString();

            if (!data.hasNvidiaSmi) {
            if (data.error)
                alertBox.innerHTML = `<div class="alert-box"><strong>Nota:</strong> ${data.error}</div>`;
            if (!data.isMock) data = MOCK_DATA;
            }

            if (data.gpus && data.gpus.length > 0) {
            if (data.gpus.length !== renderedGpuCount) {
                root.innerHTML = data.gpus.map((gpu) => generateGPUCard(gpu)).join("");
                initLucide();
                renderedGpuCount = data.gpus.length;
            } else {
                updateGpuDOM(data.gpus);
            }
            }
        } catch (error) {
            console.error("Fetch GPU error:", error);
            if (renderedGpuCount === -1) {
            root.innerHTML = MOCK_DATA.gpus
                .map((gpu) => generateGPUCard(gpu))
                .join("");
            initLucide();
            renderedGpuCount = MOCK_DATA.gpus.length;
            }
        }
        }

        fetchAndUpdate();
        const intervalId = setInterval(fetchAndUpdate, props.update_interval);
        return () => clearInterval(intervalId);

        """

        super().__init__(
            html_template=html_template, 
            css_template=css_template, 
            js_on_load=js_on_load, 
            server_functions=[get_gpu_stats],
            update_interval=update_interval,
            show_last_updated=str(show_last_updated).lower(),
            **kwargs
        )
    
    def api_info(self): return {"type": "null"}