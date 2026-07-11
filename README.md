# ⚓ AI-Based Logistics Network Optimizer

An enterprise-grade internal logistics and supply chain optimization platform designed to automatically compute the cheapest multi-warehouse shipment plan while adhering to capacity, demand, and fleet constraints. Built as a tailored portfolio project demonstrating key engineering capabilities required for **Maersk Operations Research and Logistics Planning roles**.

---

## 🏗️ Architecture & Core Components

This project bridges **Linear Programming (Google OR-Tools)**, **Relational Database Engineering (SQLite)**, **Applied Machine Learning (XGBoost & Random Forest)**, and **Interactive Visualizations (Plotly, NetworkX & Streamlit)**.

```text
AI_Logistics_Optimizer/
│
├── app.py                 # Maersk-themed 5-tab Streamlit Executive Dashboard
├── optimizer.py           # Google OR-Tools Linear Programming Solver (GLOP)
├── forecaster.py          # Machine Learning Demand Prediction Engine (XGBoost / Random Forest)
├── database.py            # SQLite ORM, table schemas, CSV synchronizer, and SQL Query Engine
├── visualization.py       # NetworkX bipartite flow graphs & Plotly interactive charts
├── requirements.txt       # Python dependencies
├── README.md              # Technical documentation & resume highlights
│
├── data/                  # Source CSV Datasets
│   ├── warehouses.csv     # Warehouse capacities (Kolkata, Mumbai, Chennai, Delhi)
│   ├── customers.csv      # Customer demand requirements (Pune, Jaipur, Lucknow, Bangalore, Hyderabad)
│   ├── transport_cost.csv # Complete 20-route transportation cost matrix (₹ per unit)
│   ├── trucks.csv         # Truck fleet inventory & capacities
│   └── historical_demand.csv # 24 months of rich historical data with weather & festival indicators
│
└── database/
    └── logistics.db       # Auto-generated SQLite relational database
```

---

## 📐 Mathematical Formulation (Linear Programming)

The optimization model uses Google OR-Tools (`pywraplp.Solver.CreateSolver('GLOP')`) to solve the classic **Minimum Cost Flow / Transportation Optimization Problem**.

Let:
- $W$: Set of Warehouses ($i \in W$)
- $C$: Set of Customers ($j \in C$)
- $S_i$: Max Capacity of Warehouse $i$
- $D_j$: Required Demand of Customer $j$
- $c_{i,j}$: Unit transportation cost from Warehouse $i$ to Customer $j$
- $T$: Total available Truck fleet carrying capacity ($\sum \text{TruckCapacity}$)

### 1. Decision Variables
$$x_{i,j} \ge 0 \quad \forall i \in W, j \in C$$
Where $x_{i,j}$ is the continuous/integer units shipped from Warehouse $i$ to Customer $j$.

### 2. Objective Function (Minimize Total Cost)
$$\text{Minimize } Z = \sum_{i \in W} \sum_{j \in C} c_{i,j} \times x_{i,j}$$

### 3. System Constraints
- **Warehouse Capacity Constraint**: Total outgoing shipments cannot exceed warehouse limits:
  $$\sum_{j \in C} x_{i,j} \le S_i \quad \forall i \in W$$
- **Customer Demand Fulfillment Constraint**: Each customer must receive their exact demand:
  $$\sum_{i \in W} x_{i,j} = D_j \quad \forall j \in C$$
- **Truck Fleet Carrying Capacity Constraint**: Total network flow cannot exceed available truck capacity:
  $$\sum_{i \in W} \sum_{j \in C} x_{i,j} \le \sum_{k \in \text{Trucks}} \text{Capacity}_k$$

---

## 🔮 AI Component: Applied Machine Learning Demand Forecasting

Rather than assuming static customer demands, `forecaster.py` integrates a machine learning engine capable of predicting next month's customer demand using macro-economic and environmental features:
- `Sales_Index` ($0.8 - 1.3$ Regional purchasing power index)
- `Festival_Flag` (`1` during Diwali, Eid, Christmas peak shipping seasons; `0` otherwise)
- `Rain_Storm_Flag` (`1` during heavy monsoon rain disturbances disrupting local stocking; `0` otherwise)
- `Promo_Discount_Pct` (Bulk discount percentage applied)

We train **XGBoost (`XGBRegressor`)** and **Random Forest (`RandomForestRegressor`)** models on 24 months of synthetic historical demand data (`historical_demand.csv`). Predicted demands can be applied with a single click directly into the OR-Tools optimization loop.

---

## 🗄️ SQLite Database Schema & SQL Practice Engine

All data is persisted in a local relational database (`database/logistics.db`) across 6 tables:
1. `Warehouses(Warehouse TEXT PRIMARY KEY, Capacity INTEGER)`
2. `Customers(Customer TEXT PRIMARY KEY, Demand INTEGER)`
3. `TransportationCost(Warehouse TEXT, Customer TEXT, Cost REAL, PRIMARY KEY (Warehouse, Customer))`
4. `Trucks(Truck TEXT PRIMARY KEY, Capacity INTEGER, CostPerTrip REAL)`
5. `Shipments(id INTEGER PRIMARY KEY, RunID TEXT, Warehouse TEXT, Customer TEXT, UnitsShipped INTEGER, UnitCost REAL, RouteCost REAL, Timestamp DATETIME)`
6. `HistoricalDemand(Month TEXT, Customer TEXT, Demand INTEGER, Sales_Index REAL, Festival_Flag INTEGER, Rain_Storm_Flag INTEGER, Promo_Discount_Pct REAL)`

### Practice SQL Queries (Directly Executable via Dashboard Sandbox)
You can practice key SQL operations required for Maersk interviews directly inside our dashboard's **SQL Practice Sandbox** tab:
- **Inspect Warehouses**:
  ```sql
  SELECT * FROM Warehouses;
  ```
- **Compute Total Fleet Capacity**:
  ```sql
  SELECT SUM(Capacity) AS Total_Truck_Capacity, AVG(CostPerTrip) AS Avg_Trip_Cost FROM Trucks;
  ```
- **Analyze Shipping Expenses by Warehouse**:
  ```sql
  SELECT Warehouse, SUM(RouteCost) AS Total_Shipping_Cost, SUM(UnitsShipped) AS Total_Units 
  FROM Shipments GROUP BY Warehouse;
  ```

---

## 🚀 Quickstart & Installation Guide

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Sample Scenario
```powershell
python database.py
```

### 3. Launch the Executive Streamlit Dashboard
```powershell
streamlit run app.py
```
The dashboard will open automatically in your browser (typically at `http://localhost:8501`).

---

## 💡 Resume Highlights for Technical Interviews

When discussing this project with **Maersk Operations Research or Logistics Engineering teams**, you can truthfully say:
- **✅ Built Operations Research Models**: *"Developed multi-constraint linear programming transportation models using Google OR-Tools (`pywraplp.Solver`), optimizing multi-warehouse logistics flows across 20 routes to minimize total network costs while strictly satisfying warehouse capacity and exact customer demands."*
- **✅ Integrated End-to-End Applied Machine Learning**: *"Engineered an integrated XGBoost & Random Forest demand forecasting pipeline trained on historical macroeconomic and seasonal indicators (`Sales_Index`, `Festival_Flag`, weather anomalies) that directly feeds predicted customer requirements into the LP optimizer for data-driven logistics planning."*
- **✅ Designed Relational Database Architecture**: *"Architected a normalized SQLite database engine (`logistics.db`) across 6 tables with built-in SQL auditing capabilities and interactive query sandboxes to track historical shipment runs and capacity limits."*
- **✅ Created Enterprise Visualizations & Dashboards**: *"Designed a 5-tab, Maersk-styled (`#00243D` navy & `#00E5FF` cyan) Streamlit executive decision-support dashboard featuring dynamic bipartite directed network maps (`NetworkX` + `Plotly`), capacity utilization charts, and one-click CSV export pipelines."*
