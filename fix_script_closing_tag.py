import os
import re
import json

# Read clean HTML templates
with open("dashboard_preview.html", "r", encoding="utf-8") as f:
    h_dash = f.read()
with open("demand_forecaster.html", "r", encoding="utf-8") as f:
    h_fc = f.read()
with open("cvrp_explorer.html", "r", encoding="utf-8") as f:
    h_cvrp = f.read()

# Strip out any existing ALL_SCREENS_HTML from them so they are pristine
def strip_all_screens(s):
    s = re.sub(r'<script>window\.ALL_SCREENS_HTML = \{.*?\};</script>\s*', '', s, flags=re.DOTALL)
    s = re.sub(r'window\.ALL_SCREENS_HTML = \{.*?\};\s*', '', s, flags=re.DOTALL)
    return s

h_dash = strip_all_screens(h_dash)
h_fc = strip_all_screens(h_fc)
h_cvrp = strip_all_screens(h_cvrp)

# Save the pristine un-nested files back out
with open("dashboard_preview.html", "w", encoding="utf-8") as f:
    f.write(h_dash)
with open("demand_forecaster.html", "w", encoding="utf-8") as f:
    f.write(h_fc)
with open("cvrp_explorer.html", "w", encoding="utf-8") as f:
    f.write(h_cvrp)

clean_screens_map = {
    "dashboard_preview.html": h_dash,
    "demand_forecaster.html": h_fc,
    "cvrp_explorer.html": h_cvrp,
    "index.html": h_dash
}

# CRITICAL FIX: Escape </script> as <\/script> so HTML parser never closes the <script> tag early!
json_dump_str = json.dumps(clean_screens_map).replace('</script>', '<\\/script>')
clean_js = f'<script>window.ALL_SCREENS_HTML = {json_dump_str};</script>'

# Build index.html
index_content = h_dash.replace('<head>', '<head>\n    ' + clean_js, 1)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)

print("SUCCESS: index.html generated with properly escaped <\\/script> tags inside ALL_SCREENS_HTML string!")

# Now update app.py so it applies the exact same .replace('</script>', '<\\/script>') escape when building live_screens_js!
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

mockup_block_pattern = r'with tab_mockup:.*?(?=\n# ---------------------------------------------------------|\Z)'
match = re.search(mockup_block_pattern, app_code, flags=re.DOTALL)
if match:
    new_mockup_block = """with tab_mockup:
    st.markdown("### ⚓ Maersk AI Logistics Enterprise Command Center")
    st.write("Full-screen, ultra-low latency **Single-Page Operations Research & ML Platform** (`#000F1C` obsidian navy + `#00E5FF` electric cyan). Use the left navigation bar (`Network Topology`, `Demand Forecaster`, `CVRP Dispatcher`, `+ New Optimization`) to switch views instantly.")
    
    # Load and populate clean templates
    with open("dashboard_preview.html", "r", encoding="utf-8") as f:
        h_dash_live = ui_engine.populate_network_topology(f.read(), st.session_state.get("opt_results"), warehouses_df, active_customers_df)
    with open("demand_forecaster.html", "r", encoding="utf-8") as f:
        h_fc_live = ui_engine.populate_demand_forecaster(f.read(), st.session_state.get("live_fc_metrics"), st.session_state.get("forecast_df"))
    with open("cvrp_explorer.html", "r", encoding="utf-8") as f:
        h_cvrp_live = ui_engine.populate_cvrp_explorer(f.read(), st.session_state.get("cvrp_live_res"), st.session_state.get("live_dep", "Port of Rotterdam"))
        
    # Strip any prior window.ALL_SCREENS_HTML so we don't nest strings
    def strip_all_screens(s):
        s = re.sub(r'<script>window\.ALL_SCREENS_HTML = \{.*?\};</script>', '', s, flags=re.DOTALL)
        return re.sub(r'window\.ALL_SCREENS_HTML = \{.*?\};', '', s, flags=re.DOTALL)
        
    h_dash_clean = strip_all_screens(h_dash_live)
    h_fc_clean = strip_all_screens(h_fc_live)
    h_cvrp_clean = strip_all_screens(h_cvrp_live)
    
    live_screens_dict = {
        "dashboard_preview.html": h_dash_clean,
        "demand_forecaster.html": h_fc_clean,
        "cvrp_explorer.html": h_cvrp_clean,
        "index.html": h_dash_clean
    }
    # CRITICAL FIX: Escape </script> as <\/script> so HTML parser never closes the <script> tag early!
    json_dump_escaped = json.dumps(live_screens_dict).replace('</script>', '<\\\\/script>')
    live_screens_js = '<script>window.ALL_SCREENS_HTML = ' + json_dump_escaped + ';</script>'
    
    final_spa_code = h_dash_clean.replace('<head>', '<head>' + live_screens_js, 1)
    
    components.html(final_spa_code, height=980, scrolling=False)
"""
    app_code = app_code[:match.start()] + new_mockup_block + app_code[match.end():]
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_code)
    print("SUCCESS: app.py updated with <\\/script> escaping to eliminate all raw text dumping in HTML!")
