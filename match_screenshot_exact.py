import re
import os
import json

# Master Top Bar exact as shown in Screenshot 2026-07-13 120611.png
TOP_BAR_HTML = """<header class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-lg py-sm bg-[#000F1C]/90 backdrop-blur-md border-b border-outline-variant/20 shadow-md">
    <div class="flex items-center gap-md">
        <div class="font-headline-md text-primary-fixed font-bold tracking-tighter leading-tight flex items-center gap-2">
            <span class="text-3xl">⚓</span>
            <div>
                <div class="text-lg leading-tight text-glow-cyan">AI Logistics Network</div>
                <div class="text-lg leading-tight text-glow-cyan">Optimizer</div>
            </div>
        </div>
        <nav class="hidden md:flex ml-xl gap-lg items-center text-sm">
            <a class="text-on-surface-variant hover:text-primary-fixed transition-all" href="#">Maersk Enterprise Hub</a>
            <a class="text-primary-fixed-dim font-bold border-b-2 border-primary-fixed-dim pb-1 transition-all" href="#">🟢 MILP &amp; CVRP Solvers Online</a>
        </nav>
    </div>
    <div class="flex items-center gap-md">
        <button onclick="openNewOptimizationModal(); return false;" class="bg-[#00E5FF] text-[#001A2C] px-6 py-2.5 font-extrabold rounded-lg hover:brightness-110 transition-all shadow-[0_0_20px_rgba(0,229,255,0.5)] tracking-wide uppercase text-xs flex items-center gap-1.5">
            <span class="material-symbols-outlined text-sm">bolt</span> Run Optimization Engine
        </button>
    </div>
</header>"""

def build_aside(active_id="topology"):
    items = [
        ("topology", "hub", "Network Topology", "dashboard_preview.html"),
        ("forecaster", "trending_up", "Demand Forecaster", "demand_forecaster.html"),
        ("cvrp", "local_shipping", "CVRP Dispatcher", "cvrp_explorer.html"),
        ("cost", "analytics", "Cost Analytics", "dashboard_preview.html"),
        ("audit", "history", "Audit Logs", "dashboard_preview.html")
    ]
    
    links_html = ""
    for item_id, icon, label, target_file in items:
        if item_id == active_id:
            cls = "flex items-center px-md py-sm gap-sm text-primary-fixed-dim border-r-2 border-primary-fixed-dim bg-primary-container/10 hover:bg-primary-container/5 transition-all cursor-pointer font-bold"
            fill = "1"
        else:
            cls = "flex items-center px-md py-sm gap-sm text-on-surface-variant hover:bg-primary-container/5 hover:text-primary-fixed transition-all cursor-pointer"
            fill = "0"
            
        links_html += f"""
            <a onclick="switchMainScreen('{target_file}', '{item_id}'); return false;" class="{cls}" href="#">
                <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' {fill};">{icon}</span>
                <span class="font-body-md text-body-md">{label}</span>
            </a>"""

    aside_html = f"""<aside class="fixed left-0 top-0 h-full w-64 bg-[#000F1C]/95 backdrop-blur-xl border-r border-outline-variant/20 shadow-lg flex flex-col pt-20 transition-all duration-200 z-40">
    <div class="px-md py-sm border-b border-outline-variant/10">
        <div class="flex items-center gap-xs">
            <div class="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center border border-primary-fixed-dim shadow-[0_0_10px_rgba(0,229,255,0.3)]">
                <span class="material-symbols-outlined text-primary-fixed-dim">analytics</span>
            </div>
            <div>
                <p class="font-mono-kpi text-mono-kpi text-primary-fixed-dim leading-none font-bold">Command Center</p>
                <p class="text-[10px] text-on-surface-variant uppercase tracking-widest mt-1">Precision Logistics</p>
            </div>
        </div>
        <button onclick="openNewOptimizationModal(); return false;" class="w-full bg-primary-container/10 border border-primary-container/30 text-primary-fixed-dim py-xs rounded flex items-center justify-center gap-xs hover:bg-primary-container/20 transition-all mt-md shadow-[0_0_12px_rgba(0,229,255,0.15)] font-bold text-xs">
            <span class="material-symbols-outlined text-sm">add</span>New Optimization
        </button>
    </div>
    <nav class="flex-1 mt-md space-y-1">
        {links_html}
    </nav>
    <div class="p-md mt-auto border-t border-outline-variant/10 text-xs text-on-surface-variant">
        <div class="flex items-center gap-2 mb-1">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span class="text-emerald-400 font-bold">SCIP &amp; XGBoost Active</span>
        </div>
        <p class="opacity-70">Maersk Enterprise v2.0</p>
    </div>
</aside>\n"""
    return aside_html

def update_page(filename, active_id):
    if not os.path.exists(filename): return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace header exactly
    if '<header' in content and '</header>' in content:
        idx1 = content.find('<header')
        idx2 = content.find('</header>') + 9
        content = content[:idx1] + TOP_BAR_HTML + content[idx2:]
    
    # Replace aside exactly (from <aside up to <main or first occurrence after <aside if </aside> is present)
    if '<aside' in content:
        idx1 = content.find('<aside')
        if '</aside>' in content[idx1:]:
            idx2 = content.find('</aside>', idx1) + 8
        elif '<main' in content[idx1:]:
            idx2 = content.find('<main', idx1)
        else:
            idx2 = content.find('<!-- Additional Context Card -->', idx1)
            if idx2 == -1: idx2 = idx1 + 2500
        content = content[:idx1] + build_aside(active_id) + content[idx2:]

    # Ensure map buttons work
    content = re.sub(
        r'<button[^>]*>\s*MILP Hub Allocation\s*</button>',
        '<button id="btn-map-milp" onclick="switchMapMode(\'milp\'); return false;" class="bg-primary-container/20 text-primary-fixed-dim text-xs px-xs py-1 rounded border border-primary-fixed-dim/40 font-bold transition-all shadow-[0_0_8px_rgba(0,229,255,0.3)]">MILP Hub Allocation</button>',
        content, flags=re.IGNORECASE
    )
    content = re.sub(
        r'<button[^>]*>\s*CVRP Multi-Stop\s*</button>',
        '<button id="btn-map-cvrp" onclick="switchMapMode(\'cvrp\'); return false;" class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant transition-all">CVRP Multi-Stop</button>',
        content, flags=re.IGNORECASE
    )
    content = re.sub(
        r'<button[^>]*>\s*Demand Heatmap\s*</button>',
        '<button id="btn-map-heat" onclick="switchMapMode(\'heat\'); return false;" class="bg-surface-variant/40 hover:bg-surface-variant/60 text-xs px-xs py-1 rounded border border-outline-variant/30 text-on-surface-variant transition-all">Demand Heatmap</button>',
        content, flags=re.IGNORECASE
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: {filename} updated to match Screenshot exactly (active tab: {active_id}).")

update_page("dashboard_preview.html", "topology")
update_page("demand_forecaster.html", "forecaster")
update_page("cvrp_explorer.html", "cvrp")

# Also update index.html to match dashboard_preview.html exactly
with open("dashboard_preview.html", "r", encoding="utf-8") as f:
    dash_h = f.read()

def strip_scripts(s):
    return re.sub(r'<script[^>]*>.*?</script>\s*', '', s, flags=re.DOTALL | re.IGNORECASE)

clean_screens_map = {
    "dashboard_preview.html": strip_scripts(dash_h),
    "demand_forecaster.html": strip_scripts(open("demand_forecaster.html", encoding="utf-8").read()),
    "cvrp_explorer.html": strip_scripts(open("cvrp_explorer.html", encoding="utf-8").read()),
    "index.html": strip_scripts(dash_h)
}
json_dump_escaped = json.dumps(clean_screens_map).replace('</script>', '<\\/script>')
clean_js = f'<script>window.ALL_SCREENS_HTML = {json_dump_escaped};</script>'
index_content = dash_h.replace('<head>', '<head>\n    ' + clean_js, 1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)
print("SUCCESS: index.html updated as master matching exact screenshot top bar and sidebar.")
