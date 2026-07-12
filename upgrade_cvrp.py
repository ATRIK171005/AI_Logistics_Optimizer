import re

def upgrade_cvrp_explorer():
    with open('orig_cvrp_explorer.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add Toast HTML right after <body...>
    toast_html = """
<!-- Toast Notification -->
<div id="toast-notification" class="fixed bottom-6 right-6 z-50 bg-[#00243D]/95 border border-[#00E5FF] shadow-[0_0_25px_rgba(0,229,255,0.4)] backdrop-blur-md px-6 py-4 rounded-xl flex items-center gap-3 transition-all duration-400 opacity-0 pointer-events-none translate-y-5">
    <span class="material-symbols-outlined text-[#00E5FF] animate-pulse">check_circle</span>
    <div>
        <p id="toast-title" class="font-bold text-sm text-[#00E5FF] font-mono-kpi">⚡ GLS Metaheuristics Converged</p>
        <p id="toast-msg" class="text-xs text-gray-300">Exact CVRP loops scheduled across 18 active vehicles.</p>
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
                        '<button onclick="runCVRPOptimization()" class="bg-primary-container text-on-primary-container px-sm py-xs rounded-lg font-bold hover:scale-105 transition-transform shadow-[0_0_15px_rgba(0,229,255,0.4)] flex items-center gap-1.5"><span class="material-symbols-outlined text-sm">bolt</span> Re-optimize Fleet Dispatch</button>')
    
    html = html.replace('<button class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md">',
                        '<button onclick="resetCVRP()" class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md shadow-sm font-semibold">')

    # Side nav links
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*hub.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold" href="dashboard_preview.html"><span class="material-symbols-outlined">hub</span><span class="font-body-md text-body-md">Network Topology</span></a>', html, flags=re.DOTALL)
    
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*trending_up.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold" href="demand_forecaster.html"><span class="material-symbols-outlined">trending_up</span><span class="font-body-md text-body-md">Demand Forecaster</span></a>', html, flags=re.DOTALL)

    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2[^>]*href="[^"]*"',
                  '<a class="flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2 border-primary-fixed-dim bg-primary-container/10 hover:bg-primary-container/5 transition-all font-semibold" href="cvrp_explorer.html"', html)
    
    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*analytics.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold cursor-pointer" onclick="showToast(\'Fleet Fuel Savings\', \'Optimized multi-stop routing cuts CO2 emissions by 28.4% monthly.\')"><span class="material-symbols-outlined">analytics</span><span class="font-body-md text-body-md">Cost Analytics</span></a>', html, flags=re.DOTALL)

    html = re.sub(r'<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5[^>]*history.*?</a>',
                  '<a class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all font-semibold cursor-pointer" onclick="showToast(\'Audit Trail Logged\', \'18 discrete truck trips synced to SQLite database.\')"><span class="material-symbols-outlined">history</span><span class="font-body-md text-body-md">Audit Logs</span></a>', html, flags=re.DOTALL)

    # 3. Top Right Filter and Share buttons
    html = html.replace('<button class="px-sm py-xs rounded-lg bg-surface-variant/40 hover:bg-surface-variant text-xs text-on-surface-variant flex items-center gap-xs transition-colors">Filter Fleet</button>',
                        '<button id="btn-filter-fleet" onclick="toggleFleetFilter()" class="px-sm py-xs rounded-lg bg-surface-variant/40 hover:bg-surface-variant text-xs text-on-surface-variant flex items-center gap-xs transition-colors"><span id="txt-filter">Filter Fleet</span></button>')
    html = html.replace('<button class="px-sm py-xs rounded-lg bg-surface-variant/40 hover:bg-surface-variant text-xs text-on-surface-variant flex items-center gap-xs transition-colors">Share Map</button>',
                        '<button onclick="shareDispatchLink()" class="px-sm py-xs rounded-lg bg-surface-variant/40 hover:bg-surface-variant text-xs text-on-surface-variant flex items-center gap-xs transition-colors">Share Map</button>')

    # 4. Map Zoom controls
    html = html.replace('<button class="w-8 h-8 rounded bg-surface-variant/40 hover:bg-surface-variant flex items-center justify-center text-on-surface-variant transition-colors">+</button>',
                        '<button onclick="zoomMap(1.2)" class="w-8 h-8 rounded bg-surface-variant/40 hover:bg-surface-variant flex items-center justify-center text-on-surface-variant transition-colors">+</button>')
    html = html.replace('<button class="w-8 h-8 rounded bg-surface-variant/40 hover:bg-surface-variant flex items-center justify-center text-on-surface-variant transition-colors">-</button>',
                        '<button onclick="zoomMap(0.8)" class="w-8 h-8 rounded bg-surface-variant/40 hover:bg-surface-variant flex items-center justify-center text-on-surface-variant transition-colors">-</button>')
    html = html.replace('<button class="w-8 h-8 rounded bg-surface-variant/40 hover:bg-surface-variant flex items-center justify-center text-on-surface-variant transition-colors">layers</button>',
                        '<button onclick="toggleMapTheme()" class="w-8 h-8 rounded bg-surface-variant/40 hover:bg-surface-variant flex items-center justify-center text-on-surface-variant transition-colors">layers</button>')

    # 5. Add IDs to KPI metrics
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">412.5 KM</h3>', '<h3 id="cvrp-dist" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">412.5 KM</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">18 Active Trucks</h3>', '<h3 id="cvrp-trucks" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">18 Active Trucks</h3>')
    html = html.replace('<h3 class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">89.4% Fill Factor</h3>', '<h3 id="cvrp-fill" class="font-mono-kpi text-mono-kpi text-primary-fixed-dim">89.4% Fill Factor</h3>')

    # 6. Add IDs to Truck cards and accordions
    html = re.sub(r'(<div class="border border-outline-variant/30 rounded-lg bg-surface-container/30 overflow-hidden">)', r'\1\n<div onclick="toggleAccordion(\'truck-acc-1\')" class="cursor-pointer">', html, count=1)
    html = re.sub(r'(<div class="border border-outline-variant/30 rounded-lg bg-surface-container/30 overflow-hidden">)', r'\1\n<div onclick="toggleAccordion(\'truck-acc-2\')" class="cursor-pointer">', html, count=1)
    html = re.sub(r'(<div class="border border-outline-variant/30 rounded-lg bg-surface-container/30 overflow-hidden">)', r'\1\n<div onclick="toggleAccordion(\'truck-acc-3\')" class="cursor-pointer">', html, count=1)

    # 7. Add IDs to bottom buttons
    html = html.replace('<button class="w-full py-xs rounded bg-surface-variant/40 text-xs text-on-surface-variant hover:bg-surface-variant transition-colors">Manual Vehicle Assign</button>',
                        '<button onclick="showToast(\'Manual Assign Mode\', \'Click any unassigned map node to dispatch emergency backup vehicle.\')" class="w-full py-xs rounded bg-surface-variant/40 text-xs text-on-surface-variant hover:bg-surface-variant transition-colors">Manual Vehicle Assign</button>')
    html = html.replace('<button class="w-full py-xs rounded bg-primary-container text-on-primary-container text-xs font-bold hover:scale-[1.02] transition-transform">Run Metaheuristics →</button>',
                        '<button id="btn-run-cvrp-bottom" onclick="runCVRPOptimization()" class="w-full py-xs rounded bg-primary-container text-on-primary-container text-xs font-bold hover:scale-[1.02] transition-transform">Run Metaheuristics →</button>')

    # 8. Replace script controller at bottom
    new_script = """<script>
    let currentZoom = 1.0;
    let isFiltered = false;

    function showToast(title, message) {
        const toast = document.getElementById('toast-notification');
        if (!toast) return;
        document.getElementById('toast-title').innerText = '⚡ ' + title;
        document.getElementById('toast-msg').innerText = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3800);
    }

    function zoomMap(scale) {
        currentZoom = Math.max(0.6, Math.min(2.0, currentZoom * scale));
        const el = document.querySelector('main svg');
        if (el) el.style.transform = `scale(${currentZoom})`;
        showToast('Map Zoom', 'Current topological scale: ' + Math.round(currentZoom * 100) + '%');
    }

    function toggleMapTheme() {
        const el = document.querySelector('main svg');
        if (!el) return;
        if (el.style.filter === 'contrast(1.4) saturate(1.8)') {
            el.style.filter = 'none';
            showToast('Satellite Mode Off', 'Switched to standard high-contrast GIS map.');
        } else {
            el.style.filter = 'contrast(1.4) saturate(1.8)';
            showToast('High Contrast Active', 'Enhanced GIS topographical neon contrast active.');
        }
    }

    function toggleFleetFilter() {
        isFiltered = !isFiltered;
        const btn = document.getElementById('btn-filter-fleet');
        const txt = document.getElementById('txt-filter');
        if (isFiltered) {
            if (btn) btn.className = 'px-sm py-xs rounded-lg bg-primary-container text-on-primary-container text-xs font-bold flex items-center gap-xs transition-colors';
            if (txt) txt.innerText = 'High-Load Only (>90%)';
            showToast('Fleet Filtered', 'Displaying only trucks with >90% TEU capacity utilization.');
        } else {
            if (btn) btn.className = 'px-sm py-xs rounded-lg bg-surface-variant/40 hover:bg-surface-variant text-xs text-on-surface-variant flex items-center gap-xs transition-colors';
            if (txt) txt.innerText = 'Filter Fleet';
            showToast('Filter Cleared', 'Showing all 18 active delivery vehicles.');
        }
    }

    function shareDispatchLink() {
        navigator.clipboard?.writeText('https://maersk-enterprise.internal/dispatch/cvrp-rotterdam-77291');
        showToast('📋 Dispatch Link Copied', 'Shareable multi-stop VRP manifest link copied to clipboard.');
    }

    function toggleAccordion(accId) {
        showToast('Manifest Expanded', 'Displaying full multi-stop delivery loop itinerary.');
    }

    function runCVRPOptimization() {
        const btn = document.getElementById('btn-run-cvrp-bottom');
        if (btn) {
            btn.innerHTML = '<span class="material-symbols-outlined animate-spin text-xs">refresh</span> Solving GLS...';
            btn.disabled = true;
        }

        setTimeout(() => {
            const kDist = document.getElementById('cvrp-dist');
            const kTrucks = document.getElementById('cvrp-trucks');
            const kFill = document.getElementById('cvrp-fill');
            if (kDist) kDist.innerText = '384.8 KM';
            if (kTrucks) kTrucks.innerText = '16 Active Trucks';
            if (kFill) kFill.innerText = '95.2% Fill Factor';
            
            if (btn) {
                btn.innerHTML = 'Run Metaheuristics →';
                btn.disabled = false;
            }
            showToast('GLS Metaheuristics Converged', 'Total distance reduced to 384.8 km (-27.7 km saved) using OR-Tools routing kernel.');
        }, 650);
    }

    function resetCVRP() {
        const kDist = document.getElementById('cvrp-dist');
        const kTrucks = document.getElementById('cvrp-trucks');
        const kFill = document.getElementById('cvrp-fill');
        if (kDist) kDist.innerText = '412.5 KM';
        if (kTrucks) kTrucks.innerText = '18 Active Trucks';
        if (kFill) kFill.innerText = '89.4% Fill Factor';
        showToast('Dispatch Reset', 'Fleet allocation restored to baseline multi-stop schedule.');
    }
</script>
</body>"""
    html = re.sub(r'<script>\s*// Micro-interactions.*?</body>', new_script, html, flags=re.DOTALL)
    
    with open('cvrp_explorer.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully restored & upgraded cvrp_explorer.html!")

upgrade_cvrp_explorer()
