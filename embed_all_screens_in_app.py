import re

# 1. Update navigateToScreen in dashboard_preview.html, demand_forecaster.html, cvrp_explorer.html
nav_js = """<script>
    function navigateToScreen(targetScreen) {
        // 1. INSTANT LOCAL SWITCH: Check if all screens are pre-embedded in window.ALL_SCREENS_HTML (from Streamlit app.py!)
        try {
            if (window.ALL_SCREENS_HTML && window.ALL_SCREENS_HTML[targetScreen]) {
                document.open();
                document.write(window.ALL_SCREENS_HTML[targetScreen]);
                document.close();
                return;
            }
        } catch(e) {}

        // 2. Check if we are inside index.html iframe master portal
        try {
            if (window.parent && window.parent.switchTab && typeof window.parent.switchTab === 'function') {
                window.parent.switchTab(targetScreen);
                return;
            }
        } catch(e) {}

        // 3. Check if we can click Streamlit parent radio buttons
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

        // 4. Fallback to fetch or window.location
        fetch(targetScreen)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.text();
            })
            .then(html => {
                document.open();
                document.write(html);
                document.close();
            })
            .catch(err => {
                try { window.location.href = targetScreen; } catch(e) {}
            });
    }
"""

for fn in ['dashboard_preview.html', 'demand_forecaster.html', 'cvrp_explorer.html']:
    with open(fn, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = re.sub(r'function navigateToScreen\(.*?\}\n\s*\}', nav_js.replace('<script>', '').strip(), html, flags=re.DOTALL)
    
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated navigateToScreen with instant ALL_SCREENS_HTML check in {fn}!")

# 2. Update app.py to inject window.ALL_SCREENS_HTML into the html_code before rendering components.html
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

old_block = """    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            html_code = f.read()
            
        # Dynamically inject live data into the HTML code before rendering!
        if "Network Topology" in mockup_view:
            html_code = ui_engine.populate_network_topology(html_code, st.session_state.get("opt_results"), warehouses_df, active_customers_df)
        elif "Demand Forecaster" in mockup_view:
            html_code = ui_engine.populate_demand_forecaster(html_code, st.session_state.get("live_fc_metrics"), st.session_state.get("forecast_df"))
        else:
            html_code = ui_engine.populate_cvrp_explorer(html_code, st.session_state.get("cvrp_live_res"), st.session_state.get("live_dep", "Port of Rotterdam"))
            
        components.html(html_code, height=950, scrolling=True)"""

new_block = """    if os.path.exists(file_path):
        with open("dashboard_preview.html", "r", encoding="utf-8") as f:
            h_dash = ui_engine.populate_network_topology(f.read(), st.session_state.get("opt_results"), warehouses_df, active_customers_df)
        with open("demand_forecaster.html", "r", encoding="utf-8") as f:
            h_fc = ui_engine.populate_demand_forecaster(f.read(), st.session_state.get("live_fc_metrics"), st.session_state.get("forecast_df"))
        with open("cvrp_explorer.html", "r", encoding="utf-8") as f:
            h_cvrp = ui_engine.populate_cvrp_explorer(f.read(), st.session_state.get("cvrp_live_res"), st.session_state.get("live_dep", "Port of Rotterdam"))
        
        import json
        all_screens_js = f'<script>window.ALL_SCREENS_HTML = {{ "dashboard_preview.html": {json.dumps(h_dash)}, "demand_forecaster.html": {json.dumps(h_fc)}, "cvrp_explorer.html": {json.dumps(h_cvrp)} }};</script>'
        
        if "Network Topology" in mockup_view:
            html_code = h_dash.replace('<head>', '<head>' + all_screens_js, 1)
        elif "Demand Forecaster" in mockup_view:
            html_code = h_fc.replace('<head>', '<head>' + all_screens_js, 1)
        else:
            html_code = h_cvrp.replace('<head>', '<head>' + all_screens_js, 1)
            
        components.html(html_code, height=950, scrolling=True)"""

if old_block in app_code:
    app_code = app_code.replace(old_block, new_block, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("Successfully updated app.py to embed all 3 screens into window.ALL_SCREENS_HTML!")
else:
    print("WARNING: exact old_block not found in app.py, inspecting...")
