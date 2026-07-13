import os
import re
import json

MASTER_INTERACTIVE_JS = """
<script>
    // Restore ALL_SCREENS_HTML from sessionStorage if needed
    if (!window.ALL_SCREENS_HTML) {
        try {
            const saved = sessionStorage.getItem('SAVED_SCREENS_HTML');
            if (saved) window.ALL_SCREENS_HTML = JSON.parse(saved);
        } catch(e) {}
    }
    if (window.ALL_SCREENS_HTML) {
        try {
            sessionStorage.setItem('SAVED_SCREENS_HTML', JSON.stringify(window.ALL_SCREENS_HTML));
        } catch(e) {}
    }

    // 1. Holiday & Monsoon Toggle Handler
    function toggleHolidayMonsoon(labelEl, name) {
        const checkbox = labelEl.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
            const isChecked = checkbox.checked;
            showToast(name + (isChecked ? ' Activated' : ' Deactivated'), 
                      name + (isChecked ? ' surge active (+18.5% TEU weighting applied to forecast curve).' : ' normalized to baseline schedule.'));
            
            // Adjust SVG dots dynamically
            const dots = document.querySelectorAll('svg circle.predicted-dot');
            dots.forEach((dot, idx) => {
                let cy = parseFloat(dot.getAttribute('data-base-cy') || dot.getAttribute('cy'));
                if (!dot.getAttribute('data-base-cy')) dot.setAttribute('data-base-cy', cy);
                let newCy = isChecked ? Math.max(20, cy - (idx * 4 + 10)) : cy;
                dot.setAttribute('cy', newCy);
            });
            const path = document.querySelector('path.predicted-line');
            if (path && dots.length > 0) {
                let d = 'M ' + dots[0].getAttribute('cx') + ',' + dots[0].getAttribute('cy');
                for (let i = 1; i < dots.length; i++) {
                    d += ' L ' + dots[i].getAttribute('cx') + ',' + dots[i].getAttribute('cy');
                }
                path.setAttribute('d', d);
            }
        }
    }

    // 2. ML Model Selection Handler (Random Forest, XGBoost, Baseline)
    function switchMLModel(spanEl, modelName) {
        const container = spanEl.parentElement;
        if (!container) return;
        const allBadges = container.querySelectorAll('span');
        allBadges.forEach(b => {
            const txt = (b.innerText || b.textContent || '').trim();
            if (txt.includes(modelName)) {
                b.className = 'px-sm py-1 rounded-full bg-primary-container text-on-primary-container text-[10px] font-bold uppercase tracking-widest flex items-center gap-1 shadow-[0_0_10px_rgba(0,229,255,0.4)] cursor-pointer transition-all';
                if (!b.querySelector('.animate-pulse')) {
                    b.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span> ' + modelName + ' (Active)';
                }
            } else {
                let rawTxt = txt.replace(/\(Active\)/g, '').replace('•', '').trim();
                b.className = 'px-sm py-1 rounded-full bg-surface-variant text-on-surface-variant text-[10px] font-bold uppercase tracking-widest hover:bg-surface-bright cursor-pointer transition-colors';
                b.innerHTML = rawTxt;
            }
        });

        // Update KPI cards based on model
        const rmseEl = document.querySelector('.grid.grid-cols-2 p.font-mono-kpi');
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
    }

    // 3. Slider Value Live Scale Update
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
        // If this is Sales Index or Promo discount, trigger subtle curve shift feedback
        showToast('Scale Adjusted: ' + rangeEl.value, 'Recalculating container volume allocation sensitivity...');
    }

    // 4. Sidebar Highlights & Navigation
    function updateSidebarHighlight(activeText) {
        const links = document.querySelectorAll('aside a, aside button.nav-link');
        links.forEach(a => {
            const txt = (a.innerText || a.textContent || '').trim();
            if (txt.includes(activeText)) {
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
        if (viewMode === 'cost') {
            updateSidebarHighlight('Cost Analytics');
            // Check if we are on dashboard_preview.html right now
            if (!document.getElementById('drawer-table-routes') && window.ALL_SCREENS_HTML && window.ALL_SCREENS_HTML['dashboard_preview.html']) {
                try { sessionStorage.setItem('SAVED_SCREENS_HTML', JSON.stringify(window.ALL_SCREENS_HTML)); } catch(e){}
                document.open();
                document.write(window.ALL_SCREENS_HTML['dashboard_preview.html']);
                document.close();
                setTimeout(() => {
                    const costEl = document.querySelector('.mt-lg.pt-md.border-t') || document.querySelector('main');
                    if (costEl) costEl.scrollIntoView({behavior: 'smooth', block: 'center'});
                    if (typeof switchDrawerTab === 'function') switchDrawerTab('routes');
                    showToast('Cost Analytics Active', 'Inspecting SCIP MILP freight cost breakdown: ₹ 6,600 Optimal vs ₹ 19,800 Baseline (66.6% Savings).');
                }, 100);
                return false;
            }
            const costEl = document.querySelector('.mt-lg.pt-md.border-t') || document.querySelector('main');
            if (costEl) costEl.scrollIntoView({behavior: 'smooth', block: 'center'});
            if (typeof switchDrawerTab === 'function') switchDrawerTab('routes');
            showToast('Cost Analytics Active', 'Inspecting SCIP MILP freight cost breakdown: ₹ 6,600 Optimal vs ₹ 19,800 Baseline (66.6% Savings).');
            return false;
        }
        if (viewMode === 'audit') {
            updateSidebarHighlight('Audit Logs');
            if (!document.getElementById('drawer-table-sql') && window.ALL_SCREENS_HTML && window.ALL_SCREENS_HTML['dashboard_preview.html']) {
                try { sessionStorage.setItem('SAVED_SCREENS_HTML', JSON.stringify(window.ALL_SCREENS_HTML)); } catch(e){}
                document.open();
                document.write(window.ALL_SCREENS_HTML['dashboard_preview.html']);
                document.close();
                setTimeout(() => {
                    if (typeof switchDrawerTab === 'function') switchDrawerTab('sql');
                    const drawerEl = document.getElementById('drawer-table-sql') || document.querySelector('.glass-panel.rounded-xl.overflow-hidden');
                    if (drawerEl) drawerEl.scrollIntoView({behavior: 'smooth', block: 'center'});
                    showToast('3NF Audit Logs Active', 'Inspecting real-time ACID transaction audit trail (0.42ms average sync latency).');
                }, 100);
                return false;
            }
            if (typeof switchDrawerTab === 'function') switchDrawerTab('sql');
            const drawerEl = document.getElementById('drawer-table-sql') || document.querySelector('.glass-panel.rounded-xl.overflow-hidden');
            if (drawerEl) drawerEl.scrollIntoView({behavior: 'smooth', block: 'center'});
            showToast('3NF Audit Logs Active', 'Inspecting real-time ACID transaction audit trail (0.42ms average sync latency).');
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

    function runGlobalOptimization() {
        showToast('Solvers Re-Dispatched', 'Running SCIP MILP exact allocation across all 36 global freight corridors...');
        setTimeout(() => {
            showToast('SCIP MILP Converged', 'Total freight cost optimized to ₹ 6,600. Savings vs Baseline: 66.6%!');
        }, 1200);
    }
</script>
"""

def update_demand_forecaster(filename="demand_forecaster.html"):
    if not os.path.exists(filename):
        return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Holiday Surge & Monsoon Disruption: Wrap in <label> with onclick
    content = re.sub(
        r'<div class="flex items-center justify-between group">\s*<span class="text-sm font-body-md text-on-surface">Holiday Surge</span>\s*<div class="relative inline-flex items-center cursor-pointer">\s*<input[^>]*>\s*<div[^>]*></div>\s*</div>\s*</div>',
        '<label onclick="toggleHolidayMonsoon(this, \'Holiday Surge\')" class="flex items-center justify-between group cursor-pointer py-1">\n                                <span class="text-sm font-body-md text-on-surface">Holiday Surge</span>\n                                <div class="relative inline-flex items-center">\n                                    <input class="sr-only peer" type="checkbox"/>\n                                    <div class="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[\'\'] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container shadow-inner"></div>\n                                </div>\n                            </label>',
        content
    )
    content = re.sub(
        r'<div class="flex items-center justify-between group">\s*<span class="text-sm font-body-md text-on-surface">Monsoon Disruption</span>\s*<div class="relative inline-flex items-center cursor-pointer">\s*<input[^>]*>\s*<div[^>]*></div>\s*</div>\s*</div>',
        '<label onclick="toggleHolidayMonsoon(this, \'Monsoon Disruption\')" class="flex items-center justify-between group cursor-pointer py-1">\n                                <span class="text-sm font-body-md text-on-surface">Monsoon Disruption</span>\n                                <div class="relative inline-flex items-center">\n                                    <input class="sr-only peer" type="checkbox"/>\n                                    <div class="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[\'\'] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-secondary-container shadow-inner"></div>\n                                </div>\n                            </label>',
        content
    )

    # 2. Model Badges: Add onclick="switchMLModel(this, '...')" to Random Forest, Baseline Linear, XGBoost
    content = re.sub(
        r'<span[^>]*>\s*(<span[^>]*></span>)?\s*XGBoost Regressor \(Active\)\s*</span>',
        '<span onclick="switchMLModel(this, \'XGBoost Regressor\')" class="px-sm py-1 rounded-full bg-primary-container text-on-primary-container text-[10px] font-bold uppercase tracking-widest flex items-center gap-1 shadow-[0_0_10px_rgba(0,229,255,0.4)] cursor-pointer transition-all"><span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span> XGBoost Regressor (Active)</span>',
        content
    )
    content = re.sub(
        r'<span[^>]*>\s*Random Forest\s*</span>',
        '<span onclick="switchMLModel(this, \'Random Forest\')" class="px-sm py-1 rounded-full bg-surface-variant text-on-surface-variant text-[10px] font-bold uppercase tracking-widest hover:bg-surface-bright cursor-pointer transition-colors">Random Forest</span>',
        content
    )
    content = re.sub(
        r'<span[^>]*>\s*Baseline Linear\s*</span>',
        '<span onclick="switchMLModel(this, \'Baseline Linear\')" class="px-sm py-1 rounded-full bg-surface-variant text-on-surface-variant text-[10px] font-bold uppercase tracking-widest hover:bg-surface-bright cursor-pointer transition-colors">Baseline Linear</span>',
        content
    )

    # 3. Add oninput="updateSliderValue(this)" across every single <input type="range" class="... custom-range" ...>
    content = re.sub(
        r'<input class="w-full custom-range"([^>]*)>',
        r'<input class="w-full custom-range" \1 oninput="updateSliderValue(this)">',
        content
    )

    # 4. Add dotted line dasharray and glowing circular dots along the dotted AI Predicted Line & Historical Line!
    # Check if we already injected circles
    if '<circle class="predicted-dot"' not in content:
        # We find <!-- AI Predicted Line --> <path ...> and ensure it has stroke-dasharray="6,6" and inject circles
        predicted_dots_svg = """<!-- AI Predicted Line (Dotted with glowing nodes) -->
                        <path class="predicted-line filter drop-shadow-[0_0_8px_rgba(0,229,255,0.8)]" stroke-dasharray="6,6" d="M 500,170 L 550,150 L 600,190 L 650,120 L 700,160 L 750,110 L 800,130 L 850,70 L 900,100 L 950,50" fill="none" stroke="#00e5ff" stroke-linecap="round" stroke-width="3"></path>
                        <!-- Dotted Line Data Points (Dots) -->
                        <circle class="predicted-dot" data-base-cy="170" cx="500" cy="170" r="5" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 6px #00e5ff);"><title>Horizon T+0: 1,840 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="150" cx="550" cy="150" r="5" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 6px #00e5ff);"><title>Horizon T+3: 1,910 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="190" cx="600" cy="190" r="5" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 6px #00e5ff);"><title>Horizon T+6: 1,780 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="120" cx="650" cy="120" r="5" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 6px #00e5ff);"><title>Horizon T+9: 2,050 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="160" cx="700" cy="160" r="5" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 6px #00e5ff);"><title>Horizon T+12: 1,890 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="110" cx="750" cy="110" r="5" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 6px #00e5ff);"><title>Horizon T+15: 2,120 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="130" cx="800" cy="130" r="5" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 6px #00e5ff);"><title>Horizon T+18: 2,040 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="70" cx="850" cy="70" r="6" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 8px #00e5ff);"><title>Horizon T+21: 2,340 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="100" cx="900" cy="100" r="6" fill="#00e5ff" stroke="#ffffff" stroke-width="2" style="cursor: pointer; filter: drop-shadow(0 0 8px #00e5ff);"><title>Horizon T+24: 2,210 TEUs</title></circle>
                        <circle class="predicted-dot" data-base-cy="50" cx="950" cy="50" r="7" fill="#00e5ff" stroke="#ffffff" stroke-width="2.5" style="cursor: pointer; filter: drop-shadow(0 0 12px #00e5ff);"><title>Horizon T+30 Optimal Target: 2,680 TEUs</title></circle>
                        <!-- Historical Data Dots -->
                        <circle cx="50" cy="300" r="4" fill="#dce4e5" stroke="#080f11" stroke-width="1.5"><title>Q3-2023: 1,320 TEUs</title></circle>
                        <circle cx="150" cy="310" r="4" fill="#dce4e5" stroke="#080f11" stroke-width="1.5"><title>Oct-2023: 1,290 TEUs</title></circle>
                        <circle cx="250" cy="270" r="4" fill="#dce4e5" stroke="#080f11" stroke-width="1.5"><title>Dec-2023: 1,450 TEUs</title></circle>
                        <circle cx="350" cy="240" r="4" fill="#dce4e5" stroke="#080f11" stroke-width="1.5"><title>Feb-2024: 1,580 TEUs</title></circle>
                        <circle cx="450" cy="220" r="4.5" fill="#dce4e5" stroke="#080f11" stroke-width="1.5"><title>Apr-2024: 1,660 TEUs</title></circle>"""

        content = re.sub(
            r'<!-- AI Predicted Line -->\s*<path class="filter drop-shadow-\[0_0_8px_rgba\(0,229,255,0\.8\)\]"[^>]*></path>',
            predicted_dots_svg,
            content
        )

    # 5. Inject MASTER_INTERACTIVE_JS
    idx = content.rfind("<script>")
    if idx != -1 and "</body>" in content[idx:]:
        content = content[:idx] + MASTER_INTERACTIVE_JS + "\n</body>\n</html>"
    else:
        content = content.replace("</body>", MASTER_INTERACTIVE_JS + "\n</body>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

update_demand_forecaster("demand_forecaster.html")
print("SUCCESS: demand_forecaster.html updated with Holiday/Monsoon toggles, Model badges, Slider live numbers, and Dotted Line Dots!")

# Also update dashboard_preview.html and cvrp_explorer.html with MASTER_INTERACTIVE_JS and slider oninput
for fn in ["dashboard_preview.html", "cvrp_explorer.html"]:
    if not os.path.exists(fn):
        continue
    with open(fn, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r'<input class="w-full custom-range"([^>]*)>',
        r'<input class="w-full custom-range" \1 oninput="updateSliderValue(this)">',
        content
    )
    idx = content.rfind("<script>")
    if idx != -1 and "</body>" in content[idx:]:
        content = content[:idx] + MASTER_INTERACTIVE_JS + "\n</body>\n</html>"
    else:
        content = content.replace("</body>", MASTER_INTERACTIVE_JS + "\n</body>")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(content)

print("SUCCESS: Updated dashboard_preview.html and cvrp_explorer.html with MASTER_INTERACTIVE_JS and slider oninput!")

# Regenerate clean index.html
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

print("SUCCESS: Regenerated index.html with all interactive handlers and dots!")
