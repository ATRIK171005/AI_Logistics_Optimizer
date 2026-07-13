import os
import re
import json

COMPLETE_JS = """
<script>
    function navigateToScreen(targetScreen) {
        try {
            if (window.ALL_SCREENS_HTML && window.ALL_SCREENS_HTML[targetScreen]) {
                document.open();
                document.write(window.ALL_SCREENS_HTML[targetScreen]);
                document.close();
                return;
            }
        } catch(e) {}

        try {
            if (window.parent && window.parent.switchTab && typeof window.parent.switchTab === 'function') {
                window.parent.switchTab(targetScreen);
                return;
            }
        } catch(e) {}

        try {
            if (window.parent && window.parent.document) {
                const labels = window.parent.document.querySelectorAll('div[role="radiogroup"] label, label[data-baseweb="radio"], p, span, div[data-testid="stRadio"] label');
                if (labels && labels.length > 0) {
                    for (let label of labels) {
                        const txt = label.innerText || label.textContent || '';
                        if (
                            (targetScreen === 'dashboard_preview.html' && (txt.includes('Network Topology') || txt.includes('Allocation Hub'))) ||
                            (targetScreen === 'demand_forecaster.html' && (txt.includes('Demand Forecaster') || txt.includes('Macro Simulation'))) ||
                            (targetScreen === 'cvrp_explorer.html' && (txt.includes('CVRP') || txt.includes('Fleet Dispatch')))
                        ) {
                            label.click();
                            showToast('Switched Screen', 'Navigating to ' + targetScreen);
                            return;
                        }
                    }
                }
            }
        } catch (e) {}

        try {
            window.location.href = targetScreen;
        } catch(e) {}
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
                showToast('SCIP MILP Converged', 'Custom network hub allocation solved in 14.8ms. Freight cost: $1,098,400 | Savings: 68.2%');
            } else if (eng === 'xgb') {
                showToast('XGBoost Multi-Horizon Retrained', 'Custom 30-day forecast generated across Rotterdam Hub cluster (`R² = 0.982`).');
            } else {
                showToast('OR-Tools GLS Dispatched', 'Custom multi-stop loops scheduled for Rotterdam Depot across 16 active EV trucks.');
            }
        }, 800);
    }

    function runGlobalOptimization() {
        showToast('Solvers Re-Dispatched', 'Running SCIP MILP exact allocation across all 36 global freight corridors...');
        setTimeout(() => {
            showToast('SCIP MILP Converged', 'Total freight cost optimized to ₹ 6,600. Savings vs Baseline: 66.6%!');
        }, 1200);
    }
</script>
"""

# HTML for the 3 switching tables inside Data Drawer
AI_DIAG_TABLE = """
<table id="drawer-table-ai" class="w-full text-left border-collapse" style="display: none;">
    <thead>
    <tr class="text-[11px] uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20">
        <th class="pb-sm px-xs font-medium">Cluster ID</th>
        <th class="pb-sm px-xs font-medium">ML Model</th>
        <th class="pb-sm px-xs font-medium">Horizon</th>
        <th class="pb-sm px-xs font-medium text-right">RMSE (TEUs)</th>
        <th class="pb-sm px-xs font-medium text-right">MAE</th>
        <th class="pb-sm px-xs font-medium text-right">MAPE (%)</th>
        <th class="pb-sm px-xs font-medium text-right">R² Accuracy</th>
        <th class="pb-sm px-xs font-medium">Drift Status</th>
    </tr>
    </thead>
    <tbody class="font-mono-label text-[13px]">
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">ROT_NORTH_01</td>
        <td class="py-sm px-xs">XGBoost-Multi</td>
        <td class="py-sm px-xs">30 Days</td>
        <td class="py-sm px-xs text-right">0.99</td>
        <td class="py-sm px-xs text-right">0.70</td>
        <td class="py-sm px-xs text-right text-emerald-400">0.35%</td>
        <td class="py-sm px-xs text-right font-bold text-primary-fixed-dim">0.999</td>
        <td class="py-sm px-xs"><span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px]">STABLE</span></td>
    </tr>
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">MUM_WEST_02</td>
        <td class="py-sm px-xs">XGBoost-Multi</td>
        <td class="py-sm px-xs">30 Days</td>
        <td class="py-sm px-xs text-right">1.24</td>
        <td class="py-sm px-xs text-right">0.95</td>
        <td class="py-sm px-xs text-right text-emerald-400">0.82%</td>
        <td class="py-sm px-xs text-right font-bold text-primary-fixed-dim">0.994</td>
        <td class="py-sm px-xs"><span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px]">STABLE</span></td>
    </tr>
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">SNG_EAST_03</td>
        <td class="py-sm px-xs">XGBoost-Multi</td>
        <td class="py-sm px-xs">30 Days</td>
        <td class="py-sm px-xs text-right">1.12</td>
        <td class="py-sm px-xs text-right">0.88</td>
        <td class="py-sm px-xs text-right text-emerald-400">0.61%</td>
        <td class="py-sm px-xs text-right font-bold text-primary-fixed-dim">0.996</td>
        <td class="py-sm px-xs"><span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px]">STABLE</span></td>
    </tr>
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">AMS_EURO_04</td>
        <td class="py-sm px-xs">Ensemble-LGBM</td>
        <td class="py-sm px-xs">30 Days</td>
        <td class="py-sm px-xs text-right">0.85</td>
        <td class="py-sm px-xs text-right">0.62</td>
        <td class="py-sm px-xs text-right text-emerald-400">0.29%</td>
        <td class="py-sm px-xs text-right font-bold text-primary-fixed-dim">0.999</td>
        <td class="py-sm px-xs"><span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px]">STABLE</span></td>
    </tr>
    </tbody>
</table>
"""

SQL_AUDIT_TABLE = """
<table id="drawer-table-sql" class="w-full text-left border-collapse" style="display: none;">
    <thead>
    <tr class="text-[11px] uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20">
        <th class="pb-sm px-xs font-medium">Audit ID</th>
        <th class="pb-sm px-xs font-medium">3NF Entity Table</th>
        <th class="pb-sm px-xs font-medium">Primary Key</th>
        <th class="pb-sm px-xs font-medium">Mutation Action</th>
        <th class="pb-sm px-xs font-medium">Constraint Check</th>
        <th class="pb-sm px-xs font-medium text-right">Latency</th>
        <th class="pb-sm px-xs font-medium">Sync Timestamp</th>
    </tr>
    </thead>
    <tbody class="font-mono-label text-[13px]">
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">LOG-99201</td>
        <td class="py-sm px-xs">Warehouses (3NF)</td>
        <td class="py-sm px-xs">WarehouseID = 'Hub_A'</td>
        <td class="py-sm px-xs">UPDATE CapacityTEU -> 2600</td>
        <td class="py-sm px-xs text-emerald-400 font-bold">PASSED (CHECK > 0)</td>
        <td class="py-sm px-xs text-right">0.42ms</td>
        <td class="py-sm px-xs text-on-surface-variant">2026-07-13 11:24:00</td>
    </tr>
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">LOG-99202</td>
        <td class="py-sm px-xs">Customers (3NF)</td>
        <td class="py-sm px-xs">CustomerID = 'Dest_B'</td>
        <td class="py-sm px-xs">SYNC MonthlyDemand -> 1000</td>
        <td class="py-sm px-xs text-emerald-400 font-bold">PASSED (FK Valid)</td>
        <td class="py-sm px-xs text-right">0.38ms</td>
        <td class="py-sm px-xs text-on-surface-variant">2026-07-13 11:24:01</td>
    </tr>
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">LOG-99203</td>
        <td class="py-sm px-xs">TransportationCost</td>
        <td class="py-sm px-xs">RouteKey = 'Hub_A_Dest_B'</td>
        <td class="py-sm px-xs">CALCULATE UnitCost -> ₹ 500</td>
        <td class="py-sm px-xs text-emerald-400 font-bold">PASSED (3NF Indexed)</td>
        <td class="py-sm px-xs text-right">0.51ms</td>
        <td class="py-sm px-xs text-on-surface-variant">2026-07-13 11:24:02</td>
    </tr>
    <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
        <td class="py-sm px-xs text-primary-fixed-dim font-bold">LOG-99204</td>
        <td class="py-sm px-xs">Shipments (MILP Res)</td>
        <td class="py-sm px-xs">ShipmentID = 1010..1014</td>
        <td class="py-sm px-xs">COMMIT SCIP Optimal Plan</td>
        <td class="py-sm px-xs text-emerald-400 font-bold">PASSED (ACID Transaction)</td>
        <td class="py-sm px-xs text-right">1.12ms</td>
        <td class="py-sm px-xs text-on-surface-variant">2026-07-13 11:24:05</td>
    </tr>
    </tbody>
</table>
"""

def update_template(filename):
    if not os.path.exists(filename):
        return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Strip out old/broken script block right above </body>
    idx = content.rfind("<script>")
    if idx != -1 and "</body>" in content[idx:]:
        content = content[:idx] + COMPLETE_JS + "\n</body>\n</html>"
    else:
        content = content.replace("</body>", COMPLETE_JS + "\n</body>")

    # 2. Ensure drawer table headers have id="tab-btn-routes", id="tab-btn-ai", id="tab-btn-sql" and onclick handlers
    content = re.sub(
        r'<button[^>]*>\s*Active Routes &amp; TEU Allocation\s*</button>',
        '<button id="tab-btn-routes" onclick="switchDrawerTab(\'routes\')" class="px-md py-sm text-sm font-bold text-primary-fixed-dim border-b-2 border-primary-fixed-dim bg-primary-container/5 transition-all">Active Routes &amp; TEU Allocation</button>',
        content
    )
    content = re.sub(
        r'<button[^>]*>\s*AI Forecaster Diagnostics\s*</button>',
        '<button id="tab-btn-ai" onclick="switchDrawerTab(\'ai\')" class="px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all">AI Forecaster Diagnostics</button>',
        content
    )
    content = re.sub(
        r'<button[^>]*>\s*3NF SQLite Audit Trail\s*</button>',
        '<button id="tab-btn-sql" onclick="switchDrawerTab(\'sql\')" class="px-md py-sm text-sm text-on-surface-variant hover:text-primary hover:bg-surface-variant/20 transition-all">3NF SQLite Audit Trail</button>',
        content
    )

    # 3. Ensure the active routes table has id="drawer-table-routes" and append AI & SQL tables inside the overflow drawer div
    if 'id="drawer-table-routes"' not in content:
        content = content.replace('<table class="w-full text-left border-collapse">', '<table id="drawer-table-routes" class="w-full text-left border-collapse">', 1)
    
    if 'id="drawer-table-ai"' not in content:
        # Find closing of drawer-table-routes
        idx_t = content.find('id="drawer-table-routes"')
        if idx_t != -1:
            idx_end_t = content.find('</table>', idx_t)
            if idx_end_t != -1:
                content = content[:idx_end_t+8] + "\n" + AI_DIAG_TABLE + "\n" + SQL_AUDIT_TABLE + content[idx_end_t+8:]

    # 4. Ensure New Optimization button calls openNewOptimizationModal
    if 'openNewOptimizationModal()' not in content and '+ New Optimization' in content:
        content = re.sub(
            r'<button[^>]*>\s*<span[^>]*>add</span>\s*<span>New Optimization</span>\s*</button>',
            '<button onclick="openNewOptimizationModal()" class="w-full bg-gradient-to-r from-[#00E5FF]/20 to-[#3491ff]/20 border border-[#00E5FF]/50 text-[#00E5FF] py-2.5 px-3 rounded-lg flex items-center justify-center gap-2 hover:bg-[#00E5FF]/30 active:scale-95 transition-all shadow-[0_0_15px_rgba(0,229,255,0.2)] font-bold text-sm tracking-wide group"><span class="material-symbols-outlined text-base group-hover:rotate-90 transition-transform">add</span><span>New Optimization</span></button>',
            content
        )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

for fn in ["dashboard_preview.html", "demand_forecaster.html", "cvrp_explorer.html"]:
    update_template(fn)

print("SUCCESS: Updated dashboard_preview.html, demand_forecaster.html, and cvrp_explorer.html with COMPLETE_JS and interactive drawer tables!")

# Now regenerate clean index.html and update app.py
with open("dashboard_preview.html", "r", encoding="utf-8") as f:
    h_dash = f.read()
with open("demand_forecaster.html", "r", encoding="utf-8") as f:
    h_fc = f.read()
with open("cvrp_explorer.html", "r", encoding="utf-8") as f:
    h_cvrp = f.read()

def strip_all_screens(s):
    s = re.sub(r'<script>window\.ALL_SCREENS_HTML = \{.*?\};</script>\s*', '', s, flags=re.DOTALL)
    s = re.sub(r'window\.ALL_SCREENS_HTML = \{.*?\};\s*', '', s, flags=re.DOTALL)
    return s

h_dash = strip_all_screens(h_dash)
h_fc = strip_all_screens(h_fc)
h_cvrp = strip_all_screens(h_cvrp)

clean_screens_map = {
    "dashboard_preview.html": h_dash,
    "demand_forecaster.html": h_fc,
    "cvrp_explorer.html": h_cvrp,
    "index.html": h_dash
}

json_dump_str = json.dumps(clean_screens_map).replace('</script>', '<\\/script>')
clean_js = f'<script>window.ALL_SCREENS_HTML = {json_dump_str};</script>'

index_content = h_dash.replace('<head>', '<head>\n    ' + clean_js, 1)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)

print("SUCCESS: Regenerated index.html with all tabs, tables, and scripts included!")

# Update app.py to auto-compute opt_results BEFORE tab_mockup is rendered!
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Make sure opt_results auto-solves before tab_mockup
init_pattern = r'if "current_sql" not in st\.session_state:\s*st\.session_state\["current_sql"\] = "SELECT \* FROM Warehouses;"'
if re.search(init_pattern, app_code):
    replacement = """if "current_sql" not in st.session_state:
    st.session_state["current_sql"] = "SELECT * FROM Warehouses;"
if "opt_results" not in st.session_state:
    st.session_state["opt_results"] = None"""
    app_code = re.sub(init_pattern, replacement, app_code, count=1)

# Before # Main Navigation Tabs, let's inject auto solver if opt_results is None
tabs_pattern = r'# Main Navigation Tabs\s*tab_mockup, tab_opt'
if re.search(tabs_pattern, app_code):
    auto_solve_inject = """# Auto-solve SCIP MILP on initial startup so High-Fidelity UI Command Center has live optimal tables immediately
if st.session_state["opt_results"] is None:
    opt = optimizer.LogisticsOptimizer(warehouses_df, active_customers_df, cost_df, trucks_df)
    results = opt.solve()
    st.session_state["opt_results"] = results
    if results.get("status") in ["OPTIMAL", "FEASIBLE"]:
        database.save_shipments(results["shipments_df"])

# Main Navigation Tabs
tab_mockup, tab_opt"""
    app_code = re.sub(tabs_pattern, auto_solve_inject, app_code, count=1)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("SUCCESS: app.py updated to auto-compute MILP optimal plan before rendering Tab 0!")
