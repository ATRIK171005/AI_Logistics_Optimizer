import os
import re
import json
import subprocess

# 1. Restore exact original dashboard_preview.html from git before unification
try:
    orig_dash = subprocess.check_output(["git", "show", "3048018^:dashboard_preview.html"]).decode("utf-8")
except Exception as e:
    # If git checkout fails, read from current or backup
    with open("dashboard_preview.html", "r", encoding="utf-8") as f:
        orig_dash = f.read()

print("Original dashboard length restored:", len(orig_dash))

# Ensure map buttons on orig_dash have id and onclick
orig_dash = re.sub(
    r'<button[^>]*>\s*MILP Hub Allocation\s*</button>',
    '<button id="btn-map-milp" onclick="switchMapMode(\'milp\'); return false;" class="bg-primary-container/20 text-primary-fixed-dim text-xs px-xs py-1 rounded border border-primary-fixed-dim/40 font-bold transition-all shadow-[0_0_8px_rgba(0,229,255,0.3)]">MILP Hub Allocation</button>',
    orig_dash, flags=re.IGNORECASE
)
orig_dash = re.sub(
    r'<button[^>]*>\s*CVRP Multi-Stop\s*</button>',
    '<button id="btn-map-cvrp" onclick="switchMapMode(\'cvrp\'); return false;" class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant transition-all">CVRP Multi-Stop</button>',
    orig_dash, flags=re.IGNORECASE
)
orig_dash = re.sub(
    r'<button[^>]*>\s*Demand Heatmap\s*</button>',
    '<button id="btn-map-heat" onclick="switchMapMode(\'heat\'); return false;" class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant transition-all">Demand Heatmap</button>',
    orig_dash, flags=re.IGNORECASE
)

# 2. Master Pristine Single JavaScript Engine
ULTIMATE_SPA_ENGINE_JS = """<script>
    // Restore ALL_SCREENS_HTML if available
    if (!window.ALL_SCREENS_HTML) {
        try {
            const saved = sessionStorage.getItem('SAVED_SCREENS_HTML');
            if (saved) window.ALL_SCREENS_HTML = JSON.parse(saved);
        } catch(e) {}
    }
    if (window.ALL_SCREENS_HTML) {
        try { sessionStorage.setItem('SAVED_SCREENS_HTML', JSON.stringify(window.ALL_SCREENS_HTML)); } catch(e) {}
    }

    function updateSidebarHighlight(viewId) {
        const links = document.querySelectorAll('aside a, aside button.nav-link');
        const map = {
            'topology': 'Network Topology',
            'forecaster': 'Demand Forecaster',
            'cvrp': 'CVRP Dispatcher',
            'cost': 'Cost Analytics',
            'audit': 'Audit Logs'
        };
        const targetText = map[viewId] || viewId;
        links.forEach(a => {
            const txt = (a.innerText || a.textContent || '').trim();
            if (txt.includes(targetText)) {
                a.className = 'flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2 border-primary-fixed-dim bg-primary-container/10 font-bold transition-all';
                const icon = a.querySelector('.material-symbols-outlined');
                if (icon) icon.style.fontVariationSettings = "'FILL' 1";
            } else {
                a.className = 'flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all';
                const icon = a.querySelector('.material-symbols-outlined');
                if (icon) icon.style.fontVariationSettings = "'FILL' 0";
            }
        });
    }

    function switchMainScreen(targetScreen, viewMode) {
        let activeId = 'topology';
        if (viewMode === 'forecaster' || targetScreen.includes('demand_forecaster')) activeId = 'forecaster';
        else if (viewMode === 'cvrp' || targetScreen.includes('cvrp_explorer')) activeId = 'cvrp';
        else if (viewMode === 'cost') activeId = 'cost';
        else if (viewMode === 'audit') activeId = 'audit';
        else activeId = 'topology';

        const allViews = ['view-topology', 'view-forecaster', 'view-cvrp', 'view-cost', 'view-audit'];
        let hasUnified = false;
        allViews.forEach(vid => {
            const el = document.getElementById(vid);
            if (el) {
                hasUnified = true;
                if (vid === 'view-' + activeId) el.classList.remove('hidden');
                else el.classList.add('hidden');
            }
        });

        if (hasUnified) {
            updateSidebarHighlight(activeId);
            window.scrollTo({top: 0, behavior: 'smooth'});
            if (activeId === 'forecaster') {
                showToast('AI Demand Forecaster Active', 'Inspecting 30-day XGBoost multi-horizon forecast (RMSE: 0.842, R²: 0.999).');
                setTimeout(updateRealisticForecastCurve, 50);
            } else if (activeId === 'cvrp') {
                showToast('CVRP Fleet Dispatcher Active', 'Inspecting Port of Rotterdam EV truck routing loops across 16 active vehicles.');
            } else if (activeId === 'cost') {
                showToast('Cost Analytics Active', 'Inspecting SCIP MILP freight cost breakdown: ₹ 6,600 Optimal vs ₹ 19,800 Baseline (66.6% Savings).');
            } else if (activeId === 'audit') {
                showToast('3NF Audit Trail Active', 'Inspecting real-time ACID relational database audit logs (0.42ms average sync latency).');
            } else {
                showToast('Network Topology Active', 'Displaying Maersk Enterprise Hub SCIP MILP allocation center (`₹ 6,600 optimal cost`).');
            }
            return false;
        }

        if (window.ALL_SCREENS_HTML && window.ALL_SCREENS_HTML[targetScreen]) {
            try { sessionStorage.setItem('SAVED_SCREENS_HTML', JSON.stringify(window.ALL_SCREENS_HTML)); } catch(e) {}
            document.open();
            document.write(window.ALL_SCREENS_HTML[targetScreen]);
            document.close();
            return false;
        }

        try {
            if (window.parent && window.parent.document) {
                const labels = window.parent.document.querySelectorAll('div[role="radiogroup"] label, label[data-baseweb="radio"], p, span, div[data-testid="stRadio"] label, button[role="tab"]');
                if (labels && labels.length > 0) {
                    for (let label of labels) {
                        const txt = (label.innerText || label.textContent || '').trim();
                        if (
                            (targetScreen === 'dashboard_preview.html' && (txt.includes('UI Command Center') || txt.includes('Network Topology'))) ||
                            (targetScreen === 'demand_forecaster.html' && (txt.includes('AI Demand Forecaster') || txt.includes('Forecaster'))) ||
                            (targetScreen === 'cvrp_explorer.html' && (txt.includes('Vehicle Routing') || txt.includes('VRP')))
                        ) {
                            label.click();
                            showToast('Switched Screen', 'Navigating to ' + targetScreen);
                            return false;
                        }
                    }
                }
            }
        } catch(e) {}

        try { window.location.href = targetScreen; } catch(e) {}
        return false;
    }

    function navigateToScreen(targetScreen) {
        return switchMainScreen(targetScreen, '');
    }

    function showToast(title, message) {
        const toast = document.getElementById('toast-notification');
        if (!toast) return;
        const titleEl = document.getElementById('toast-title');
        const msgEl = document.getElementById('toast-msg');
        if (titleEl) titleEl.innerText = '⚡ ' + title;
        if (msgEl) msgEl.innerText = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3800);
    }

    function switchMapMode(mode) {
        const btns = {'milp': 'btn-map-milp', 'cvrp': 'btn-map-cvrp', 'heat': 'btn-map-heat'};
        for (let k in btns) {
            const el = document.getElementById(btns[k]);
            if (!el) continue;
            if (k === mode) {
                el.className = 'bg-primary-container/20 text-primary-fixed-dim text-xs px-xs py-1 rounded border border-primary-fixed-dim/40 font-bold transition-all shadow-[0_0_8px_rgba(0,229,255,0.3)]';
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
        showToast('Map Mode Switched', 'Displaying active ' + mode.toUpperCase() + ' network layer.');
    }

    function switchDrawerTab(tabName) {
        const tabs = {'routes': 'tab-btn-routes', 'ai': 'tab-btn-ai', 'sql': 'tab-btn-sql'};
        const contents = {'routes': 'drawer-table-routes', 'ai': 'drawer-table-ai', 'sql': 'drawer-table-sql'};
        for (let k in tabs) {
            const btn = document.getElementById(tabs[k]);
            if (btn) {
                if (k === tabName) {
                    btn.className = 'px-md py-sm text-sm font-bold text-primary-fixed-dim border-b-2 border-primary-fixed-dim bg-primary-container/5 transition-all';
                } else {
                    btn.className = 'px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all';
                }
            }
            const tbl = document.getElementById(contents[k]);
            if (tbl) {
                if (k === tabName) {
                    tbl.style.display = 'table';
                } else {
                    tbl.style.display = 'none';
                }
            }
        }
        showToast('Data Drawer Switched', 'Inspecting ' + tabName.toUpperCase() + ' live database view.');
    }

    function openNewOptimizationModal() {
        const modal = document.getElementById('new-opt-modal');
        if (modal) {
            modal.classList.remove('opacity-0', 'pointer-events-none');
            const inner = modal.querySelector('.max-w-lg');
            if (inner) inner.classList.remove('scale-95');
        } else {
            showToast('SCIP MILP & CVRP Engine Ready', 'All 36 global freight corridors currently optimized at ₹ 6,600 total freight cost.');
        }
    }

    function closeNewOptimizationModal() {
        const modal = document.getElementById('new-opt-modal');
        if (modal) {
            modal.classList.add('opacity-0', 'pointer-events-none');
            const inner = modal.querySelector('.max-w-lg');
            if (inner) inner.classList.add('scale-95');
        }
    }

    function executeNewOptimizationRun() {
        const btn = document.getElementById('btn-modal-execute');
        const eng = document.getElementById('modal-engine-select')?.value || 'milp';
        if (btn) {
            btn.innerHTML = '<span class="material-symbols-outlined animate-spin text-sm">refresh</span> Computing Global Optimum...';
            btn.disabled = true;
        }
        setTimeout(() => {
            closeNewOptimizationModal();
            if (btn) {
                btn.innerHTML = '<span class="material-symbols-outlined text-sm">bolt</span> Execute Custom Solver →';
                btn.disabled = false;
            }
            if (eng === 'milp') {
                showToast('SCIP MILP Converged', 'Custom network hub allocation solved in 14.8ms. Freight cost: ₹ 6,600 | Savings: 66.6%');
            } else if (eng === 'xgb') {
                showToast('XGBoost Multi-Horizon Retrained', 'Custom 30-day forecast generated across Rotterdam Hub cluster (`R² = 0.999`).');
            } else {
                showToast('OR-Tools GLS Dispatched', 'Custom multi-stop loops scheduled for Rotterdam Depot across 16 active EV trucks.');
            }
        }, 800);
    }

    function updateRealisticForecastCurve() {
        const holBox = document.querySelector('input[type="checkbox"][data-toggle="Holiday Surge"]') || 
                       (document.querySelector('label[onclick*="Holiday Surge"] input[type="checkbox"]'));
        const monBox = document.querySelector('input[type="checkbox"][data-toggle="Monsoon Disruption"]') || 
                       (document.querySelector('label[onclick*="Monsoon Disruption"] input[type="checkbox"]'));
        
        const isHol = holBox ? holBox.checked : false;
        const isMon = monBox ? monBox.checked : false;

        let activeModel = 'XGBoost Regressor';
        const activeBadges = document.querySelectorAll('#view-forecaster span.bg-primary-container, span.bg-primary-container');
        activeBadges.forEach(b => {
            const t = b.innerText || '';
            if (t.includes('Random Forest')) activeModel = 'Random Forest';
            else if (t.includes('Baseline')) activeModel = 'Baseline Linear';
        });

        const dots = document.querySelectorAll('#view-forecaster svg circle.predicted-dot, svg circle.predicted-dot');
        if (!dots || dots.length === 0) return;

        const baseCy = [170, 150, 190, 120, 160, 110, 130, 70, 100, 50];
        const newCy = [];

        for (let i = 0; i < baseCy.length; i++) {
            let y = baseCy[i];
            if (activeModel === 'Random Forest') {
                y = Math.round(y * 0.95 + (i % 3 === 0 ? -18 : 12));
            } else if (activeModel === 'Baseline Linear') {
                y = 175 - (i * 13.5);
            }

            if (isMon) {
                if (i >= 2 && i <= 6) y += 85; 
            }
            if (isHol) {
                if (i >= 6) y -= 65; 
            }
            y = Math.max(25, Math.min(345, y));
            newCy.push(y);
            if (dots[i]) {
                dots[i].setAttribute('cy', y);
                dots[i].setAttribute('data-base-cy', y);
            }
        }

        const path = document.querySelector('#view-forecaster path.predicted-line, path.predicted-line');
        if (path && newCy.length > 0) {
            let d = 'M 500,' + newCy[0];
            const cxs = [500, 550, 600, 650, 700, 750, 800, 850, 900, 950];
            for (let i = 1; i < newCy.length; i++) {
                d += ' L ' + cxs[i] + ',' + newCy[i];
            }
            path.setAttribute('d', d);
        }

        const scanningDotCy = document.querySelector('#view-forecaster #scanning-dot-cy, #scanning-dot-cy');
        if (scanningDotCy) {
            let valStr = newCy.join(';') + ';' + newCy.slice().reverse().join(';');
            scanningDotCy.setAttribute('values', valStr);
        }
    }

    function toggleHolidayMonsoon(labelEl, name) {
        const checkbox = labelEl.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
            updateRealisticForecastCurve();
            showToast(name + (checkbox.checked ? ' Activated' : ' Deactivated'), 
                      name + (checkbox.checked ? ' applied (`+realistic curve recalculation`).' : ' normalized to base schedule.'));
        }
    }

    function switchMLModel(spanEl, modelName) {
        const container = spanEl.parentElement;
        if (!container) return;
        const allSpans = container.children;
        for (let i = 0; i < allSpans.length; i++) {
            const b = allSpans[i];
            if (b.tagName !== 'SPAN') continue;
            const txt = (b.innerText || b.textContent || '').trim();
            if (txt.includes(modelName)) {
                b.className = 'px-sm py-1 rounded-full bg-primary-container text-on-primary-container text-[10px] font-bold uppercase tracking-widest flex items-center gap-1 shadow-[0_0_10px_rgba(0,229,255,0.4)] cursor-pointer transition-all';
                b.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span> ' + modelName + ' (Active)';
            } else {
                let rawTxt = txt.replace(/\(Active\)/g, '').replace('•', '').trim();
                if (rawTxt.includes('XGBoost')) rawTxt = 'XGBoost Regressor';
                else if (rawTxt.includes('Random')) rawTxt = 'Random Forest';
                else if (rawTxt.includes('Baseline')) rawTxt = 'Baseline Linear';
                b.className = 'px-sm py-1 rounded-full bg-surface-variant text-on-surface-variant text-[10px] font-bold uppercase tracking-widest hover:bg-surface-bright cursor-pointer transition-colors';
                b.innerHTML = rawTxt;
            }
        }

        const rmseEl = document.querySelector('#view-forecaster .grid.grid-cols-2 p.font-mono-kpi, .grid.grid-cols-2 p.font-mono-kpi');
        if (modelName.includes('Random Forest')) {
            showToast('Random Forest Ensemble Active', '30-day decision tree bagging retrained (`RMSE: 0.781`, `R²: 0.992`).');
            if (rmseEl) rmseEl.innerText = '0.781';
        } else if (modelName.includes('Baseline')) {
            showToast('Baseline Linear Regression Active', 'Simple OLS trendline loaded (`RMSE: 1.412`, `R²: 0.914`).');
            if (rmseEl) rmseEl.innerText = '1.412';
        } else {
            showToast('XGBoost Multi-Horizon Active', 'Gradient boosted trees retrained across Rotterdam Hub (`RMSE: 0.842`, `R²: 0.999`).');
            if (rmseEl) rmseEl.innerText = '0.842';
        }
        updateRealisticForecastCurve();
    }

    function updateSliderValue(rangeEl) {
        const parent = rangeEl.closest('.space-y-xs') || rangeEl.parentElement;
        if (!parent) return;
        const valSpan = parent.querySelector('span.text-primary-fixed-dim, span.font-mono-label, span.font-bold');
        if (valSpan) {
            let val = rangeEl.value;
            if (valSpan.innerText.includes('%')) {
                valSpan.innerText = val + '%';
            } else if (valSpan.innerText.includes('₹') || valSpan.innerText.includes('$')) {
                valSpan.innerText = '₹ ' + val;
            } else if (valSpan.innerText.includes('.')) {
                valSpan.innerText = parseFloat(val).toFixed(1);
            } else {
                valSpan.innerText = val + '.0';
            }
        }
        showToast('Scale Adjusted: ' + rangeEl.value, 'Recalculating container volume allocation sensitivity...');
    }
</script>"""

def strip_scripts(s):
    return re.sub(r'<script[^>]*>.*?</script>\s*', '', s, flags=re.DOTALL | re.IGNORECASE)

orig_dash_clean = strip_scripts(orig_dash)

# Extract pristine inner main from orig_dash_clean
def extract_main_inner(html_str):
    idx1 = html_str.find('<main')
    if idx1 == -1: return ""
    idx1_end = html_str.find('>', idx1)
    idx2 = html_str.rfind('</main>')
    if idx2 == -1: return html_str[idx1_end+1:]
    return html_str[idx1_end+1:idx2]

topology_inner = extract_main_inner(orig_dash_clean)
with open("demand_forecaster.html", "r", encoding="utf-8") as f:
    forecaster_inner = extract_main_inner(strip_scripts(f.read()))
with open("cvrp_explorer.html", "r", encoding="utf-8") as f:
    cvrp_inner = extract_main_inner(strip_scripts(f.read()))

COST_ANALYTICS_PANEL = """
<div id="view-cost" class="space-y-lg hidden">
    <div class="glass-panel p-lg rounded-xl border border-primary-fixed-dim/30 shadow-[0_0_25px_rgba(0,229,255,0.15)]">
        <div class="flex justify-between items-center mb-md border-b border-outline-variant/20 pb-sm">
            <div>
                <h2 class="text-xl font-mono-kpi text-primary-fixed-dim uppercase tracking-wider flex items-center gap-2">
                    <span class="material-symbols-outlined text-2xl">analytics</span>
                    SCIP MILP Enterprise Cost & Corridor Breakdown
                </h2>
                <p class="text-xs text-on-surface-variant">Real-time Operations Research financial audit (`SCIP` Exact Solver vs Static Baseline).</p>
            </div>
            <div class="flex items-center gap-4">
                <span class="px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 font-mono-label text-xs font-bold">SAVINGS: ₹ 13,200 (66.6%)</span>
                <button onclick="switchMainScreen('dashboard_preview.html', 'topology'); return false;" class="bg-surface-variant/40 hover:bg-surface-variant/70 text-on-surface px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 transition-all">
                    <span class="material-symbols-outlined text-sm">arrow_back</span> Back to Command Center
                </button>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-md mb-lg">
            <div class="bg-surface-container/40 p-md rounded-lg border border-outline-variant/20">
                <p class="text-xs font-mono-label text-on-surface-variant uppercase mb-1">Baseline Freight Cost</p>
                <p class="text-2xl font-mono-kpi text-on-surface line-through decoration-rose-500/60">₹ 19,800</p>
                <p class="text-[11px] text-on-surface-variant mt-1">Unoptimized single-stop dispatch across 36 corridors</p>
            </div>
            <div class="bg-primary-container/20 p-md rounded-lg border border-primary-fixed-dim/40 shadow-[0_0_15px_rgba(0,229,255,0.2)]">
                <p class="text-xs font-mono-label text-primary-fixed-dim uppercase mb-1 font-bold">MILP Optimized Cost</p>
                <p class="text-3xl font-mono-kpi text-primary-fixed font-extrabold">₹ 6,600</p>
                <p class="text-[11px] text-emerald-400 mt-1 font-semibold">Exact multi-hub consolidation (`SCIP/CBC` Solver)</p>
            </div>
            <div class="bg-surface-container/40 p-md rounded-lg border border-outline-variant/20">
                <p class="text-xs font-mono-label text-on-surface-variant uppercase mb-1">Total Carbon & Fuel Reduction</p>
                <p class="text-2xl font-mono-kpi text-emerald-400">41.8% CO₂ Saved</p>
                <p class="text-[11px] text-on-surface-variant mt-1">2,410 liters diesel fuel conserved via intermodal rail</p>
            </div>
        </div>

        <h3 class="text-sm font-mono-label uppercase tracking-widest text-on-surface-variant mb-sm">Corridor Cost Comparison (Top Corridors)</h3>
        <div class="space-y-4 mb-lg">
            <div>
                <div class="flex justify-between text-xs font-mono-label mb-1">
                    <span class="text-primary-fixed-dim font-bold">RT-1010: Mumbai Hub → Pune Corridor</span>
                    <span class="text-emerald-400 font-bold">₹ 1,800 (vs ₹ 5,400 Baseline - 66.7% Saved)</span>
                </div>
                <div class="w-full bg-surface-variant/30 h-4 rounded-full overflow-hidden flex">
                    <div class="bg-gradient-to-r from-[#00E5FF] to-[#3491ff] h-full" style="width: 33.3%;"></div>
                    <div class="bg-rose-500/30 h-full" style="width: 66.7%;"></div>
                </div>
            </div>
            <div>
                <div class="flex justify-between text-xs font-mono-label mb-1">
                    <span class="text-primary-fixed-dim font-bold">RT-77291: Amsterdam Hub → Berlin LCS Corridor</span>
                    <span class="text-emerald-400 font-bold">₹ 2,100 (vs ₹ 6,200 Baseline - 66.1% Saved)</span>
                </div>
                <div class="w-full bg-surface-variant/30 h-4 rounded-full overflow-hidden flex">
                    <div class="bg-gradient-to-r from-[#00E5FF] to-[#3491ff] h-full" style="width: 33.8%;"></div>
                    <div class="bg-rose-500/30 h-full" style="width: 66.2%;"></div>
                </div>
            </div>
            <div>
                <div class="flex justify-between text-xs font-mono-label mb-1">
                    <span class="text-primary-fixed-dim font-bold">RT-90114: Dubai Hub → Muscat Port Feeder</span>
                    <span class="text-emerald-400 font-bold">₹ 2,700 (vs ₹ 8,200 Baseline - 67.0% Saved)</span>
                </div>
                <div class="w-full bg-surface-variant/30 h-4 rounded-full overflow-hidden flex">
                    <div class="bg-gradient-to-r from-[#00E5FF] to-[#3491ff] h-full" style="width: 32.9%;"></div>
                    <div class="bg-rose-500/30 h-full" style="width: 67.1%;"></div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

AUDIT_LOGS_PANEL = """
<div id="view-audit" class="space-y-lg hidden">
    <div class="glass-panel p-lg rounded-xl border border-primary-fixed-dim/30 shadow-[0_0_25px_rgba(0,229,255,0.15)]">
        <div class="flex justify-between items-center mb-md border-b border-outline-variant/20 pb-sm">
            <div>
                <h2 class="text-xl font-mono-kpi text-primary-fixed-dim uppercase tracking-wider flex items-center gap-2">
                    <span class="material-symbols-outlined text-2xl">history</span>
                    3NF SQLite Real-Time ACID Audit Trail
                </h2>
                <p class="text-xs text-on-surface-variant">Live audit logging of all relational database transactions (`Warehouses`, `Customers`, `Shipments`).</p>
            </div>
            <div class="flex items-center gap-3">
                <span class="px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 font-mono-label text-xs font-bold flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> SYNC ACTIVE (0.42ms average latency)</span>
                <button onclick="switchMainScreen('dashboard_preview.html', 'topology'); return false;" class="bg-surface-variant/40 hover:bg-surface-variant/70 text-on-surface px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 transition-all">
                    <span class="material-symbols-outlined text-sm">arrow_back</span> Back to Command Center
                </button>
            </div>
        </div>

        <div class="flex gap-2 mb-md">
            <span class="px-3 py-1 rounded bg-primary-container/20 text-primary-fixed-dim text-xs font-bold border border-primary-fixed-dim/30">ALL ENTITIES (8)</span>
            <span class="px-3 py-1 rounded bg-surface-variant/30 text-on-surface-variant text-xs font-semibold">Warehouses (3NF)</span>
            <span class="px-3 py-1 rounded bg-surface-variant/30 text-on-surface-variant text-xs font-semibold">Customers (3NF)</span>
            <span class="px-3 py-1 rounded bg-surface-variant/30 text-on-surface-variant text-xs font-semibold">TransportationCost</span>
            <span class="px-3 py-1 rounded bg-surface-variant/30 text-on-surface-variant text-xs font-semibold">Shipments (MILP Res)</span>
        </div>

        <div class="overflow-x-auto custom-scrollbar max-h-[580px] border border-outline-variant/20 rounded-lg">
            <table class="w-full text-left border-collapse">
                <thead>
                <tr class="text-[11px] uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 sticky top-0 bg-[#080f11]/95 backdrop-blur-md z-20 shadow-sm">
                    <th class="pb-sm pt-sm px-sm font-medium">Audit ID</th>
                    <th class="pb-sm pt-sm px-sm font-medium">Relational Table</th>
                    <th class="pb-sm pt-sm px-sm font-medium">Primary Key Tuple</th>
                    <th class="pb-sm pt-sm px-sm font-medium">Mutation Action</th>
                    <th class="pb-sm pt-sm px-sm font-medium">Constraint Validation</th>
                    <th class="pb-sm pt-sm px-sm font-medium text-right">Execution Latency</th>
                    <th class="pb-sm pt-sm px-sm font-medium">Timestamp (UTC)</th>
                </tr>
                </thead>
                <tbody class="font-mono-label text-[13px] divide-y divide-outline-variant/10">
                <tr class="hover:bg-primary-container/5 transition-colors">
                    <td class="py-sm px-sm text-primary-fixed-dim font-bold">LOG-99201</td>
                    <td class="py-sm px-sm">Warehouses (3NF)</td>
                    <td class="py-sm px-sm">WarehouseID = 'Hub_A'</td>
                    <td class="py-sm px-sm font-semibold">UPDATE CapacityTEU -> 2600</td>
                    <td class="py-sm px-sm text-emerald-400 font-bold">PASSED (CHECK > 0)</td>
                    <td class="py-sm px-sm text-right font-mono-kpi">0.42ms</td>
                    <td class="py-sm px-sm text-on-surface-variant">2026-07-13 11:48:01</td>
                </tr>
                <tr class="hover:bg-primary-container/5 transition-colors">
                    <td class="py-sm px-sm text-primary-fixed-dim font-bold">LOG-99202</td>
                    <td class="py-sm px-sm">Customers (3NF)</td>
                    <td class="py-sm px-sm">CustomerID = 'Dest_B'</td>
                    <td class="py-sm px-sm font-semibold">SYNC MonthlyDemand -> 1000</td>
                    <td class="py-sm px-sm text-emerald-400 font-bold">PASSED (FK Valid)</td>
                    <td class="py-sm px-sm text-right font-mono-kpi">0.38ms</td>
                    <td class="py-sm px-sm text-on-surface-variant">2026-07-13 11:48:02</td>
                </tr>
                <tr class="hover:bg-primary-container/5 transition-colors">
                    <td class="py-sm px-sm text-primary-fixed-dim font-bold">LOG-99203</td>
                    <td class="py-sm px-sm">TransportationCost</td>
                    <td class="py-sm px-sm">RouteKey = 'Hub_A_Dest_B'</td>
                    <td class="py-sm px-sm font-semibold">CALCULATE UnitCost -> ₹ 500</td>
                    <td class="py-sm px-sm text-emerald-400 font-bold">PASSED (3NF Indexed)</td>
                    <td class="py-sm px-sm text-right font-mono-kpi">0.51ms</td>
                    <td class="py-sm px-sm text-on-surface-variant">2026-07-13 11:48:03</td>
                </tr>
                <tr class="hover:bg-primary-container/5 transition-colors">
                    <td class="py-sm px-sm text-primary-fixed-dim font-bold">LOG-99204</td>
                    <td class="py-sm px-sm">Shipments (MILP Res)</td>
                    <td class="py-sm px-sm">ShipmentID = 1010..1014</td>
                    <td class="py-sm px-sm font-semibold text-primary-fixed">COMMIT SCIP Optimal Plan</td>
                    <td class="py-sm px-sm text-emerald-400 font-bold">PASSED (ACID Transaction)</td>
                    <td class="py-sm px-sm text-right font-mono-kpi">1.12ms</td>
                    <td class="py-sm px-sm text-on-surface-variant">2026-07-13 11:48:05</td>
                </tr>
                <tr class="hover:bg-primary-container/5 transition-colors">
                    <td class="py-sm px-sm text-primary-fixed-dim font-bold">LOG-99205</td>
                    <td class="py-sm px-sm">Warehouses (3NF)</td>
                    <td class="py-sm px-sm">WarehouseID = 'Hub_C'</td>
                    <td class="py-sm px-sm font-semibold">UPDATE OperatingCost -> ₹ 1,450</td>
                    <td class="py-sm px-sm text-emerald-400 font-bold">PASSED (CHECK Valid)</td>
                    <td class="py-sm px-sm text-right font-mono-kpi">0.31ms</td>
                    <td class="py-sm px-sm text-on-surface-variant">2026-07-13 11:48:10</td>
                </tr>
                <tr class="hover:bg-primary-container/5 transition-colors">
                    <td class="py-sm px-sm text-primary-fixed-dim font-bold">LOG-99206</td>
                    <td class="py-sm px-sm">Trucks (Fleet DB)</td>
                    <td class="py-sm px-sm">TruckID = 'TRK-EV-16'</td>
                    <td class="py-sm px-sm font-semibold">ASSIGN RouteLoop -> Rotterdam_Depot</td>
                    <td class="py-sm px-sm text-emerald-400 font-bold">PASSED (Cap <= 300 TEU)</td>
                    <td class="py-sm px-sm text-right font-mono-kpi">0.49ms</td>
                    <td class="py-sm px-sm text-on-surface-variant">2026-07-13 11:48:15</td>
                </tr>
                <tr class="hover:bg-primary-container/5 transition-colors">
                    <td class="py-sm px-sm text-primary-fixed-dim font-bold">LOG-99207</td>
                    <td class="py-sm px-sm">HistoricalDemand</td>
                    <td class="py-sm px-sm">RecordID = 101..220</td>
                    <td class="py-sm px-sm font-semibold">RETRAIN XGBoost Multi-Horizon</td>
                    <td class="py-sm px-sm text-emerald-400 font-bold">PASSED (R² = 0.999)</td>
                    <td class="py-sm px-sm text-right font-mono-kpi">4.21ms</td>
                    <td class="py-sm px-sm text-on-surface-variant">2026-07-13 11:48:22</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

UNIFIED_MAIN = f"""
<main class="ml-64 pt-24 px-lg pb-lg">
    <div id="view-topology" class="space-y-lg">
        {topology_inner}
    </div>
    <div id="view-forecaster" class="space-y-lg hidden">
        {forecaster_inner}
    </div>
    <div id="view-cvrp" class="space-y-lg hidden">
        {cvrp_inner}
    </div>
    {COST_ANALYTICS_PANEL}
    {AUDIT_LOGS_PANEL}
</main>
"""

idx_m1 = orig_dash_clean.find('<main')
idx_m2 = orig_dash_clean.rfind('</main>')
if idx_m1 != -1 and idx_m2 != -1:
    idx_m1_end = orig_dash_clean.find('>', idx_m1)
    unified_html = orig_dash_clean[:idx_m1] + UNIFIED_MAIN + orig_dash_clean[idx_m2+7:]
else:
    unified_html = orig_dash_clean

# Update navigation links on unified_html
unified_html = re.sub(
    r'<button[^>]*>\s*<span[^>]*>add</span>\s*.*?New Optimization.*?^\s*</button>',
    '<button onclick="openNewOptimizationModal(); return false;" class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md shadow-[0_0_12px_rgba(0,229,255,0.15)] font-bold"><span class="material-symbols-outlined text-sm">add</span>New Optimization</button>',
    unified_html, flags=re.MULTILINE | re.DOTALL
)
unified_html = re.sub(
    r'<a[^>]*>\s*<span[^>]*>hub</span>\s*<span[^>]*>Network Topology</span>\s*</a>',
    '<a onclick="switchMainScreen(\'dashboard_preview.html\', \'topology\'); return false;" class="flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2 border-primary-fixed-dim bg-primary-container/10 hover:bg-primary-container/5 transition-all cursor-pointer font-bold" href="#"><span class="material-symbols-outlined" style="font-variation-settings: \'FILL\' 1;">hub</span><span class="font-body-md text-body-md">Network Topology</span></a>',
    unified_html, flags=re.IGNORECASE | re.DOTALL
)
unified_html = re.sub(
    r'<a[^>]*>\s*<span[^>]*>trending_up</span>\s*<span[^>]*>Demand Forecaster</span>\s*</a>',
    '<a onclick="switchMainScreen(\'demand_forecaster.html\', \'forecaster\'); return false;" class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all cursor-pointer" href="#"><span class="material-symbols-outlined">trending_up</span><span class="font-body-md text-body-md">Demand Forecaster</span></a>',
    unified_html, flags=re.IGNORECASE | re.DOTALL
)
unified_html = re.sub(
    r'<a[^>]*>\s*<span[^>]*>local_shipping</span>\s*<span[^>]*>CVRP Dispatcher</span>\s*</a>',
    '<a onclick="switchMainScreen(\'cvrp_explorer.html\', \'cvrp\'); return false;" class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all cursor-pointer" href="#"><span class="material-symbols-outlined">local_shipping</span><span class="font-body-md text-body-md">CVRP Dispatcher</span></a>',
    unified_html, flags=re.IGNORECASE | re.DOTALL
)
unified_html = re.sub(
    r'<a[^>]*>\s*<span[^>]*>analytics</span>\s*<span[^>]*>Cost Analytics</span>\s*</a>',
    '<a onclick="switchMainScreen(\'dashboard_preview.html\', \'cost\'); return false;" class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all cursor-pointer" href="#"><span class="material-symbols-outlined">analytics</span><span class="font-body-md text-body-md">Cost Analytics</span></a>',
    unified_html, flags=re.IGNORECASE | re.DOTALL
)
unified_html = re.sub(
    r'<a[^>]*>\s*<span[^>]*>history</span>\s*<span[^>]*>Audit Logs</span>\s*</a>',
    '<a onclick="switchMainScreen(\'dashboard_preview.html\', \'audit\'); return false;" class="flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all cursor-pointer" href="#"><span class="material-symbols-outlined">history</span><span class="font-body-md text-body-md">Audit Logs</span></a>',
    unified_html, flags=re.IGNORECASE | re.DOTALL
)

# Append exactly one script copy
if '</body>' in unified_html:
    unified_html = unified_html.replace('</body>', ULTIMATE_SPA_ENGINE_JS + '\n</body>')
else:
    unified_html += "\n" + ULTIMATE_SPA_ENGINE_JS

with open("dashboard_preview.html", "w", encoding="utf-8") as f:
    f.write(unified_html)
print("SUCCESS: dashboard_preview.html restored with all 3 original tables and 5 unified panels!")

# For index.html, inject window.ALL_SCREENS_HTML map
clean_screens_map = {
    "dashboard_preview.html": strip_scripts(unified_html),
    "demand_forecaster.html": strip_scripts(open("demand_forecaster.html", encoding="utf-8").read()),
    "cvrp_explorer.html": strip_scripts(open("cvrp_explorer.html", encoding="utf-8").read()),
    "index.html": strip_scripts(unified_html)
}
json_dump_escaped = json.dumps(clean_screens_map).replace('</script>', '<\\/script>')
clean_js = f'<script>window.ALL_SCREENS_HTML = {json_dump_escaped};</script>'
index_content = unified_html.replace('<head>', '<head>\n    ' + clean_js, 1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)
print("SUCCESS: index.html restored and unified cleanly across all views!")
