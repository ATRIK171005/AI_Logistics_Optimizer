import streamlit as st
import pandas as pd
import numpy as np
import os
import database
import optimizer
import forecaster
import visualization

# Set Streamlit page configuration
st.set_page_config(
    page_title="AI-Based Logistics Network Optimizer | Maersk",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Maersk-Inspired Corporate CSS (Dark Navy #00243D + Vibrant Cyan #00E5FF)
st.markdown("""
    <style>
    /* Main Background and Text */
    .stApp {
        background: linear-gradient(135deg, #001A2C 0%, #00243D 50%, #00365A 100%);
        color: #FFFFFF;
        font-family: 'Inter', 'Roboto', sans-serif;
    }
    
    /* Headers & Accents */
    h1, h2, h3, h4, h5, h6 {
        color: #00E5FF !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Glassmorphism KPI Card */
    .kpi-card {
        background: rgba(0, 54, 90, 0.45);
        border: 1px solid rgba(0, 229, 255, 0.35);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        margin-bottom: 15px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: #00E5FF;
    }
    .kpi-title {
        font-size: 0.95rem;
        color: #A0C4DF;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #00E5FF;
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
        padding: 0 20px;
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
        box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 229, 255, 0.5);
    }
    
    /* DataFrame Styling */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(0, 229, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Database and Session States
database.init_db()

if "opt_results" not in st.session_state:
    st.session_state["opt_results"] = None
if "use_forecast" not in st.session_state:
    st.session_state["use_forecast"] = False
if "forecast_df" not in st.session_state:
    st.session_state["forecast_df"] = None

# Load Base Datasets from SQLite
warehouses_df = database.get_table_data("Warehouses")
base_customers_df = database.get_table_data("Customers")
cost_df = database.get_table_data("TransportationCost")
trucks_df = database.get_table_data("Trucks")
historical_df = database.get_table_data("HistoricalDemand")

# Determine which customer demand to use
if st.session_state["use_forecast"] and st.session_state["forecast_df"] is not None:
    active_customers_df = st.session_state["forecast_df"]
    demand_mode_badge = "🔮 AI Forecasted Demand Active"
else:
    active_customers_df = base_customers_df
    demand_mode_badge = "📋 Base Scenario Demand Active"

# Header Section
st.markdown("""
    <div style="background: rgba(0, 36, 61, 0.6); padding: 24px; border-radius: 14px; border: 1px solid rgba(0, 229, 255, 0.3); margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 2.3rem; color: #00E5FF;">⚓ AI-Based Logistics Network Optimizer</h1>
            <p style="margin: 6px 0 0 0; color: #B3D8F5; font-size: 1.05rem;">
                Internal Supply Chain & Transportation Planning Tool | Powered by Google OR-Tools & Machine Learning
            </p>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(0, 229, 255, 0.15); border: 1px solid #00E5FF; color: #00E5FF; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                MAERSK ENTERPRISE LOGISTICS
            </span>
            <div style="margin-top: 8px; color: #7BB2D9; font-size: 0.9rem;">
                Demand State: <b>{}</b>
            </div>
        </div>
    </div>
""".format(demand_mode_badge), unsafe_allow_html=True)

# Main Navigation Tabs
tab_opt, tab_ai, tab_viz, tab_sql, tab_data = st.tabs([
    "🚀 Optimization Engine",
    "🔮 AI Demand Forecaster",
    "🌐 Network Analytics",
    "🗄️ SQL Practice Sandbox",
    "📁 Data & Scenario Management"
])

# ---------------------------------------------------------
# TAB 1: OPTIMIZATION ENGINE
# ---------------------------------------------------------
with tab_opt:
    st.markdown("### ⚡ Multi-Constraint Network Optimization Engine")
    st.write("Automatically computes the cheapest shipment plan across all warehouses and customers using **Google OR-Tools (`GLOP` Linear Solver)** while strictly satisfying warehouse capacity, exact customer demand fulfillment, and total truck fleet capacities.")
    
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

    # Automatically run optimizer on button click or if no results exist yet
    if run_opt or st.session_state["opt_results"] is None:
        opt = optimizer.LogisticsOptimizer(warehouses_df, active_customers_df, cost_df, trucks_df)
        results = opt.solve()
        st.session_state["opt_results"] = results
        if results.get("status") in ["OPTIMAL", "FEASIBLE"]:
            database.save_shipments(results["shipments_df"])

    res = st.session_state["opt_results"]

    if res and res.get("status") in ["OPTIMAL", "FEASIBLE"]:
        total_cost = res["total_cost"]
        total_units = res["total_units_shipped"]
        avg_cost = round(total_cost / total_units, 2) if total_units > 0 else 0
        total_fleet_cap = trucks_df['Capacity'].sum() if not trucks_df.empty else 0
        fleet_util = round((total_units / total_fleet_cap) * 100, 1) if total_fleet_cap > 0 else 0

        # KPI Cards Row
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Optimal Total Cost</div>
                    <div class="kpi-value">₹ {total_cost:,.0f}</div>
                    <div class="kpi-subtext">Optimized across 20 routes</div>
                </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Total Shipped Units</div>
                    <div class="kpi-value">{total_units:,}</div>
                    <div class="kpi-subtext">100% Demand Fulfilled</div>
                </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Average Cost / Unit</div>
                    <div class="kpi-value">₹ {avg_cost:,.2f}</div>
                    <div class="kpi-subtext">Weighted Route Average</div>
                </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Fleet Capacity Utilized</div>
                    <div class="kpi-value">{fleet_util}%</div>
                    <div class="kpi-subtext">Total Fleet: {total_fleet_cap:,} units</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Step-by-Step Route Breakdown Table and Download
        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.markdown("#### 📋 Step-by-Step Optimal Shipment Plan")
            ship_df = res["shipments_df"]
            if not ship_df.empty:
                display_df = ship_df[['Warehouse', 'Customer', 'UnitsShipped', 'UnitCost', 'RouteCost']].copy()
                display_df.columns = ['Warehouse Origin', 'Customer Destination', 'Units Shipped', 'Unit Cost (₹)', 'Route Cost (₹)']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Download button
                csv_data = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Optimized Plan (CSV)",
                    data=csv_data,
                    file_name=f"optimal_logistics_plan_{res.get('run_id', 'maersk')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No shipments generated.")

        with c_right:
            st.markdown("#### 🔄 Route Flow Visual Cards")
            if not ship_df.empty:
                # Group by warehouse to show clean card flow like in Step 4 of prompt
                grouped = ship_df.groupby('Warehouse')
                for w_name, group in grouped:
                    flow_str = f"🏢 **Warehouse {w_name}**"
                    for _, s_row in group.iterrows():
                        flow_str += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;➔ **{s_row['Customer']}** = <span style='color: #00E5FF; font-weight: bold;'>{s_row['UnitsShipped']} units</span> (₹{s_row['RouteCost']:,.0f})"
                    
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
    st.markdown("### 🔮 Machine Learning Demand Forecasting Component")
    st.write("To make this platform more than just standard linear optimization, we train ensemble tree models (**XGBoost / Random Forest**) on historical monthly demand data enriched with macroeconomic and seasonal indicators.")
    
    col_ctrl, col_chart = st.columns([1.2, 2.8])
    with col_ctrl:
        st.markdown("#### 🎛️ Simulation Controls")
        model_choice = st.selectbox("ML Algorithm Type", ["XGBoost (Preferred)", "Random Forest"])
        m_type = "xgboost" if "XGBoost" in model_choice else "random_forest"
        
        sales_idx = st.slider("Macro Sales Index", min_value=0.8, max_value=1.3, value=1.05, step=0.01, help="Regional purchasing power index (1.0 = Normal baseline)")
        festival_flag = st.toggle("🎉 Peak Festival Season (Diwali / Eid)", value=False, help="Adds surge demand for holiday stocking")
        rain_flag = st.toggle("🌧️ Monsoon / Heavy Rainfall Disturbance", value=False, help="Reflects weather-induced stocking shifts")
        promo_discount = st.slider("Bulk Discount Promo (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.5)

        # Train ML Model
        forecaster_obj = forecaster.DemandForecaster(model_type=m_type)
        r2, mae = forecaster_obj.train(historical_df)
        
        st.markdown(f"""
            <div style="background: rgba(0, 229, 255, 0.1); border-left: 4px solid #00E5FF; padding: 12px; border-radius: 6px; margin-top: 15px;">
                <div style="font-size: 0.85rem; color: #B3D8F5;">Model Training Accuracy</div>
                <div style="font-size: 1.1rem; font-weight: bold; color: #00E5FF;">R² Score: {r2:.3f} | MAE: {mae:.1f} units</div>
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

        if st.button("⚡ Feed Forecast into Optimizer", key="apply_ai_btn"):
            st.session_state["use_forecast"] = True
            st.session_state["opt_results"] = None # Re-run optimizer automatically
            st.success("AI Forecasted demand loaded! Switch to the Optimization Engine tab to see updated results.")
            st.rerun()

    with col_chart:
        st.markdown("#### 📊 Base vs Predicted Next Month Demand Comparison")
        fig_comp = visualization.plot_demand_comparison(base_customers_df, pred_df)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Show feature importances
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
        
        # Interactive Network Graph
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
        st.info("💡 Please run the optimization in the **Optimization Engine** tab to unlock live network graphs and charts.")

# ---------------------------------------------------------
# TAB 4: SQL PRACTICE SANDBOX
# ---------------------------------------------------------
with tab_sql:
    st.markdown("### 🗄️ SQLite Database Exploration & SQL Practice Sandbox")
    st.write("Satisfy our required SQL skills by exploring the `logistics.db` schema and executing live SQL queries directly against our tables (`Warehouses`, `Customers`, `TransportationCost`, `Trucks`, `Shipments`).")
    
    col_sql_left, col_sql_right = st.columns([1.3, 2.7])
    
    with col_sql_left:
        st.markdown("#### 📋 Quick Practice Queries")
        st.write("Click any pre-built SQL query below to execute instantly:")
        
        if st.button("🔍 `SELECT * FROM Warehouses;`", key="sql_btn_1"):
            st.session_state["current_sql"] = "SELECT * FROM Warehouses;"
        if st.button("🚛 `SELECT SUM(Capacity) FROM Trucks;`", key="sql_btn_2"):
            st.session_state["current_sql"] = "SELECT SUM(Capacity) AS Total_Truck_Capacity FROM Trucks;"
        if st.button("💰 `SELECT Warehouse, SUM(RouteCost) as Total_Cost FROM Shipments GROUP BY Warehouse;`", key="sql_btn_3"):
            st.session_state["current_sql"] = "SELECT Warehouse, SUM(RouteCost) AS Total_Shipping_Cost, SUM(UnitsShipped) AS Total_Units FROM Shipments GROUP BY Warehouse;"
        if st.button("🛒 `SELECT * FROM Customers WHERE Demand >= 200;`", key="sql_btn_4"):
            st.session_state["current_sql"] = "SELECT * FROM Customers WHERE Demand >= 200 ORDER BY Demand DESC;"
        if st.button("📜 `SELECT * FROM TransportationCost WHERE Cost < 15;`", key="sql_btn_5"):
            st.session_state["current_sql"] = "SELECT * FROM TransportationCost WHERE Cost < 15 ORDER BY Cost ASC;"

        st.markdown("#### 🗂️ Database Tables")
        selected_table_preview = st.selectbox("Inspect Table Schema:", ["Warehouses", "Customers", "TransportationCost", "Trucks", "Shipments", "HistoricalDemand"])
        df_preview = database.get_table_data(selected_table_preview)
        st.write(f"Row count: `{len(df_preview)} rows`")

    with col_sql_right:
        st.markdown("#### 💻 Interactive SQL Query Runner")
        default_sql = st.session_state.get("current_sql", "SELECT * FROM Warehouses;")
        query_input = st.text_area("Type your custom SQL query below:", value=default_sql, height=110)
        
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
# TAB 5: DATA & SCENARIO MANAGEMENT
# ---------------------------------------------------------
with tab_data:
    st.markdown("### 📁 Custom CSV Uploads & Scenario Management")
    st.write("Upload custom CSV files to simulate different warehouse networks, or reset to the default Maersk interview scenario at any time.")
    
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
    if st.button("🔄 Reset Database & CSVs to Maersk Default Scenario", key="reset_btn"):
        database.seed_data_from_csvs(overwrite=True)
        st.session_state["opt_results"] = None
        st.session_state["use_forecast"] = False
        st.success("Successfully reset all datasets to our default Maersk scenario!")
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #7BB2D9; font-size: 0.85rem; padding: 10px;">
        AI-Based Logistics Network Optimizer | Built with Python, Google OR-Tools, SQLite, Plotly & Streamlit | Maersk Logistics Portfolio Project
    </div>
""", unsafe_allow_html=True)
