import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import os
import json
import re
import database
import optimizer
import forecaster
import visualization
import vrp_solver
import ui_engine

# Set Streamlit page configuration
st.set_page_config(
    page_title="AI-Based Logistics Network Optimizer | Maersk Enterprise",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Maersk-Inspired Corporate CSS (Dark Navy #000F1C + Vibrant Cyan #00E5FF)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    /* Main Background and Text */
    .stApp {
        background: linear-gradient(135deg, #000F1C 0%, #001A2C 50%, #00243D 100%);
        color: #DCE4E5;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Headers & Accents */
    h1, h2, h3, h4, h5, h6 {
        color: #00E5FF !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Scanning Solver Bar Animation */
    @keyframes scanning {
        0% { background-position: 100% 0%; }
        100% { background-position: -100% 0%; }
    }
    
    /* Glassmorphism KPI Card */
    .kpi-card {
        background: rgba(0, 36, 61, 0.45);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #003061 0%, #00e5ff 50%, #003061 100%);
        background-size: 200% 100%;
        animation: scanning 3s linear infinite;
        opacity: 0.7;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 229, 255, 0.6);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.2);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
        color: #A0C4DF;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.95rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        color: #00E5FF;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #7BB2D9;
        margin-top: 4px;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0, 26, 44, 0.6);
        padding: 8px;
        border-radius: 10px;
        border: 1px solid rgba(0, 229, 255, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #A0C4DF;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 18px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00E5FF !important;
        color: #001A2C !important;
        box-shadow: 0 4px 14px rgba(0, 229, 255, 0.4);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #0088FF 0%, #00E5FF 100%);
        color: #001A2C;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 229, 255, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #00E5FF 0%, #0088FF 100%);
        box-shadow: 0 6px 18px rgba(0, 229, 255, 0.6);
        transform: scale(1.02);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: rgba(0, 36, 61, 0.8) !important;
        color: #00E5FF !important;
        border-radius: 8px !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database tables and ensure sample CSV data is loaded exactly once on startup
database.init_db()

# Session state initialization
if "opt_results" not in st.session_state:
    st.session_state["opt_results"] = None
if "use_forecast" not in st.session_state:
    st.session_state["use_forecast"] = False
if "forecast_df" not in st.session_state:
    st.session_state["forecast_df"] = None
if "current_sql" not in st.session_state:
    st.session_state["current_sql"] = "SELECT * FROM Warehouses;"
if "opt_results" not in st.session_state:
    st.session_state["opt_results"] = None

# Load core tables from SQLite database
warehouses_df = database.get_table_data("Warehouses")
base_customers_df = database.get_table_data("Customers")
cost_df = database.get_table_data("TransportationCost")
trucks_df = database.get_table_data("Trucks")
historical_df = database.get_table_data("HistoricalDemand")

# Determine active customer demand scenario based on AI toggle
if st.session_state["use_forecast"] and st.session_state["forecast_df"] is not None:
    active_customers_df = st.session_state["forecast_df"]
    demand_mode_badge = "⚡ Active Mode: **AI Forecasted Demand (ML Ensemble)**"
else:
    active_customers_df = base_customers_df
    demand_mode_badge = "⚡ Active Mode: **Baseline Customer Demand (Static CSV)**"

# Header Banner
col_logo, col_title = st.columns([0.8, 5])
with col_logo:
    st.markdown("<h1 style='font-size: 3.5rem; margin-top: -10px;'>⚓</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1>Maersk AI-Based Logistics Network Optimizer</h1>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background: rgba(0, 229, 255, 0.12); border-left: 4px solid #00E5FF; padding: 10px 18px; border-radius: 6px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.95rem; color: #E0F2FE;">Integrates <b>Operations Research (MILP & VRP)</b> with <b>Ensemble Machine Learning</b> for Enterprise Container Allocation.</span>
            <span style="background: #00243D; padding: 4px 12px; border-radius: 20px; border: 1px solid #00E5FF; font-size: 0.85rem; color: #00E5FF;">{demand_mode_badge}</span>
        </div>
    """, unsafe_allow_html=True)

# Auto-solve SCIP MILP on initial startup so High-Fidelity UI Command Center has live optimal tables immediately
if st.session_state["opt_results"] is None:
    opt = optimizer.LogisticsOptimizer(warehouses_df, active_customers_df, cost_df, trucks_df)
    results = opt.solve()
    st.session_state["opt_results"] = results
    if results.get("status") in ["OPTIMAL", "FEASIBLE"]:
        database.save_shipments(results["shipments_df"])

# Main Navigation Tabs
tab_mockup, tab_opt, tab_ai, tab_viz, tab_vrp, tab_sql, tab_data = st.tabs([
    "🖥️ UI Command Center Mockups",
    "🚀 MILP Allocation Engine",
    "🔮 AI Demand Forecaster",
    "🌐 Network Analytics",
    "🚛 Vehicle Routing (VRP)",
    "🗄️ SQL Practice Sandbox",
    "📁 Data & Scenario Management"
])

# ---------------------------------------------------------
# TAB 0: HIGH-FIDELITY UI COMMAND CENTER MOCKUPS
# ---------------------------------------------------------
with tab_mockup:
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
    json_dump_escaped = json.dumps(live_screens_dict).replace('</script>', '<\\/script>')
    live_screens_js = '<script>window.ALL_SCREENS_HTML = ' + json_dump_escaped + ';</script>'
    
    final_spa_code = h_dash_clean.replace('<head>', '<head>' + live_screens_js, 1)
    
    components.html(final_spa_code, height=1150, scrolling=True)

# ---------------------------------------------------------
# TAB 1: MILP ALLOCATION ENGINE
# ---------------------------------------------------------
with tab_opt:
    st.markdown("### ⚡ Mixed Integer Linear Programming (MILP) Allocation Engine")
    st.write("Automatically computes the lowest-cost container allocation using **Google OR-Tools (`SCIP` MILP Solver)** with discrete truck trip coupling, exact demand fulfillment, and explainability rationales.")
    
    col_btn1, col_btn2, col_info = st.columns([1.5, 1.5, 3])
    with col_btn1:
        run_opt = st.button("🚀 Compute Optimal Plan", key="run_opt_btn")
    with col_btn2:
        if st.session_state["use_forecast"]:
            if st.button("⏪ Switch to Base Demand"):
                st.session_state["use_forecast"] = False
                st.rerun()
        else:
            if st.session_state["forecast_df"] is not None:
                if st.button("🔮 Switch to AI Forecast"):
                    st.session_state["use_forecast"] = True
                    st.rerun()

    # Automatically run optimizer if requested or not yet run
    if run_opt or st.session_state["opt_results"] is None:
        opt = optimizer.LogisticsOptimizer(warehouses_df, active_customers_df, cost_df, trucks_df)
        results = opt.solve()
        st.session_state["opt_results"] = results
        if results.get("status") in ["OPTIMAL", "FEASIBLE"]:
            database.save_shipments(results["shipments_df"])

    res = st.session_state["opt_results"]

    if res and res.get("status") in ["OPTIMAL", "FEASIBLE"]:
        total_cost = res["total_cost"]
        kpis = res.get("business_kpis", {})
        savings_inr = kpis.get("cost_savings_inr", 0.0)
        savings_pct = kpis.get("cost_savings_pct", 0.0)
        total_units = kpis.get("total_units_shipped", res.get("total_units_shipped", 1000))
        total_trips = kpis.get("total_truck_trips", res.get("total_truck_trips", 5))
        avg_dist = kpis.get("avg_shipment_distance_km", res.get("avg_shipment_distance_km", 297.0))

        # KPI Cards Row
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Optimal Freight Cost</div>
                    <div class="kpi-value">₹ {total_cost:,.0f}</div>
                    <div class="kpi-subtext">Optimized via SCIP MILP</div>
                </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Total Cost Savings</div>
                    <div class="kpi-value">₹ {savings_inr:,.0f}</div>
                    <div class="kpi-subtext">📉 {savings_pct}% vs Baseline</div>
                </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Discrete Truck Trips</div>
                    <div class="kpi-value">{total_trips} Trips</div>
                    <div class="kpi-subtext">Coupled Fleet Allocation</div>
                </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Total TEUs Shipped</div>
                    <div class="kpi-value">{total_units:,}</div>
                    <div class="kpi-subtext">100% Demand Fulfilled</div>
                </div>
            """, unsafe_allow_html=True)
        with k5:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Avg Transit Distance</div>
                    <div class="kpi-value">{avg_dist:.1f} km</div>
                    <div class="kpi-subtext">Weighted Route Proxy</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Explainability Engine & Step-by-Step Route Breakdown
        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.markdown("#### 📋 Step-by-Step Optimal MILP Allocation Table")
            ship_df = res["shipments_df"]
            if not ship_df.empty:
                display_df = ship_df[['Warehouse', 'Customer', 'UnitsShipped', 'TruckTrips', 'UnitCost', 'RouteCost']].copy()
                display_df.columns = ['Origin Hub', 'Destination Node', 'Units (TEUs)', 'Truck Trips', 'Rate (₹/unit)', 'Total Cost (₹)']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                csv_data = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Optimized Plan (CSV)",
                    data=csv_data,
                    file_name=f"maersk_milp_optimal_plan_{res.get('run_id', 'run')}.csv",
                    mime="text/csv"
                )

                st.markdown("#### 🧠 Automated Decision Explainability Panel")
                st.write("Select any active route below to inspect the mathematical dual and capacity rationale:")
                for idx, row in ship_df.iterrows():
                    with st.expander(f"📌 Why did Hub '{row['Warehouse']}' supply Client '{row['Customer']}' ({row['UnitsShipped']} TEUs)?"):
                        st.markdown(f"**Explaining Allocation Decision:** `{row.get('ExplainabilityRationale', 'Optimized via SCIP.')}`")
            else:
                st.info("No active shipments generated.")

        with c_right:
            st.markdown("#### 🔄 Route Flow Visual Cards")
            if not ship_df.empty:
                grouped = ship_df.groupby('Warehouse')
                for w_name, group in grouped:
                    flow_str = f"🏢 **Hub {w_name}**"
                    for _, s_row in group.iterrows():
                        flow_str += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;➔ **{s_row['Customer']}** = <span style='color: #00E5FF; font-weight: bold;'>{s_row['UnitsShipped']} TEUs ({s_row.get('TruckTrips', 1)} Truck)</span> [₹{s_row['RouteCost']:,.0f}]"
                    
                    st.markdown(f"""
                        <div style="background: rgba(0, 26, 44, 0.7); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                            {flow_str}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("#### ✅ Customer Fulfillment Audit")
            st.dataframe(res["fulfillment_df"], use_container_width=True, hide_index=True)

    elif res and res.get("status") == "INFEASIBLE":
        st.error(f"❌ **Infeasible Solution Encountered**: {res.get('message')}")
        st.warning("Please adjust customer demands or warehouse capacities in the Data & Scenario Management tab to restore feasibility.")

# ---------------------------------------------------------
# TAB 2: AI DEMAND FORECASTER
# ---------------------------------------------------------
with tab_ai:
    st.markdown("### 🔮 Machine Learning Demand Forecasting Component (`XGBoost / RandomForest`)")
    st.write("Ensemble tree models predict monthly container demand enriched with macroeconomic indices (`Sales_Index`), seasonal surges (`Festival_Flag`), and weather interruptions (`Rain_Storm_Flag`).")
    
    col_ctrl, col_chart = st.columns([1.3, 2.7])
    with col_ctrl:
        st.markdown("#### 🎛️ Simulation & Model Controls")
        model_choice = st.selectbox("ML Algorithm Engine", ["XGBoost (Preferred)", "Random Forest"])
        m_type = "xgboost" if "XGBoost" in model_choice else "random_forest"
        
        sales_idx = st.slider("Macro Sales Index", min_value=0.8, max_value=1.3, value=1.05, step=0.01)
        festival_flag = st.toggle("🎉 Peak Festival Season (Diwali / Eid)", value=False)
        rain_flag = st.toggle("🌧️ Monsoon / Heavy Rainfall Disturbance", value=False)
        promo_discount = st.slider("Bulk Discount Promo (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.5)

        # Train ML Model
        forecaster_obj = forecaster.DemandForecaster(model_type=m_type)
        metrics = forecaster_obj.train(historical_df)
        
        st.markdown(f"""
            <div style="background: rgba(0, 54, 90, 0.6); border: 1px solid #00E5FF; padding: 14px; border-radius: 8px; margin-top: 15px;">
                <div style="font-size: 0.85rem; color: #A0C4DF; text-transform: uppercase;">Prediction Accuracy Audit</div>
                <div style="font-size: 1.1rem; font-weight: bold; color: #00E5FF; margin-top: 4px;">
                    RMSE: {metrics.get('rmse', 0.0)} | MAE: {metrics.get('mae', 0.0)}
                </div>
                <div style="font-size: 0.9rem; color: #7BB2D9; margin-top: 4px;">
                    MAPE: <b>{metrics.get('mape', 0.0)}%</b> | R² Score: <b>{metrics.get('r2', 0.0)}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Predict next month
        pred_df = forecaster_obj.predict_next_month(
            customer_list=base_customers_df['Customer'].tolist(),
            sales_index=sales_idx,
            festival_flag=1 if festival_flag else 0,
            rain_flag=1 if rain_flag else 0,
            promo_discount=promo_discount
        )
        st.session_state["forecast_df"] = pred_df

        if st.button("⚡ Feed Forecast into MILP Optimizer", key="apply_ai_btn"):
            st.session_state["use_forecast"] = True
            st.session_state["opt_results"] = None
            st.success("AI Forecast loaded! Switch to MILP Allocation Engine to inspect downstream freight cost impact.")
            st.rerun()

    with col_chart:
        st.markdown("#### 📊 Downstream ML Integration Pipeline")
        st.markdown("""
            <div style="background: rgba(0, 229, 255, 0.08); border: 1px dashed #00E5FF; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 12px; font-weight: 600;">
                🔮 Predicted Customer Demand ➔ ⚡ OR-Tools MILP Allocation Engine ➔ 💰 Minimal Transportation Spend
            </div>
        """, unsafe_allow_html=True)
        fig_comp = visualization.plot_demand_comparison(base_customers_df, pred_df)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.markdown("#### 📈 ML Feature Importance Analysis")
        df_imp = forecaster_obj.get_feature_importances()
        if not df_imp.empty:
            st.dataframe(df_imp.head(6), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TAB 3: NETWORK ANALYTICS
# ---------------------------------------------------------
with tab_viz:
    st.markdown("### 🌐 Logistics Network Graph & Capacity Analytics")
    st.write("Representing warehouses and customers as nodes (`NetworkX`), with optimized shipment flows as dynamic weighted edges (`Plotly`).")
    
    if st.session_state["opt_results"] and st.session_state["opt_results"].get("status") in ["OPTIMAL", "FEASIBLE"]:
        res_df = st.session_state["opt_results"]["shipments_df"]
        util_df = st.session_state["opt_results"]["utilization_df"]
        
        fig_net = visualization.plot_logistics_network(res_df, warehouses_df, active_customers_df)
        st.plotly_chart(fig_net, use_container_width=True)
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            fig_util = visualization.plot_warehouse_utilization(util_df)
            st.plotly_chart(fig_util, use_container_width=True)
        with col_v2:
            fig_cost = visualization.plot_cost_breakdown(res_df)
            st.plotly_chart(fig_cost, use_container_width=True)
    else:
        st.info("💡 Please run the optimization in the **MILP Allocation Engine** tab to unlock live network graphs and charts.")

# ---------------------------------------------------------
# TAB 4: VEHICLE ROUTING PROBLEM (VRP)
# ---------------------------------------------------------
with tab_vrp:
    st.markdown("### 🚛 Capacitated Vehicle Routing Problem (CVRP) Delivery Engine")
    st.write("While the **MILP Allocation Engine** determines *how many* TEUs to ship between regional hubs, the **VRP Delivery Engine** uses **Google OR-Tools (`RoutingModel` with Guided Local Search)** to schedule exact multi-stop delivery loops (`Depot ➔ Stop A ➔ Stop B ➔ Depot`) for local truck fleets.")
    
    col_vrp_ctrl, col_vrp_res = st.columns([1.3, 2.7])
    with col_vrp_ctrl:
        st.markdown("#### ⚙️ Local Depot Routing Setup")
        selected_depot = st.selectbox("Select Origin Hub Depot:", warehouses_df["Warehouse"].tolist())
        num_vrp_trucks = st.slider("Available Local Delivery Trucks:", min_value=1, max_value=5, value=3)
        vrp_truck_cap = st.slider("Truck TEU Carrying Limit:", min_value=200, max_value=600, value=450, step=50)
        
        run_vrp = st.button("🚀 Schedule Multi-Stop Routes", key="run_vrp_btn")
    
    with col_vrp_res:
        if run_vrp:
            with st.spinner(f"Computing near-global optimal multi-stop routes from '{selected_depot}' using Guided Local Search..."):
                vrp_result = vrp_solver.run_sample_vrp(
                    depot_name=selected_depot,
                    customers_df=active_customers_df,
                    num_vehicles=num_vrp_trucks,
                    vehicle_capacity=vrp_truck_cap
                )
                
            if vrp_result.get("status") == "OPTIMAL":
                st.success(f"✅ VRP Routes Scheduled successfully for Depot **{selected_depot}**!")
                
                v_kpi1, v_kpi2, v_kpi3 = st.columns(3)
                with v_kpi1:
                    st.metric("Active Delivery Trucks", f"{vrp_result['active_trucks_count']} / {num_vrp_trucks} Trucks")
                with v_kpi2:
                    st.metric("Total Distance Traveled", f"{vrp_result['total_distance_km']:,} km")
                with v_kpi3:
                    st.metric("Total TEUs Dropped Off", f"{vrp_result['total_load_delivered']} TEUs")
                
                st.markdown("#### 🛣️ Multi-Stop Vehicle Route Itineraries")
                st.dataframe(vrp_result["routes_df"], use_container_width=True, hide_index=True)
            else:
                st.error(f"❌ {vrp_result.get('message', 'Infeasible routing configuration.')}")
        else:
            st.info("👈 Select a depot and click **Schedule Multi-Stop Routes** to run the CVRP Routing Library engine.")

# ---------------------------------------------------------
# TAB 5: SQL PRACTICE SANDBOX & ANALYTICS
# ---------------------------------------------------------
with tab_sql:
    st.markdown("### 🗄️ SQLite Database Exploration & Advanced SQL Analytics")
    st.write("Demonstrates SQL proficiency beyond simple persistence by executing pre-built analytical queries and live exploratory SQL against our 3NF schema (`Warehouses`, `Customers`, `TransportationCost`, `Trucks`, `Shipments`).")
    
    col_sql_left, col_sql_right = st.columns([1.3, 2.7])
    
    with col_sql_left:
        st.markdown("#### 📊 Advanced SQL Analytics Reports")
        st.write("Click to execute Maersk Portfolio SQL reports (`database.py`):")
        
        if st.button("📈 Shipment History Audit Trail", key="sql_rep_1"):
            df_rep = database.get_shipment_history()
            st.session_state["custom_sql_rep"] = ("Shipment History Audit Trail (Top 100 Runs)", df_rep)
        if st.button("🏢 Warehouse Financial Spend Analytics", key="sql_rep_2"):
            df_rep = database.get_warehouse_analytics()
            st.session_state["custom_sql_rep"] = ("Warehouse Financial Spend & Volume Analytics", df_rep)
        if st.button("📅 Monthly Cost & Fleet Dispatch Reports", key="sql_rep_3"):
            df_rep = database.get_monthly_cost_reports()
            st.session_state["custom_sql_rep"] = ("Monthly Time-Series Transportation Cost Reports", df_rep)
        if st.button("🔀 O-D Corridor Performance Benchmarks", key="sql_rep_4"):
            df_rep = database.get_route_performance()
            st.session_state["custom_sql_rep"] = ("Origin-Destination Route Performance Queries", df_rep)

        st.markdown("---")
        st.markdown("#### 📋 Quick Practice Queries")
        if st.button("🔍 `SELECT * FROM Warehouses;`", key="sql_btn_1"):
            st.session_state["current_sql"] = "SELECT * FROM Warehouses;"
        if st.button("🚛 `SELECT SUM(Capacity) FROM Trucks;`", key="sql_btn_2"):
            st.session_state["current_sql"] = "SELECT SUM(Capacity) AS Total_Truck_Capacity FROM Trucks;"
        if st.button("💰 `SELECT Warehouse, SUM(RouteCost) FROM Shipments GROUP BY Warehouse;`", key="sql_btn_3"):
            st.session_state["current_sql"] = "SELECT Warehouse, SUM(RouteCost) AS Total_Shipping_Cost, SUM(UnitsShipped) AS Total_Units FROM Shipments GROUP BY Warehouse;"

        st.markdown("#### 🗂️ Database Table Schema")
        selected_table_preview = st.selectbox("Inspect Table Schema:", ["Warehouses", "Customers", "TransportationCost", "Trucks", "Shipments", "HistoricalDemand"])
        df_preview = database.get_table_data(selected_table_preview)
        st.write(f"Row count: `{len(df_preview)} rows`")

    with col_sql_right:
        if "custom_sql_rep" in st.session_state and st.session_state["custom_sql_rep"]:
            rep_title, rep_df = st.session_state["custom_sql_rep"]
            st.markdown(f"#### ⭐ Advanced SQL Report: `{rep_title}`")
            st.dataframe(rep_df, use_container_width=True)
            if st.button("✖️ Clear Report View"):
                st.session_state["custom_sql_rep"] = None
                st.rerun()
            st.markdown("---")

        st.markdown("#### 💻 Interactive SQL Query Runner")
        default_sql = st.session_state.get("current_sql", "SELECT * FROM Warehouses;")
        query_input = st.text_area("Type your custom SQL query below:", value=default_sql, height=100)
        
        if st.button("⚡ Execute SQL Query", key="run_sql_btn"):
            df_sql_res, error_msg = database.execute_sql_query(query_input)
            if error_msg:
                st.error(f"❌ SQL Execution Error: `{error_msg}`")
            else:
                st.success("✅ Query executed successfully!")
                st.dataframe(df_sql_res, use_container_width=True)

        st.markdown("---")
        st.markdown(f"#### 🔍 Live Table Preview: `{selected_table_preview}`")
        st.dataframe(df_preview, use_container_width=True)

# ---------------------------------------------------------
# TAB 6: DATA & SCENARIO MANAGEMENT
# ---------------------------------------------------------
with tab_data:
    st.markdown("### 📁 Custom CSV Uploads & Scenario Management")
    st.write("Upload custom CSV files (`warehouses.csv` with Latitude/Longitude, etc.) to simulate new networks, or reset to our enriched Maersk baseline.")
    
    col_u1, col_u2, col_u3, col_u4 = st.columns(4)
    with col_u1:
        w_file = st.file_uploader("Upload Warehouses CSV", type=["csv"], key="w_up")
        if w_file:
            df_w_new = pd.read_csv(w_file)
            df_w_new.to_csv(os.path.join(database.DATA_DIR, "warehouses.csv"), index=False)
            database.seed_data_from_csvs(overwrite=True)
            st.session_state["opt_results"] = None
            st.success("Updated Warehouses!")
            st.rerun()
    with col_u2:
        c_file = st.file_uploader("Upload Customers CSV", type=["csv"], key="c_up")
        if c_file:
            df_c_new = pd.read_csv(c_file)
            df_c_new.to_csv(os.path.join(database.DATA_DIR, "customers.csv"), index=False)
            database.seed_data_from_csvs(overwrite=True)
            st.session_state["opt_results"] = None
            st.success("Updated Customers!")
            st.rerun()
    with col_u3:
        tc_file = st.file_uploader("Upload Transport Cost CSV", type=["csv"], key="tc_up")
        if tc_file:
            df_tc_new = pd.read_csv(tc_file)
            df_tc_new.to_csv(os.path.join(database.DATA_DIR, "transport_cost.csv"), index=False)
            database.seed_data_from_csvs(overwrite=True)
            st.session_state["opt_results"] = None
            st.success("Updated Costs!")
            st.rerun()
    with col_u4:
        tr_file = st.file_uploader("Upload Trucks CSV", type=["csv"], key="tr_up")
        if tr_file:
            df_tr_new = pd.read_csv(tr_file)
            df_tr_new.to_csv(os.path.join(database.DATA_DIR, "trucks.csv"), index=False)
            database.seed_data_from_csvs(overwrite=True)
            st.session_state["opt_results"] = None
            st.success("Updated Trucks!")
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset Database & CSVs to Enriched Maersk Default Scenario", key="reset_btn"):
        database.seed_data_from_csvs(overwrite=True)
        st.session_state["opt_results"] = None
        st.session_state["use_forecast"] = False
        st.success("Successfully reset all datasets to our enriched Maersk scenario!")
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #7BB2D9; font-size: 0.85rem; padding: 10px;">
        AI-Based Logistics Network Optimizer | Built with Python, Google OR-Tools (MILP & VRP), SQLite, Plotly & Streamlit | Maersk Logistics Portfolio Project
    </div>
""", unsafe_allow_html=True)
