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
        <a class="{dash_style}" href="dashboard_preview.html">
            <span class="material-symbols-outlined" {fill_dash}>hub</span>
            <span>Network Topology</span>
        </a>
        <a class="{fc_style}" href="demand_forecaster.html">
            <span class="material-symbols-outlined" {fill_fc}>trending_up</span>
            <span>Demand Forecaster</span>
        </a>
        <a class="{cvrp_style}" href="cvrp_explorer.html">
            <span class="material-symbols-outlined" {fill_cvrp}>local_shipping</span>
            <span>CVRP Dispatcher</span>
        </a>
        <a class="{style_inactive}" onclick="showToast('Cost Spend Analytics', 'Inspecting time-series spend variance across regional corridors ($1.42M vs $1.10M baseline).')">
            <span class="material-symbols-outlined">analytics</span>
            <span>Cost Analytics</span>
        </a>
        <a class="{style_inactive}" onclick="showToast('Audit Log Verified', '120 historical monthly demand tuples synced from 3NF SQLite database.')">
            <span class="material-symbols-outlined">history</span>
            <span>Audit Logs</span>
        </a>
    </nav>
    <div class="p-6 border-t border-[#00E5FF]/10 space-y-2">
        <a class="flex items-center py-2 gap-3 text-gray-400 hover:text-[#00E5FF] text-sm transition-all cursor-pointer" onclick="showToast('Global Solver Settings', 'SCIP/CBC Integer linear solver active. Gap tolerance: 0.01%')">
            <span class="material-symbols-outlined text-sm">settings</span>
            <span>Settings</span>
        </a>
        <a class="flex items-center py-2 gap-3 text-gray-400 hover:text-[#00E5FF] text-sm transition-all cursor-pointer" onclick="showToast('AI Support Online', 'Ensemble ML engine monitoring 36 global freight corridors 24/7.')">
            <span class="material-symbols-outlined text-sm">help</span>
            <span>Support</span>
        </a>
    </div>
</aside>"""
    return sidebar

modal_html = """
<!-- Interactive New Optimization Setup Modal -->
<div id="new-opt-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center opacity-0 pointer-events-none transition-all duration-300">
    <div class="glass-panel bg-[#001A2C]/95 border-2 border-[#00E5FF] shadow-[0_0_50px_rgba(0,229,255,0.4)] rounded-2xl p-8 max-w-lg w-full mx-4 transform scale-95 transition-all duration-300">
        <div class="flex justify-between items-center pb-4 border-b border-[#00E5FF]/30 mb-6">
            <div class="flex items-center gap-3">
                <span class="p-2 bg-[#00E5FF]/20 rounded-lg text-[#00E5FF] material-symbols-outlined text-2xl">bolt</span>
                <div>
                    <h3 class="font-bold text-lg text-[#00E5FF] font-headline-md tracking-tight">Launch New Optimization</h3>
                    <p class="text-xs text-gray-300 font-mono-label">Configure custom Operations Research & ML job</p>
                </div>
            </div>
            <button onclick="closeNewOptimizationModal()" class="text-gray-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10">
                <span class="material-symbols-outlined">close</span>
            </button>
        </div>
        
        <div class="space-y-5">
            <div>
                <label class="block text-xs font-mono-label uppercase text-gray-300 font-bold mb-2">1. Optimization Engine Domain</label>
                <select id="modal-engine-select" class="w-full bg-[#000F1C] border border-[#00E5FF]/40 rounded-lg py-2.5 px-3 text-sm text-[#00E5FF] font-semibold focus:border-[#00E5FF] focus:ring-1 focus:ring-[#00E5FF]">
                    <option value="milp">SCIP Hub Location & Intermodal Allocation (MILP)</option>
                    <option value="xgb">XGBoost Multi-Horizon Regional Demand Forecast</option>
                    <option value="cvrp">OR-Tools Guided Local Search Fleet Dispatch (CVRP)</option>
                </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-mono-label uppercase text-gray-300 font-bold mb-2">Origin Hub / Depot</label>
                    <select id="modal-depot-select" class="w-full bg-[#000F1C] border border-[#00E5FF]/40 rounded-lg py-2 px-3 text-xs text-white">
                        <option>Rotterdam Hub (TEU-2600)</option>
                        <option>Hamburg Port Cluster</option>
                        <option>Antwerp Inland Hub</option>
                        <option>Amsterdam North Depot</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-mono-label uppercase text-gray-300 font-bold mb-2">Fleet / Capacity Target</label>
                    <input id="modal-cap-input" type="number" value="450" class="w-full bg-[#000F1C] border border-[#00E5FF]/40 rounded-lg py-2 px-3 text-xs text-[#00E5FF] font-bold" />
                </div>
            </div>

            <div>
                <label class="block text-xs font-mono-label uppercase text-gray-300 font-bold mb-2">Objective Priority Function</label>
                <div class="grid grid-cols-1 gap-2 text-xs">
                    <label class="flex items-center gap-2 p-2.5 rounded-lg border border-[#00E5FF]/30 bg-[#00E5FF]/10 text-white cursor-pointer">
                        <input type="radio" name="opt_obj" checked class="text-[#00E5FF] focus:ring-0 bg-[#000F1C] border-[#00E5FF]" />
                        <span>Minimize Total Freight Tariff & Spot Rate Costs</span>
                    </label>
                    <label class="flex items-center gap-2 p-2.5 rounded-lg border border-gray-700 bg-black/20 text-gray-300 cursor-pointer">
                        <input type="radio" name="opt_obj" class="text-[#00E5FF] focus:ring-0 bg-[#000F1C] border-gray-600" />
                        <span>Maximize Fleet Fill Factor & Load Balancing (>95%)</span>
                    </label>
                </div>
            </div>
        </div>

        <div class="mt-8 pt-4 border-t border-[#00E5FF]/20 flex justify-end gap-3">
            <button onclick="closeNewOptimizationModal()" class="px-5 py-2.5 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 transition-all font-semibold text-xs uppercase">Cancel</button>
            <button onclick="executeNewOptimizationRun()" id="btn-modal-execute" class="px-6 py-2.5 rounded-lg bg-gradient-to-r from-[#00E5FF] to-[#3491ff] text-[#001A2C] font-bold hover:scale-105 active:scale-95 transition-all shadow-[0_0_20px_rgba(0,229,255,0.6)] text-xs uppercase tracking-wider flex items-center gap-2">
                <span class="material-symbols-outlined text-sm">bolt</span> Execute Custom Solver →
            </button>
        </div>
    </div>
</div>
"""

modal_js = """<script>
    function openNewOptimizationModal() {
        const modal = document.getElementById('new-opt-modal');
        if (modal) {
            modal.classList.remove('opacity-0', 'pointer-events-none');
            const inner = modal.querySelector('.max-w-lg');
            if (inner) inner.classList.remove('scale-95');
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
                showToast('SCIP MILP Converged', 'Custom network hub allocation solved in 14.8ms. Freight cost: $1,098,400 | Savings: 68.2%');
            } else if (eng === 'xgb') {
                showToast('XGBoost Multi-Horizon Retrained', 'Custom 30-day forecast generated across Rotterdam Hub cluster (`R² = 0.982`).');
            } else {
                showToast('OR-Tools GLS Dispatched', 'Custom multi-stop loops scheduled for Rotterdam Depot across 16 active EV trucks.');
            }
        }, 800);
    }
"""

for fn in ['dashboard_preview.html', 'demand_forecaster.html', 'cvrp_explorer.html']:
    with open(fn, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. Replace existing <aside ...> ... </aside> with unified sidebar
    html = re.sub(r'<aside.*?</aside>', create_unified_sidebar(fn), html, flags=re.DOTALL)
    
    # 2. Inject modal right before </body> if not already there
    if 'id="new-opt-modal"' not in html:
        html = re.sub(r'(</body>)', modal_html + r'\n\1', html, flags=re.IGNORECASE)
    
    # 3. Inject modal JS right after <script> or update existing functions
    if 'function openNewOptimizationModal()' not in html:
        html = html.replace('<script>', modal_js, 1)
        
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully unified sidebar & added New Optimization modal to {fn}!")
