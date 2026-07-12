import re

def create_unified_sidebar(active_page):
    style_active = 'flex items-center px-6 py-3 gap-3 text-[#00E5FF] border-r-4 border-[#00E5FF] bg-[#00E5FF]/10 hover:bg-[#00E5FF]/15 transition-all font-bold text-sm cursor-pointer'
    style_inactive = 'flex items-center px-6 py-3 gap-3 text-gray-300 hover:bg-[#00E5FF]/5 hover:text-[#00E5FF] transition-all font-medium text-sm cursor-pointer'
    
    dash_style = style_active if active_page == 'dashboard_preview.html' else style_inactive
    fc_style = style_active if active_page == 'demand_forecaster.html' else style_inactive
    cvrp_style = style_active if active_page == 'cvrp_explorer.html' else style_inactive
    
    fill_dash = 'style="font-variation-settings: \'FILL\' 1;"' if active_page == 'dashboard_preview.html' else ''
    fill_fc = 'style="font-variation-settings: \'FILL\' 1;"' if active_page == 'demand_forecaster.html' else ''
    fill_cvrp = 'style="font-variation-settings: \'FILL\' 1;"' if active_page == 'cvrp_explorer.html' else ''
    
    sidebar = f"""<aside class="fixed left-0 top-0 h-full w-64 bg-[#001424]/85 backdrop-blur-xl border-r border-[#00E5FF]/20 shadow-2xl flex flex-col pt-20 transition-all duration-200 z-40">
    <div class="px-6 mb-6">
        <div class="flex items-center gap-3 mb-4">
            <div class="w-11 h-11 rounded-full border border-[#00E5FF] overflow-hidden shadow-[0_0_15px_rgba(0,229,255,0.3)] bg-[#00243D]">
                <img class="w-full h-full object-cover" data-alt="Logistics Director Portrait" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDTpHqSHrzndrG9qILFlGIm8P8w17DEa5ZRikg4JAbw8RFdOOR8kXrz0TjeT8492tnmaJhHTO87ThJcqiBwGYGUvgr0l-J8FwccWaw7X_O-DQC8PCbyP8dSwz2f00-pf_2v7ZdCOyjlVIpwnyJI7X-zYZ1WvB1_wQRYtJdx18DXOsY7Cp5hRgj_qpVxb9JWiYa9zssir75Kwx3zwGqZjoSaMAZ7pnxyxRwezmjyvqP_NMx5fSKmdixn"/>
            </div>
            <div>
                <p class="font-mono-kpi text-[#00E5FF] font-bold text-base leading-tight">Command Center</p>
                <p class="text-xs text-gray-400 tracking-wider">Precision Logistics</p>
            </div>
        </div>
        <button onclick="openNewOptimizationModal()" class="w-full bg-gradient-to-r from-[#00E5FF]/20 to-[#3491ff]/20 border border-[#00E5FF]/50 text-[#00E5FF] py-2.5 px-3 rounded-lg flex items-center justify-center gap-2 hover:bg-[#00E5FF]/30 active:scale-95 transition-all shadow-[0_0_15px_rgba(0,229,255,0.2)] font-bold text-sm tracking-wide group">
            <span class="material-symbols-outlined text-base group-hover:rotate-90 transition-transform">add</span>
            <span>New Optimization</span>
        </button>
    </div>
    <nav class="flex-grow space-y-1">
        <a class="{dash_style}" onclick="navigateToScreen('dashboard_preview.html'); return false;" href="dashboard_preview.html">
            <span class="material-symbols-outlined" {fill_dash}>hub</span>
            <span>Network Topology</span>
        </a>
        <a class="{fc_style}" onclick="navigateToScreen('demand_forecaster.html'); return false;" href="demand_forecaster.html">
            <span class="material-symbols-outlined" {fill_fc}>trending_up</span>
            <span>Demand Forecaster</span>
        </a>
        <a class="{cvrp_style}" onclick="navigateToScreen('cvrp_explorer.html'); return false;" href="cvrp_explorer.html">
            <span class="material-symbols-outlined" {fill_cvrp}>local_shipping</span>
            <span>CVRP Dispatcher</span>
        </a>
        <a class="{style_inactive}" onclick="showToast('Cost Spend Analytics', 'Inspecting time-series spend variance across regional corridors ($1.42M vs $1.10M baseline).'); return false;" href="#">
            <span class="material-symbols-outlined">analytics</span>
            <span>Cost Analytics</span>
        </a>
        <a class="{style_inactive}" onclick="showToast('Audit Log Verified', '120 historical monthly demand tuples synced from 3NF SQLite database.'); return false;" href="#">
            <span class="material-symbols-outlined">history</span>
            <span>Audit Logs</span>
        </a>
    </nav>
    <div class="p-6 border-t border-[#00E5FF]/10 space-y-2">
        <a class="flex items-center py-2 gap-3 text-gray-400 hover:text-[#00E5FF] text-sm transition-all cursor-pointer" onclick="showToast('Global Solver Settings', 'SCIP/CBC Integer linear solver active. Gap tolerance: 0.01%'); return false;">
            <span class="material-symbols-outlined text-sm">settings</span>
            <span>Settings</span>
        </a>
        <a class="flex items-center py-2 gap-3 text-gray-400 hover:text-[#00E5FF] text-sm transition-all cursor-pointer" onclick="showToast('AI Support Online', 'Ensemble ML engine monitoring 36 global freight corridors 24/7.'); return false;">
            <span class="material-symbols-message text-sm">help</span>
            <span>Support</span>
        </a>
    </div>
</aside>"""
    return sidebar

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
        // Streamlit parent window has radio buttons above the iframe with labels like '🌐 Network Topology & Allocation Hub'
        try {
            if (window.parent && window.parent.document) {
                const labels = window.parent.document.querySelectorAll('div[role="radiogroup"] label, label[data-baseweb="radio"], p');
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

        // 3. Fallback to direct window location navigation if opened directly via double click
        try {
            window.location.href = targetScreen;
        } catch(e) {}
    }
"""

for fn in ['dashboard_preview.html', 'demand_forecaster.html', 'cvrp_explorer.html']:
    with open(fn, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace existing sidebar
    html = re.sub(r'<aside.*?</aside>', create_unified_sidebar(fn), html, flags=re.DOTALL)
    
    # Inject or update navigateToScreen function
    if 'function navigateToScreen(' not in html:
        html = html.replace('<script>', nav_js, 1)
    else:
        html = re.sub(r'function navigateToScreen\(.*?\}\n\s*\}', nav_js.replace('<script>', '').strip(), html, flags=re.DOTALL)
        
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully injected navigation bridge across {fn}!")
