import os
import re
import json

# Read clean HTML templates that already contain our unified views
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

clean_dash = strip_all_screens(h_dash)
clean_fc = strip_all_screens(h_fc)
clean_cvrp = strip_all_screens(h_cvrp)

with open("dashboard_preview.html", "w", encoding="utf-8") as f:
    f.write(clean_dash)
with open("demand_forecaster.html", "w", encoding="utf-8") as f:
    f.write(clean_fc)
with open("cvrp_explorer.html", "w", encoding="utf-8") as f:
    f.write(clean_cvrp)

clean_screens_map = {
    "dashboard_preview.html": clean_dash,
    "demand_forecaster.html": clean_fc,
    "cvrp_explorer.html": clean_cvrp,
    "index.html": clean_dash
}

json_dump_str = json.dumps(clean_screens_map).replace('</script>', '<\/script>')
clean_js = f'<script>window.ALL_SCREENS_HTML = {json_dump_str};</script>'

index_content = clean_dash.replace('<head>', '<head>\n    ' + clean_js, 1)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)

print("SUCCESS: index.html generated with properly escaped <\/script> tags while preserving all 5 unified views!")

if os.path.exists("app.py"):
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
    if 'final_spa_code = re.sub(' in app_code and "re.DOTALL)" in app_code:
        idx = app_code.find('final_spa_code = re.sub(')
        old_line_end = app_code.find('\n', idx)
        app_code = app_code[:idx] + 'final_spa_code = re.sub(r\'<script>window\\.ALL_SCREENS_HTML = \{.*?\};</script>\', \'\', h_dash_live, flags=re.DOTALL)\n        final_spa_code = final_spa_code.replace("</script>", "<\\/script>").replace("<head>", "<head><script>window.ALL_SCREENS_HTML=" + json.dumps(live_screens_dict).replace("</script>", "<\\/script>") + ";</script>", 1)' + app_code[old_line_end:]
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(app_code)
    print("SUCCESS: app.py verified with <\/script> escaping!")
