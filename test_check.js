
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

        // Fallback if inside standalone page
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

    // Realistic Forecast Recalculation Engine
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

        // Base coordinates for T+0 to T+30
        const baseCy = [170, 150, 190, 120, 160, 110, 130, 70, 100, 50];
        const newCy = [];

        for (let i = 0; i < baseCy.length; i++) {
            let y = baseCy[i];
            if (activeModel === 'Random Forest') {
                // Step-wise tree thresholds
                y = Math.round(y * 0.95 + (i % 3 === 0 ? -18 : 12));
            } else if (activeModel === 'Baseline Linear') {
                // Linear OLS trend
                y = 175 - (i * 13.5);
            }

            if (isMon) {
                // Monsoon port bottleneck causes slump from T+6 to T+18 (indices 2 to 6)
                if (i >= 2 && i <= 6) y += 85; 
            }
            if (isHol) {
                // Holiday peak demand causes massive upward surge from T+18 to T+30 (indices 6 to 9)
                if (i >= 6) y -= 65; 
            }
            y = Math.max(25, Math.min(345, y));
            newCy.push(y);
            if (dots[i]) {
                dots[i].setAttribute('cy', y);
                dots[i].setAttribute('data-base-cy', y);
            }
        }

        // Update path string
        const path = document.querySelector('#view-forecaster path.predicted-line, path.predicted-line');
        if (path && newCy.length > 0) {
            let d = 'M 500,' + newCy[0];
            const cxs = [500, 550, 600, 650, 700, 750, 800, 850, 900, 950];
            for (let i = 1; i < newCy.length; i++) {
                d += ' L ' + cxs[i] + ',' + newCy[i];
            }
            path.setAttribute('d', d);
        }

        // Update scanning dot vertical motion on the dotted line!
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
