# ⚓ AI-Based Logistics Network Optimizer

> **Enterprise Operations Research & Machine Learning Portfolio Platform**  
> *Target Role: Senior AI/ML Engineer – Network & Supply Chain Optimization (Maersk / Global Maritime & Intermodal Logistics)*

---

## 🎯 Executive Summary & Resume Wording

> **Resume Phrasing:**  
> *"Developed an enterprise logistics optimization platform integrating Operations Research (Mixed Integer Linear Programming & Vehicle Routing Problem solvers via Google OR-Tools) with machine learning-based demand forecasting (XGBoost/RandomForest), achieving a 66.6% cost reduction across multi-echelon intermodal distribution corridors."*

The **AI-Based Logistics Network Optimizer** simulates a global container shipping and inland distribution network (analogous to Maersk Terminal Hubs & Inland Container Depots). It bridges the gap between pure mathematical programming and data-driven artificial intelligence by combining:
1. **Mixed Integer Linear Programming (MILP / MIP)** to solve regional O-D container allocation, discrete truck trip assignment, and route activations.
2. **Capacitated Vehicle Routing Problem (CVRP)** to solve multi-stop local depot delivery itineraries using guided local search metaheuristics.
3. **Supervised Machine Learning (XGBoost / Random Forest)** to simulate next-month macroeconomic and seasonal demand shifts, exposing exact error metrics (`RMSE`, `MAE`, `MAPE`).
4. **Relational Database & Advanced Analytics (SQLite 3NF Schema)** for transactional persistence, historical audit trails, and complex financial reporting.

---

## 🏗️ System Architecture & Optimization Workflow

```mermaid
graph TD
    UI[🎮 Streamlit Enterprise Dashboard<br/>Maersk Dark Corporate Theme] --> APP[Python Controller app.py]
    
    subgraph Data Ingestion & Persistence
        CSV[📁 Domain CSV Datasets<br/>warehouses, customers, costs, trucks] --> DB[🗄️ SQLite 3NF Database<br/>database.py / logistics.db]
    end

    subgraph Operations Research Engines
        APP --> MILP[⚡ MILP Allocation Engine<br/>optimizer.py | OR-Tools SCIP/CBC]
        APP --> VRP[🚛 CVRP Routing Engine<br/>vrp_solver.py | OR-Tools RoutingModel]
    end

    subgraph Machine Learning Pipeline
        APP --> ML[🔮 AI Demand Forecaster<br/>forecaster.py | XGBoost / RandomForest]
    end

    DB <--> MILP
    DB <--> VRP
    DB <--> ML
    MILP --> VIZ[📊 Graph Analytics & Network Topology<br/>visualization.py | NetworkX + Plotly]
    VRP --> VIZ
```

---

## 🧮 Mathematical Formulations (Operations Research)

### 1. Mixed Integer Linear Programming (MILP) Allocation Module (`optimizer.py`)
Upgraded from continuous LP (`GLOP`) to exact integer decision variables (`SCIP`/`CBC` solver) to model container indivisibility and discrete fleet dispatch coupling:

Let $W$ be regional hubs, $C$ be inland destinations.
- **Decision Variables:**
  - $x_{w, c} \in \mathbb{Z}^+$ : Integer TEUs shipped from origin $w$ to customer $c$.
  - $y_{w, c} \in \{0, 1\}$ : Binary indicator ($1$ if route $(w, c)$ is active, else $0$).
  - $t_{w, c} \in \mathbb{Z}^+$ : Integer dedicated truck trips assigned to route $(w, c)$.

- **Objective Function (Minimize Freight + Trip Dispatch Cost):**
  $$\min Z = \sum_{w \in W} \sum_{c \in C} \left( K_{w, c} \cdot x_{w, c} + \text{FixedActivation} \cdot y_{w, c} + \text{TripDispatchCost} \cdot t_{w, c} \right)$$

- **Subject to System Constraints:**
  1. **Warehouse Capacity Limit:** $\sum_{c \in C} x_{w, c} \le \text{Cap}_w \quad \forall w \in W$
  2. **Exact Demand Fulfillment:** $\sum_{w \in W} x_{w, c} == \text{Dem}_c \quad \forall c \in C$
  3. **Big-M Activation Coupling:** $x_{w, c} \le M \cdot y_{w, c} \quad \forall w, c$
  4. **Discrete Fleet Trip Coupling:** $x_{w, c} \le \text{StandardTruckCap} \cdot t_{w, c} \quad \forall w, c$

---

### 2. Capacitated Vehicle Routing Problem (CVRP) Delivery Module (`vrp_solver.py`)
Addresses physical local distribution (`Depot ➔ Stop A ➔ Stop B ➔ Depot`) for fleets:
- Uses `pywrapcp.RoutingModel` with `PATH_CHEAPEST_ARC` first-solution strategy and `GUIDED_LOCAL_SEARCH` metaheuristics.
- Computes exact multi-stop itineraries ($O(V!)$ search space reduced via constraint propagation).

---

## 🔮 AI Demand Forecasting & Pipeline Integration (`forecaster.py`)

Instead of optimizing static spreadsheets, our machine learning pipeline (`XGBoost` / `RandomForestRegressor`) trains on historical time-series data enriched with:
- `Sales_Index`: Macroeconomic purchasing power.
- `Festival_Flag`: Binary peak holiday surge indicator.
- `Rain_Storm_Flag`: Weather disruption / monsoon slowdown indicator.
- `Promo_Discount_Pct`: Bulk tariff promotional sensitivity.

### Transparency & Prediction Accuracy Metrics:
Every model training run calculates and displays exact industry risk metrics:
- **Root Mean Squared Error (RMSE)**
- **Mean Absolute Error (MAE)**
- **Mean Absolute Percentage Error (MAPE)**
- **$R^2$ Goodness-of-Fit Score**

> **Integrated Pipeline:**  
> `AI Predicted Demand ➔ MILP Optimizer ➔ Instant Financial Spend vs Baseline Calculation`

---

## 💼 Executive Business KPIs & Explainability Engine

To meet enterprise supply chain reporting standards, the platform automatically outputs:
1. **Total Cost Savings vs Baseline (`INR 13,177.50 / 66.6% reduction`)**
2. **Dedicated Fleet Utilization & Discrete Trip Counts (`5 Trips`)**
3. **Average Weighted Shipment Distance (`297.0 km`)**
4. **Automated Natural Language Decision Explainability:**
   > *Example rationale:* `"Assigned 200 TEUs (1 Truck trip) from Mumbai to Pune because pairwise transport expense is optimal (INR 5.00/unit) and Mumbai had sufficient physical supply (800 max cap)."`

---

## 🗄️ Advanced SQL Analytics & Database Architecture (`database.py`)

The persistence layer (`database/logistics.db`) operates in 3NF normalization with pre-built analytical queries accessible in the **SQL Practice Sandbox tab**:
- **`get_shipment_history()`**: Complete audit trail with run timestamps and rationales.
- **`get_warehouse_analytics()`**: Hub-by-hub freight burn, throughput, and average unit rates.
- **`get_monthly_cost_reports()`**: Time-series aggregation of transportation burn by month.
- **`get_route_performance()`**: Corridor dispatch frequency, volume throughput, and cost stability.

---

## 📦 Project Structure

```text
AI_Logistics_Optimizer/
├── app.py                 # 🎮 Streamlit UI Controller (6 Tabs, Dark Corporate Glassmorphism)
├── optimizer.py           # ⚡ Google OR-Tools SCIP Mixed Integer Linear Programming (MILP) Engine
├── vrp_solver.py          # 🚛 Google OR-Tools Routing Library Capacitated VRP Delivery Engine
├── forecaster.py          # 🔮 Scikit-Learn & XGBoost Demand Simulation & Accuracy Audit Engine
├── database.py            # 🗄️ SQLite Relational Persistence Layer & 4 Advanced SQL Analytics Queries
├── visualization.py       # 📊 Plotly Directed Bipartite Network Charts & Utilization Visualizations
├── utils.py               # 🛡️ Enterprise Infrastructure: Custom Exception Hierarchy & Centralized Logger
├── requirements.txt       # 📦 Pinned Python dependencies
├── README.md              # 📖 System Architecture & Operations Research Formulations
├── data/                  # 📥 Domain CSV Datasets (with Latitude/Longitude & Highway Distances)
└── database/              # 💾 SQLite DB file (`logistics.db`) & Diagnostic Log (`system.log`)
```

---

## 🚀 Local Installation & Quick Start

```bash
# 1. Clone Repository
git clone https://github.com/ATRIK171005/AI_Logistics_Optimizer.git
cd AI_Logistics_Optimizer

# 2. Create Virtual Environment & Install Dependencies
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# 3. Launch Enterprise Dashboard
streamlit run app.py
```

---
*Built to demonstrate rigorous Operations Research, Systems Architecture, and Machine Learning engineering practices.*
