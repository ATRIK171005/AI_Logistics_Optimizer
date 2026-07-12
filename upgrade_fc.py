import re

def upgrade_demand_forecaster():
    with open('orig_demand_forecaster.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add Toast HTML right after <body...>
    toast_html = """
<!-- Toast Notification -->
<div id="toast-notification" class="fixed bottom-6 right-6 z-50 bg-[#00243D]/95 border border-[#00E5FF] shadow-[0_0_25px_rgba(0,229,255,0.4)] backdrop-blur-md px-6 py-4 rounded-xl flex items-center gap-3 transition-all duration-400 opacity-0 pointer-events-none translate-y-5">
    <span class="material-symbols-outlined text-[#00E5FF] animate-pulse">check_circle</span>
    <div>
        <p id="toast-title" class="font-bold text-sm text-[#00E5FF] font-mono-kpi">⚡ XGBoost Ensemble Retrained</p>
        <p id="toast-msg" class="text-xs text-gray-300">Forecast updated across 12 regional customer clusters.</p>
    </div>
</div>
"""
    html = re.sub(r'(<body[^>]*>)', r'\1' + toast_html, html, count=1)

    # Add toast css to style
    toast_css = """
        #toast-notification.show {
            opacity: 1 !important;
            transform: translateY(0) !important;
            pointer-events: auto !important;
        }
    </style>
"""
    html = html.replace('</style>', toast_css)

    # 2. Update Nav Links & Buttons
    html = html.replace('<button class="bg-primary-container text-on-primary-container px-sm py-xs rounded-lg font-bold hover:scale-105 transition-transform">Run Optimization Engine</button>',
                        '<button onclick="runForecastSimulation()" class="bg-primary-container text-on-primary-container px-sm py-xs rounded-lg font-bold hover:scale-105 transition-transform shadow-[0_0_15px_rgba(0,229,255,0.4)] flex items-center gap-1.5"><span class="material-symbols-outlined text-sm">bolt</span> Run Optimization Engine</button>')
    
    html = html.replace('<button class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md">',
                        '<button onclick="resetForecast()" class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md shadow-sm font-semibold">')

    # Side nav links
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*hub.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold" href="dashboard_preview.html"><span class="material-symbols-outlined">hub</span><span class="font-body-md text-body-md">Network Topology</span></a>', html, flags=re.DOTALL)
    
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2[^>]*href="[^"]*"',
                  '<a class="flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2 border-primary-fixed-dim bg-primary-container/10 hover:bg-primary-container/5 transition-all font-semibold" href="demand_forecaster.html"', html)
    
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*local_shipping.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold" href="cvrp_explorer.html"><span class="material-symbols-outlined">local_shipping</span><span class="font-body-md text-body-md">CVRP Dispatcher</span></a>', html, flags=re.DOTALL)

    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*analytics.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold cursor-pointer" onclick="showToast(\'Cost Spend Analytics\', \'Predicted demand variance saves ~14% on emergency spot rates.\')"><span class="material-symbols-outlined">analytics</span><span class="font-body-md text-body-md">Cost Analytics</span></a>', html, flags=re.DOTALL)

    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*history.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold cursor-pointer" onclick="showToast(\'Audit Trail Verified\', \'120 historical monthly demand tuples synced from SQLite.\')"><span class="material-symbols-outlined">history</span><span class="font-body-md text-body-md">Audit Logs</span></a>', html, flags=re.DOTALL)

    # 3. Add IDs to Model Selector Pills
    html = html.replace('<button class="px-sm py-1 rounded-full bg-primary-container text-on-primary-container text-xs font-bold flex items-center gap-xs shadow-sm">',
                        '<button id="pill-xgb" onclick="switchModel(\'xgb\')" class="px-sm py-1 rounded-full bg-primary-container text-on-primary-container text-xs font-bold flex items-center gap-xs shadow-sm">')
    html = html.replace('<button class="px-sm py-1 rounded-full bg-surface-variant/40 hover:bg-surface-variant text-on-surface-variant text-xs transition-colors">Random Forest</button>',
                        '<button id="pill-rf" onclick="switchModel(\'rf\')" class="px-sm py-1 rounded-full bg-surface-variant/40 hover:bg-surface-variant text-on-surface-variant text-xs transition-colors">Random Forest</button>')
    html = html.replace('<button class="px-sm py-1 rounded-full bg-surface-variant/40 hover:bg-surface-variant text-on-surface-variant text-xs transition-colors">Baseline Linear</button>',
                        '<button id="pill-lin" onclick="switchModel(\'lin\')" class="px-sm py-1 rounded-full bg-surface-variant/40 hover:bg-surface-variant text-on-surface-variant text-xs transition-colors">Baseline Linear</button>')

    # 4. Add IDs to KPI metrics
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">0.842</h3>', '<h3 id="kpi-rmse" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">0.842</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">0.615</h3>', '<h3 id="kpi-mae" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">0.615</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">4.2%</h3>', '<h3 id="kpi-mape" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">4.2%</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">0.96</h3>', '<h3 id="kpi-r2-fc" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">0.96</h3>')

    # 5. Add IDs to Simulation Sliders & Update Button
    html = html.replace('<span class="font-mono-label text-primary-fixed-dim">1.05</span>', '<span id="disp-sales" class="font-mono-label text-primary-fixed-dim font-bold">1.05</span>')
    html = html.replace('<input class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" type="range"/>', '<input id="slider-sales-fc" oninput="document.getElementById(\'disp-sales\').innerText=parseFloat(this.value).toFixed(2)" class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" min="0.80" max="1.50" step="0.01" value="1.05" type="range"/>', 1)
    
    html = html.replace('<button class="w-full py-sm bg-primary-container text-on-primary-container font-bold rounded-lg shadow-[0_0_20px_rgba(0,229,255,0.4)] hover:shadow-[0_0_30px_rgba(0,229,255,0.6)] transition-all flex items-center justify-center gap-sm mt-md group">',
                        '<button id="btn-update-fc" onclick="runForecastSimulation()" class="w-full py-sm bg-primary-container text-on-primary-container font-bold rounded-lg shadow-[0_0_20px_rgba(0,229,255,0.4)] hover:shadow-[0_0_30px_rgba(0,229,255,0.6)] transition-all flex items-center justify-center gap-sm mt-md group">')

    # Add ID to prediction curve in SVG if present
    html = re.sub(r'(<path[^>]*d="M\s*500,140\s*L.*?)"', r'\1" id="svg-pred-line"', html, count=1)

    # 6. Replace script controller at bottom
    new_script = """<script>
    let currentModel = 'xgb';

    function showToast(title, message) {
        const toast = document.getElementById('toast-notification');
        if (!toast) return;
        document.getElementById('toast-title').innerText = '⚡ ' + title;
        document.getElementById('toast-msg').innerText = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3800);
    }

    function switchModel(model) {
        currentModel = model;
        const pills = {'xgb': 'pill-xgb', 'rf': 'pill-rf', 'lin': 'pill-lin'};
        const titles = {'xgb': 'XGBoost Regressor (Active)', 'rf': 'Random Forest (Active)', 'lin': 'Baseline Linear (Active)'};
        const paths = {
            'xgb': 'M 500,140 L 550,110 L 600,150 L 650,80 L 700,130 L 750,70 L 800,100 L 850,40 L 900,80 L 950,20',
            'rf': 'M 500,140 L 550,120 L 600,145 L 650,95 L 700,125 L 750,85 L 800,105 L 850,55 L 900,85 L 950,40',
            'lin': 'M 500,140 L 550,130 L 600,120 L 650,110 L 700,100 L 750,90 L 800,80 L 850,70 L 900,60 L 950,50'
        };
        const metrics = {
            'xgb': {rmse: '0.842', mae: '0.615', mape: '4.2%', r2: '0.96'},
            'rf': {rmse: '0.914', mae: '0.680', mape: '4.8%', r2: '0.93'},
            'lin': {rmse: '1.450', mae: '1.120', mape: '8.5%', r2: '0.81'}
        };

        for (let k in pills) {
            const el = document.getElementById(pills[k]);
            if (!el) continue;
            if (k === model) {
                el.className = 'px-sm py-1 rounded-full bg-primary-container text-on-primary-container text-xs font-bold flex items-center gap-xs shadow-sm';
                el.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-on-primary-container animate-pulse"></span> ' + titles[k];
            } else {
                el.className = 'px-sm py-1 rounded-full bg-surface-variant/40 hover:bg-surface-variant text-on-surface-variant text-xs transition-colors';
                el.innerHTML = k === 'xgb' ? 'XGBoost Regressor' : (k === 'rf' ? 'Random Forest' : 'Baseline Linear');
            }
        }

        const pEl = document.getElementById('svg-pred-line');
        if (pEl && paths[model]) pEl.setAttribute('d', paths[model]);
        
        const kRmse = document.getElementById('kpi-rmse');
        const kMae = document.getElementById('kpi-mae');
        const kMape = document.getElementById('kpi-mape');
        const kR2 = document.getElementById('kpi-r2-fc');
        if (kRmse) kRmse.innerText = metrics[model].rmse;
        if (kMae) kMae.innerText = metrics[model].mae;
        if (kMape) kMape.innerText = metrics[model].mape;
        if (kR2) kR2.innerText = metrics[model].r2;

        showToast('ML Kernel Switched', 'Active forecasting engine shifted to ' + titles[model]);
    }

    function runForecastSimulation() {
        const btn = document.getElementById('btn-update-fc');
        if (btn) {
            btn.innerHTML = '<span class="material-symbols-outlined animate-spin text-sm">refresh</span> Retraining Trees...';
            btn.disabled = true;
        }

        const salesVal = parseFloat(document.getElementById('slider-sales-fc')?.value || 1.05);

        setTimeout(() => {
            const kRmse = document.getElementById('kpi-rmse');
            const kR2 = document.getElementById('kpi-r2-fc');
            if (kRmse) kRmse.innerText = (0.842 * (1.05/salesVal)).toFixed(3);
            if (kR2) kR2.innerText = '0.98';

            const pEl = document.getElementById('svg-pred-line');
            if (pEl) {
                const offset = Math.round((salesVal - 1.05) * 40);
                const newPath = `M 500,${140-offset} L 550,${110-offset} L 600,${150-offset} L 650,${80-offset} L 700,${130-offset} L 750,${70-offset} L 800,${100-offset} L 850,${40-offset} L 900,${80-offset} L 950,${20-offset}`;
                pEl.setAttribute('d', newPath);
            }

            if (btn) {
                btn.innerHTML = '<span class="material-symbols-outlined group-hover:rotate-180 transition-transform duration-700">bolt</span> Update Forecast';
                btn.disabled = false;
            }
            showToast('Forecast Converged', 'XGBoost multi-horizon predictions updated across 12 regional clusters.');
        }, 600);
    }

    function resetForecast() {
        const sSales = document.getElementById('slider-sales-fc');
        if (sSales) sSales.value = 1.05;
        const vSales = document.getElementById('disp-sales');
        if (vSales) vSales.innerText = '1.05';
        switchModel('xgb');
        showToast('Reset Complete', 'Macro indices restored to base Q4 values.');
    }
</script>
</body>"""
    html = re.sub(r'<script>\s*// Micro-interactions.*?</body>', new_script, html, flags=re.DOTALL)
    
    with open('demand_forecaster.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully restored & upgraded demand_forecaster.html!")

upgrade_demand_forecaster()
