import re

def refine_chart_to_solid_curve_and_scanning_dot_only(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Make the AI Predicted Line a clean, solid, glowing electric cyan curve (remove stroke-dasharray="6,6")
    content = re.sub(
        r'<path class="predicted-line[^"]*"[^>]*>',
        '<path class="predicted-line filter drop-shadow-[0_0_12px_rgba(0,229,255,0.9)]" d="M 500,170 L 550,150 L 600,190 L 650,120 L 700,160 L 750,110 L 800,130 L 850,70 L 900,100 L 950,50" fill="none" stroke="#00e5ff" stroke-linecap="round" stroke-width="3.5"></path>',
        content
    )

    # 2. Make the 10 static predicted-dot circles transparent (opacity="0" or r="0") so they don't clutter the colored graph,
    # while leaving data-base-cy intact for updateRealisticForecastCurve coordinate calculations!
    content = re.sub(
        r'<circle class="predicted-dot"([^>]*)>',
        r'<circle class="predicted-dot"\1 opacity="0" pointer-events="none">',
        content
    )
    # Ensure any double opacity="0" is cleaned up
    content = content.replace('opacity="0" pointer-events="none" opacity="0" pointer-events="none"', 'opacity="0" pointer-events="none"')

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: {filename} chart updated: solid glowing cyan wave + single scanning dot on dotted line.")

refine_chart_to_solid_curve_and_scanning_dot_only("demand_forecaster.html")

# Also update index.html master map so Streamlit Tab 0 renders this exact clean chart
with open("dashboard_preview.html", "r", encoding="utf-8") as f:
    dash_h = f.read()
with open("demand_forecaster.html", "r", encoding="utf-8") as f:
    fc_h = f.read()
with open("cvrp_explorer.html", "r", encoding="utf-8") as f:
    cvrp_h = f.read()

import json
def strip_scripts(s):
    return re.sub(r'<script[^>]*>.*?</script>\s*', '', s, flags=re.DOTALL | re.IGNORECASE)

clean_screens_map = {
    "dashboard_preview.html": strip_scripts(dash_h),
    "demand_forecaster.html": strip_scripts(fc_h),
    "cvrp_explorer.html": strip_scripts(cvrp_h),
    "index.html": strip_scripts(dash_h)
}
json_dump_escaped = json.dumps(clean_screens_map).replace('</script>', '<\\/script>')
clean_js = f'<script>window.ALL_SCREENS_HTML = {json_dump_escaped};</script>'
index_content = dash_h.replace('<head>', '<head>\n    ' + clean_js, 1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)
print("SUCCESS: index.html updated.")
