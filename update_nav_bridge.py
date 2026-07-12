import re

nav_js = """<script>
    function navigateToScreen(targetScreen) {
        // 1. Check if we are inside index.html iframe master portal
        try {
            if (window.parent && window.parent.switchTab && typeof window.parent.switchTab === 'function') {
                window.parent.switchTab(targetScreen);
                return;
            }
        } catch(e) {}

        // 2. Check if we are inside Streamlit app.py iframe!
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
        } catch (e) {
            console.log('Streamlit iframe sandbox check:', e);
        }

        // 3. Fallback: If inside an iframe where parent DOM access is restricted or directly in browser,
        // dynamically fetch and render the target screen inside the current document!
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
                try {
                    window.location.href = targetScreen;
                } catch(e) {}
            });
    }
"""

for fn in ['dashboard_preview.html', 'demand_forecaster.html', 'cvrp_explorer.html']:
    with open(fn, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = re.sub(r'function navigateToScreen\(.*?\}\n\s*\}', nav_js.replace('<script>', '').strip(), html, flags=re.DOTALL)
    
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated robust navigateToScreen in {fn}!")
