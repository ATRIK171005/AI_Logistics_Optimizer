import re
import json

# Read the three high-fidelity pages
with open('dashboard_preview.html', 'r', encoding='utf-8') as f:
    h_dash = f.read()
with open('demand_forecaster.html', 'r', encoding='utf-8') as f:
    h_fc = f.read()
with open('cvrp_explorer.html', 'r', encoding='utf-8') as f:
    h_cvrp = f.read()

# Clean up any residual window.ALL_SCREENS_HTML script blocks inside the strings so we don't nest strings infinitely
h_dash_clean = re.sub(r'<script>window\.ALL_SCREENS_HTML = \{.*?\};</script>', '', h_dash, flags=re.DOTALL)
h_fc_clean = re.sub(r'<script>window\.ALL_SCREENS_HTML = \{.*?\};</script>', '', h_fc, flags=re.DOTALL)
h_cvrp_clean = re.sub(r'<script>window\.ALL_SCREENS_HTML = \{.*?\};</script>', '', h_cvrp, flags=re.DOTALL)

# Ensure navigateToScreen in all three cleanly writes the pre-loaded screen
nav_js_clean = """<script>
    function navigateToScreen(targetScreen) {
        try {
            if (window.ALL_SCREENS_HTML && window.ALL_SCREENS_HTML[targetScreen]) {
                document.open();
                document.write(window.ALL_SCREENS_HTML[targetScreen]);
                document.close();
                return;
            }
        } catch(e) {}

        // Fallback if not preloaded
        try { window.location.href = targetScreen; } catch(e) {}
    }
"""

def inject_clean_nav(html_str):
    if 'function navigateToScreen(' in html_str:
        return re.sub(r'function navigateToScreen\(.*?\}\n\s*\}', nav_js_clean.replace('<script>', '').strip(), html_str, flags=re.DOTALL)
    else:
        return html_str.replace('<script>', nav_js_clean, 1)

h_dash_clean = inject_clean_nav(h_dash_clean)
h_fc_clean = inject_clean_nav(h_fc_clean)
h_cvrp_clean = inject_clean_nav(h_cvrp_clean)

# Create the master ALL_SCREENS_HTML script
all_screens_dict = {
    "dashboard_preview.html": h_dash_clean,
    "demand_forecaster.html": h_fc_clean,
    "cvrp_explorer.html": h_cvrp_clean,
    "index.html": h_dash_clean
}
all_screens_js = f'<script>window.ALL_SCREENS_HTML = {json.dumps(all_screens_dict)};</script>'

# Inject ALL_SCREENS_HTML into <head> of each file so any page loaded directly can switch to any other page instantly!
h_dash_final = h_dash_clean.replace('<head>', '<head>\n' + all_screens_js, 1)
h_fc_final = h_fc_clean.replace('<head>', '<head>\n' + all_screens_js, 1)
h_cvrp_final = h_cvrp_clean.replace('<head>', '<head>\n' + all_screens_js, 1)

# Save back to individual files
with open('dashboard_preview.html', 'w', encoding='utf-8') as f:
    f.write(h_dash_final)
with open('demand_forecaster.html', 'w', encoding='utf-8') as f:
    f.write(h_fc_final)
with open('cvrp_explorer.html', 'w', encoding='utf-8') as f:
    f.write(h_cvrp_final)

# NOW: Replace index.html completely!
# Instead of index.html having a <header> and <iframe src="dashboard_preview.html"> (which causes "one website inside another"),
# index.html IS direct, single-page dashboard_preview.html with ALL 3 screens embedded inside ALL_SCREENS_HTML!
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(h_dash_final)

print("SUCCESS: index.html is now a pure Single-Page Application without any double header or iframe wrapper!")

# NOW: Update app.py so Streamlit renders edge-to-edge cleanly without duplicate radio selectors clashing with the sidebar!
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Let's check how tab_mockup is structured in app.py and ensure it renders cleanly
mockup_block_pattern = r'with tab_mockup:.*?(?=\n# ---------------------------------------------------------|\Z)'
match = re.search(mockup_block_pattern, app_code, flags=re.DOTALL)
if match:
    new_mockup_block = """with tab_mockup:
    st.markdown("### ⚓ Maersk AI Logistics Enterprise Command Center")
    st.write("Full-screen, ultra-low latency **Single-Page Operations Research & ML Platform** (`#000F1C` obsidian navy + `#00E5FF` electric cyan). Use the left navigation bar (`Network Topology`, `Demand Forecaster`, `CVRP Dispatcher`, `+ New Optimization`) to switch views instantly.")
    
    # Load the pure Single-Page Application (index.html) populated with live data
    with open("dashboard_preview.html", "r", encoding="utf-8") as f:
        h_dash_live = ui_engine.populate_network_topology(f.read(), st.session_state.get("opt_results"), warehouses_df, active_customers_df)
    with open("demand_forecaster.html", "r", encoding="utf-8") as f:
        h_fc_live = ui_engine.populate_demand_forecaster(f.read(), st.session_state.get("live_fc_metrics"), st.session_state.get("forecast_df"))
    with open("cvrp_explorer.html", "r", encoding="utf-8") as f:
        h_cvrp_live = ui_engine.populate_cvrp_explorer(f.read(), st.session_state.get("cvrp_live_res"), st.session_state.get("live_dep", "Port of Rotterdam"))
        
    live_screens_dict = {
        "dashboard_preview.html": h_dash_live,
        "demand_forecaster.html": h_fc_live,
        "cvrp_explorer.html": h_cvrp_live,
        "index.html": h_dash_live
    }
    live_screens_js = f'<script>window.ALL_SCREENS_HTML = {json.dumps(live_screens_dict)};</script>'
    
    # Render with clean height and no double radio headers
    final_spa_code = re.sub(r'<script>window\.ALL_SCREENS_HTML = \{.*?\};</script>', '', h_dash_live, flags=re.DOTALL)
    final_spa_code = final_spa_code.replace('<head>', '<head>\n' + live_screens_js, 1)
    
    components.html(final_spa_code, height=980, scrolling=False)
"""
    app_code = app_code[:match.start()] + new_mockup_block + app_code[match.end():]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("SUCCESS: app.py tab_mockup updated to clean, borderless Single-Page Application without double headers or iframe inception!")
else:
    print("WARNING: tab_mockup block pattern not found in app.py")
