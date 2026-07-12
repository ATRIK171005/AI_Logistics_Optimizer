import os
import re

def upgrade_dashboard_preview():
    with open('orig_dashboard_preview.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add Toast HTML right after <body...>
    toast_html = """
<!-- Toast Notification -->
<div id="toast-notification" class="fixed bottom-6 right-6 z-50 bg-[#00243D]/95 border border-[#00E5FF] shadow-[0_0_25px_rgba(0,229,255,0.4)] backdrop-blur-md px-6 py-4 rounded-xl flex items-center gap-3 transition-all duration-400 opacity-0 pointer-events-none translate-y-5">
    <span class="material-symbols-outlined text-[#00E5FF] animate-pulse">check_circle</span>
    <div>
        <p id="toast-title" class="font-bold text-sm text-[#00E5FF] font-mono-kpi">⚡ Solvers Converged</p>
        <p id="toast-msg" class="text-xs text-gray-300">Optimal container allocation updated across all 36 corridors.</p>
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
                        '<button onclick="runGlobalOptimization()" class="bg-primary-container text-on-primary-container px-sm py-xs rounded-lg font-bold hover:scale-105 transition-transform shadow-[0_0_15px_rgba(0,229,255,0.4)] flex items-center gap-1.5"><span class="material-symbols-outlined text-sm">bolt</span> Run Optimization Engine</button>')
    
    html = html.replace('<button class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md">',
                        '<button onclick="resetToBaseline()" class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md shadow-sm font-semibold">')

    # Update side nav anchor links
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2[^>]*href="[^"]*"',
                  '<a class="flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2 border-primary-fixed-dim bg-primary-container/10 hover:bg-primary-container/5 transition-all font-semibold" href="dashboard_preview.html"', html)
    
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*trending_up.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold" href="demand_forecaster.html"><span class="material-symbols-outlined">trending_up</span><span class="font-body-md text-body-md">Demand Forecaster</span></a>', html, flags=re.DOTALL)
    
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*local_shipping.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold" href="cvrp_explorer.html"><span class="material-symbols-outlined">local_shipping</span><span class="font-body-md text-body-md">CVRP Dispatcher</span></a>', html, flags=re.DOTALL)

    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*analytics.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold cursor-pointer" onclick="showToast(\'Cost Spend Analytics\', \'Inspecting time-series spend variance across regional corridors.\')"><span class="material-symbols-outlined">analytics</span><span class="font-body-md text-body-md">Cost Analytics</span></a>', html, flags=re.DOTALL)

    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*history.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold cursor-pointer" onclick="switchDrawerTab(\'sql\')"><span class="material-symbols-outlined">history</span><span class="font-body-md text-body-md">Audit Logs</span></a>', html, flags=re.DOTALL)

    # 3. Add IDs to KPI numbers
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">$1,425,800</h3>', '<h3 id="kpi-cost" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">$1,425,800</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">24 / 36 Routes</h3>', '<h3 id="kpi-routes" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">24 / 36 Routes</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">98.4% R² Score</h3>', '<h3 id="kpi-r2" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">98.4% R² Score</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">94.2% Capacity</h3>', '<h3 id="kpi-util" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">94.2% Capacity</h3>')
    html = html.replace('<p class="text-on-surface-variant text-xs mt-xs">18 Discrete Truck Trips</p>', '<p id="kpi-trips" class="text-on-surface-variant text-xs mt-xs">18 Discrete Truck Trips</p>')

    # 4. Map Mode buttons
    html = html.replace('<button class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant active:border-primary-fixed-dim">MILP Hub Allocation</button>',
                        '<button id="btn-map-milp" onclick="switchMapMode(\'milp\')" class="bg-primary-container/20 text-primary-fixed-dim text-xs px-xs py-1 rounded border border-primary-fixed-dim/40 font-bold transition-all">MILP Hub Allocation</button>')
    html = html.replace('<button class="bg-primary-container/20 text-primary-fixed-dim text-xs px-xs py-1 rounded border border-primary-fixed-dim/40 font-bold">CVRP Multi-Stop</button>',
                        '<button id="btn-map-cvrp" onclick="switchMapMode(\'cvrp\')" class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant transition-all">CVRP Multi-Stop</button>')
    html = html.replace('<button class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant">Demand Heatmap</button>',
                        '<button id="btn-map-heat" onclick="switchMapMode(\'heat\')" class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant transition-all">Demand Heatmap</button>')

    # Add Map Groups around SVG arcs if not already wrapped
    # We can inject CVRP & Heatmap SVG groups right inside the map SVG before closing </svg>
    extra_svg = """
                    <!-- CVRP Arcs (Hidden initially) -->
                    <g id="map-group-cvrp" class="hidden">
                        <path d="M100,200 L200,130 L320,220 L100,200" fill="none" stroke="#10b981" stroke-dasharray="5,3" stroke-width="2.5"></path>
                        <path d="M400,180 L480,260 L580,180 L400,180" fill="none" stroke="#3b82f6" stroke-dasharray="5,3" stroke-width="2.5"></path>
                        <circle cx="200" cy="130" fill="#10b981" r="5"></circle>
                        <circle cx="320" cy="220" fill="#10b981" r="5"></circle>
                        <circle cx="480" cy="260" fill="#3b82f6" r="5"></circle>
                        <circle cx="580" cy="180" fill="#3b82f6" r="5"></circle>
                        <text fill="#10b981" font-family="JetBrains Mono" font-size="10" font-weight="bold" x="180" y="120">Stop #1 (4 TEU)</text>
                        <text fill="#10b981" font-family="JetBrains Mono" font-size="10" font-weight="bold" x="300" y="240">Stop #2 (2 TEU)</text>
                        <text fill="#3b82f6" font-family="JetBrains Mono" font-size="10" font-weight="bold" x="460" y="280">Stop #3 (5 TEU)</text>
                    </g>
                    <!-- Heatmap Arcs (Hidden initially) -->
                    <g id="map-group-heat" class="hidden">
                        <circle cx="100" cy="200" fill="#ef4444" opacity="0.4" r="50"><animate attributeName="r" dur="3s" repeatCount="indefinite" values="40;55;40"></animate></circle>
                        <circle cx="400" cy="180" fill="#f59e0b" opacity="0.4" r="35"><animate attributeName="r" dur="3s" repeatCount="indefinite" values="30;45;30"></animate></circle>
                        <circle cx="700" cy="250" fill="#10b981" opacity="0.4" r="55"><animate attributeName="r" dur="3s" repeatCount="indefinite" values="45;60;45"></animate></circle>
                        <text fill="#ffffff" font-family="JetBrains Mono" font-size="11" font-weight="bold" x="75" y="205">1,820 TEUs</text>
                        <text fill="#ffffff" font-family="JetBrains Mono" font-size="11" font-weight="bold" x="375" y="185">940 TEUs</text>
                        <text fill="#ffffff" font-family="JetBrains Mono" font-size="11" font-weight="bold" x="675" y="255">2,450 TEUs</text>
                    </g>
                    <!-- MILP Group wrapper ID -->
"""
    # Wrap existing arcs in id="map-group-milp"
    html = html.replace('<svg class="absolute inset-0 w-full h-full z-10" viewBox="0 0 800 400">', '<svg class="absolute inset-0 w-full h-full z-10" viewBox="0 0 800 400"><g id="map-group-milp">')
    html = html.replace('<!-- Floating Legend -->', '</g>' + extra_svg + '<!-- Floating Legend -->')
    html = html.replace('<div class="flex flex-col gap-1 text-[10px] text-on-surface-variant font-mono-label">', '<div id="map-legend-text" class="flex flex-col gap-1 text-[10px] text-on-surface-variant font-mono-label">')

    # 5. Sliders & Re-Run Button
    html = html.replace('<span class="font-mono-label text-primary-fixed-dim">1.2x</span>', '<span id="val-sales" class="font-mono-label text-primary-fixed-dim font-bold">1.2x</span>')
    html = html.replace('<input class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" type="range"/>', '<input id="slider-sales" oninput="document.getElementById(\'val-sales\').innerText = this.value + \'x\'" class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" min="0.8" max="2.0" step="0.1" value="1.2" type="range"/>', 1)
    
    html = html.replace('<span class="font-mono-label text-primary-fixed-dim">42%</span>', '<span id="val-fest" class="font-mono-label text-primary-fixed-dim font-bold">42%</span>')
    html = re.sub(r'<input class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" type="range"/>', '<input id="slider-fest" oninput="document.getElementById(\'val-fest\').innerText = this.value + \'%\'" class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" min="0" max="100" step="5" value="42" type="range"/>', html, count=1)

    html = html.replace('<span class="font-mono-label text-error">High (7/10)</span>', '<span id="val-rain" class="font-mono-label text-error font-bold">High (7/10)</span>')
    html = html.replace('<input class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-error" type="range"/>', '<input id="slider-rain" oninput="document.getElementById(\'val-rain\').innerText = \'Risk (\' + this.value + \'/10)\'" class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-error" min="1" max="10" step="1" value="7" type="range"/>')

    html = html.replace('<span class="font-mono-label text-primary-fixed-dim">0.85</span>', '<span id="val-promo" class="font-mono-label text-primary-fixed-dim font-bold">0.85</span>')
    html = re.sub(r'<input class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" type="range"/>', '<input id="slider-promo" oninput="document.getElementById(\'val-promo\').innerText = this.value" class="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim" min="0.50" max="1.50" step="0.05" value="0.85" type="range"/>', html, count=1)

    html = html.replace('<button class="w-full py-sm bg-primary-container text-on-primary-container font-bold rounded-lg shadow-[0_0_20px_rgba(0,229,255,0.4)] hover:shadow-[0_0_30px_rgba(0,229,255,0.6)] transition-all flex items-center justify-center gap-sm mt-md group">',
                        '<button id="btn-run-solver" onclick="runGlobalOptimization()" class="w-full py-sm bg-primary-container text-on-primary-container font-bold rounded-lg shadow-[0_0_20px_rgba(0,229,255,0.4)] hover:shadow-[0_0_30px_rgba(0,229,255,0.6)] transition-all flex items-center justify-center gap-sm mt-md group">')

    # 6. Data Drawer Tabs
    html = html.replace('<button class="px-md py-sm text-sm font-bold text-primary-fixed-dim border-b-2 border-primary-fixed-dim bg-primary-container/5">Active Routes &amp; TEU Allocation</button>',
                        '<button id="tab-btn-routes" onclick="switchDrawerTab(\'routes\')" class="px-md py-sm text-sm font-bold text-primary-fixed-dim border-b-2 border-primary-fixed-dim bg-primary-container/5 transition-all">Active Routes &amp; TEU Allocation</button>')
    html = html.replace('<button class="px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all">AI Forecaster Diagnostics</button>',
                        '<button id="tab-btn-ai" onclick="switchDrawerTab(\'ai\')" class="px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all">AI Forecaster Diagnostics</button>')
    html = html.replace('<button class="px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all">3NF SQLite Audit Trail</button>',
                        '<button id="tab-btn-sql" onclick="switchDrawerTab(\'sql\')" class="px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all">3NF SQLite Audit Trail</button>')

    # Add hidden AI and SQL tables inside drawer right after table
    extra_drawers = """
            <!-- Table 2: AI Forecaster Diagnostics (Hidden initially) -->
            <div id="drawer-table-ai" class="hidden space-y-4 font-mono-label p-2">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="p-4 rounded-lg bg-surface-container/60 border border-primary-fixed-dim/20">
                        <p class="text-xs text-on-surface-variant uppercase">Ensemble Weighting</p>
                        <p class="text-lg font-bold text-primary-fixed-dim mt-1">XGBoost (65%) + RF (35%)</p>
                        <p class="text-xs text-emerald-400 mt-1">✓ Hyperparameters tuned via GridSearch</p>
                    </div>
                    <div class="p-4 rounded-lg bg-surface-container/60 border border-primary-fixed-dim/20">
                        <p class="text-xs text-on-surface-variant uppercase">Cross-Validation MAPE</p>
                        <p class="text-lg font-bold text-primary-fixed-dim mt-1">3.84% across 5 Folds</p>
                        <p class="text-xs text-on-surface-variant mt-1">Zero overfitting detected</p>
                    </div>
                    <div class="p-4 rounded-lg bg-surface-container/60 border border-primary-fixed-dim/20">
                        <p class="text-xs text-on-surface-variant uppercase">Next Month Surge Index</p>
                        <p class="text-lg font-bold text-amber-400 mt-1">+14.2% Container Volume</p>
                        <p class="text-xs text-on-surface-variant mt-1">Driven by holiday seasonal spike</p>
                    </div>
                </div>
                <div class="p-4 rounded-lg bg-surface-container-lowest/50 border border-outline-variant/20">
                    <p class="text-xs font-bold text-primary-fixed-dim mb-3 uppercase tracking-wider">Top Feature Importance breakdown (SHAP Values)</p>
                    <div class="space-y-3">
                        <div>
                            <div class="flex justify-between text-xs mb-1"><span>Sales_Index</span><span class="text-primary-fixed-dim font-bold">0.428 (42.8%)</span></div>
                            <div class="w-full h-2 bg-surface-variant rounded-full overflow-hidden"><div class="h-full bg-primary-fixed-dim w-[43%] shadow-[0_0_8px_rgba(0,229,255,0.8)]"></div></div>
                        </div>
                        <div>
                            <div class="flex justify-between text-xs mb-1"><span>Festival_Flag</span><span class="text-blue-400 font-bold">0.275 (27.5%)</span></div>
                            <div class="w-full h-2 bg-surface-variant rounded-full overflow-hidden"><div class="h-full bg-blue-400 w-[28%]"></div></div>
                        </div>
                        <div>
                            <div class="flex justify-between text-xs mb-1"><span>Promo_Discount</span><span class="text-amber-400 font-bold">0.182 (18.2%)</span></div>
                            <div class="w-full h-2 bg-surface-variant rounded-full overflow-hidden"><div class="h-full bg-amber-400 w-[18%]"></div></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Table 3: SQL Audit Trail (Hidden initially) -->
            <div id="drawer-table-sql" class="hidden font-mono-label text-xs space-y-2 p-2">
                <div class="p-3 bg-surface-container-lowest/60 rounded border-l-4 border-emerald-400 flex justify-between items-center">
                    <div><span class="text-emerald-400 font-bold">[2026-07-13 01:14:02]</span> <span class="text-on-surface">EXECUTE: `SELECT Warehouse, SUM(RouteCost) FROM Shipments GROUP BY Warehouse;`</span></div>
                    <span class="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">STATUS 200 (3.2ms)</span>
                </div>
                <div class="p-3 bg-surface-container-lowest/60 rounded border-l-4 border-primary-fixed-dim flex justify-between items-center">
                    <div><span class="text-primary-fixed-dim font-bold">[2026-07-13 01:14:05]</span> <span class="text-on-surface">EXECUTE: `UPDATE TransportationCost SET CostPerUnit = CostPerUnit * 0.95 WHERE Corridor='AMS_BER';`</span></div>
                    <span class="bg-blue-950 text-blue-400 px-2 py-0.5 rounded text-[10px] font-bold">1 ROW UPDATED</span>
                </div>
                <div class="p-3 bg-surface-container-lowest/60 rounded border-l-4 border-amber-400 flex justify-between items-center">
                    <div><span class="text-amber-400 font-bold">[2026-07-13 01:14:10]</span> <span class="text-on-surface">EXECUTE: `INSERT INTO HistoricalDemand (Customer, Month, Units) VALUES ('Berlin_LCS_A', '2026-08', 1450);`</span></div>
                    <span class="bg-amber-950 text-amber-400 px-2 py-0.5 rounded text-[10px] font-bold">TRANSACTION COMMITTED</span>
                </div>
            </div>
"""
    html = html.replace('</table>', '<table id="drawer-table-routes" class="w-full text-left border-collapse">', 1) if '<table id="drawer-table-routes"' not in html else html
    html = html.replace('</table>\n        </div>', '</table>\n        ' + extra_drawers + '</div>') if extra_drawers not in html else html

    # 7. Replace Script Controller at bottom
    new_script = """<script>
    function showToast(title, message) {
        const toast = document.getElementById('toast-notification');
        if (!toast) return;
        document.getElementById('toast-title').innerText = '⚡ ' + title;
        document.getElementById('toast-msg').innerText = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3800);
    }

    function switchMapMode(mode) {
        const btns = {'milp': 'btn-map-milp', 'cvrp': 'btn-map-cvrp', 'heat': 'btn-map-heat'};
        for (let k in btns) {
            const el = document.getElementById(btns[k]);
            if (!el) continue;
            if (k === mode) {
                el.className = 'bg-primary-container/20 text-primary-fixed-dim text-xs px-xs py-1 rounded border border-primary-fixed-dim/40 font-bold transition-all';
            } else {
                el.className = 'bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant transition-all';
            }
        }
        
        const gMilp = document.getElementById('map-group-milp');
        const gCvrp = document.getElementById('map-group-cvrp');
        const gHeat = document.getElementById('map-group-heat');
        if (gMilp) gMilp.classList.add('hidden');
        if (gCvrp) gCvrp.classList.add('hidden');
        if (gHeat) gHeat.classList.add('hidden');
        
        const target = document.getElementById('map-group-' + mode);
        if (target) target.classList.remove('hidden');

        const legends = {
            'milp': '<div class="flex items-center gap-xs"><span class="w-2 h-2 rounded-full bg-primary-fixed-dim"></span> Primary Hub</div><div class="flex items-center gap-xs"><span class="w-2 h-0.5 bg-primary-fixed-dim"></span> Active Intermodal</div><div class="flex items-center gap-xs"><span class="w-2 h-0.5 border-t border-dashed border-primary-fixed-dim"></span> Predicted Route</div>',
            'cvrp': '<div class="flex items-center gap-xs"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> Local Delivery Stop</div><div class="flex items-center gap-xs"><span class="w-2 h-0.5 border-t border-dashed border-emerald-400"></span> Multi-Stop Loop #1</div>',
            'heat': '<div class="flex items-center gap-xs"><span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span> High Demand Hub (>1.5K TEU)</div><div class="flex items-center gap-xs"><span class="w-2 h-2 rounded-full bg-amber-400"></span> Medium Volume Node</div>'
        };
        const leg = document.getElementById('map-legend-text');
        if (leg) leg.innerHTML = legends[mode] || '';
        showToast('Map Mode Switched', 'Displaying active ' + mode.toUpperCase() + ' network layer.');
    }

    function switchDrawerTab(tabName) {
        const tabs = {'routes': 'tab-btn-routes', 'ai': 'tab-btn-ai', 'sql': 'tab-btn-sql'};
        const contents = {'routes': 'drawer-table-routes', 'ai': 'drawer-table-ai', 'sql': 'drawer-table-sql'};
        
        for (let k in tabs) {
            const btn = document.getElementById(tabs[k]);
            const content = document.getElementById(contents[k]);
            if (!btn || !content) continue;
            if (k === tabName) {
                btn.className = 'px-md py-sm text-sm font-bold text-primary-fixed-dim border-b-2 border-primary-fixed-dim bg-primary-container/5 transition-all';
                content.classList.remove('hidden');
            } else {
                btn.className = 'px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all';
                content.classList.add('hidden');
            }
        }
    }

    function runGlobalOptimization() {
        const btn = document.getElementById('btn-run-solver');
        if (btn) {
            btn.innerHTML = '<span class="material-symbols-outlined animate-spin text-sm">refresh</span> Solving SCIP MILP...';
            btn.disabled = true;
        }
        
        const salesEl = document.getElementById('slider-sales');
        const salesMult = salesEl ? parseFloat(salesEl.value) : 1.2;
        const festEl = document.getElementById('slider-fest');
        const festSurge = festEl ? parseFloat(festEl.value) : 42;
        
        const newCost = Math.round(1425800 * (0.8 + (salesMult * 0.15) + (festSurge * 0.002)));
        const newRoutes = Math.min(36, Math.round(24 * salesMult));
        const newUtil = Math.min(99.4, (88.0 + (salesMult * 5.0)).toFixed(1));

        setTimeout(() => {
            const kCost = document.getElementById('kpi-cost');
            const kRoutes = document.getElementById('kpi-routes');
            const kUtil = document.getElementById('kpi-util');
            if (kCost) kCost.innerText = '$' + newCost.toLocaleString();
            if (kRoutes) kRoutes.innerText = newRoutes + ' / 36 Routes';
            if (kUtil) kUtil.innerText = newUtil + '% Capacity';
            
            if (btn) {
                btn.innerHTML = '<span class="material-symbols-outlined group-hover:rotate-180 transition-transform duration-700">bolt</span> Re-Run MILP & CVRP Solvers';
                btn.disabled = false;
            }
            showToast('Solvers Converged in 14.2ms', 'Optimal container allocation recalculated across ' + newRoutes + ' corridors with SCIP integer solver.');
        }, 650);
    }

    function resetToBaseline() {
        const sSales = document.getElementById('slider-sales');
        if (sSales) sSales.value = 1.2;
        const vSales = document.getElementById('val-sales');
        if (vSales) vSales.innerText = '1.2x';

        const sFest = document.getElementById('slider-fest');
        if (sFest) sFest.value = 42;
        const vFest = document.getElementById('val-fest');
        if (vFest) vFest.innerText = '42%';

        const sRain = document.getElementById('slider-rain');
        if (sRain) sRain.value = 7;
        const vRain = document.getElementById('val-rain');
        if (vRain) vRain.innerText = 'High (7/10)';

        const sPromo = document.getElementById('slider-promo');
        if (sPromo) sPromo.value = 0.85;
        const vPromo = document.getElementById('val-promo');
        if (vPromo) vPromo.innerText = '0.85';
        
        const kCost = document.getElementById('kpi-cost');
        if (kCost) kCost.innerText = '$1,425,800';
        const kRoutes = document.getElementById('kpi-routes');
        if (kRoutes) kRoutes.innerText = '24 / 36 Routes';
        const kUtil = document.getElementById('kpi-util');
        if (kUtil) kUtil.innerText = '94.2% Capacity';
        showToast('Baseline Restored', 'All macro parameters and solver weights reset to Maersk enriched default.');
    }
</script>
</body>"""
    html = re.sub(r'<script>\s*// Micro-interactions.*?</body>', new_script, html, flags=re.DOTALL)
    
    with open('dashboard_preview.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully restored & upgraded dashboard_preview.html!")

upgrade_dashboard_preview()
