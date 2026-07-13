import os
import re
import json

def enable_table_scrolling(filename):
    if not os.path.exists(filename):
        return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update table wrapper div to be max-h-[420px] overflow-y-auto custom-scrollbar
    content = content.replace(
        '<div class="p-md overflow-x-auto">',
        '<div class="p-md overflow-x-auto overflow-y-auto max-h-[420px] custom-scrollbar border-t border-outline-variant/10 relative">'
    )

    # 2. Make table headers sticky so when user scrolls down the table, headers stay pinned at top
    # We match <thead><tr> or <thead class="..."><tr> and update the tr/th classes
    content = re.sub(
        r'<tr class="text-\[11px\] uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20">',
        '<tr class="text-[11px] uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 sticky top-0 bg-[#080f11]/95 backdrop-blur-md z-20 shadow-sm">',
        content
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

for fn in ["dashboard_preview.html", "demand_forecaster.html", "cvrp_explorer.html"]:
    enable_table_scrolling(fn)

print("SUCCESS: Updated dashboard_preview.html, demand_forecaster.html, and cvrp_explorer.html with max-h-[420px] overflow-y-auto and sticky headers!")

# Regenerate index.html
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

print("SUCCESS: Regenerated index.html with scrollable table container and sticky headers!")

# Update app.py to set height=1150, scrolling=True on components.html so outer Streamlit iframe never clips
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

app_code = re.sub(
    r'components\.html\(final_spa_code,\s*height=\d+,\s*scrolling=False\)',
    'components.html(final_spa_code, height=1150, scrolling=True)',
    app_code
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("SUCCESS: app.py updated with height=1150 and scrolling=True on components.html!")
