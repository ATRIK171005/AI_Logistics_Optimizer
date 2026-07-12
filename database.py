import sqlite3
import pandas as pd
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "logistics.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create all required tables in SQLite if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Warehouses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Warehouses (
            Warehouse TEXT PRIMARY KEY,
            Capacity INTEGER
        )
    """)

    # 2. Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            Customer TEXT PRIMARY KEY,
            Demand INTEGER
        )
    """)

    # 3. TransportationCost table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TransportationCost (
            Warehouse TEXT,
            Customer TEXT,
            Cost REAL,
            PRIMARY KEY (Warehouse, Customer)
        )
    """)

    # 4. Trucks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Trucks (
            Truck TEXT PRIMARY KEY,
            Capacity INTEGER,
            CostPerTrip REAL
        )
    """)

    # 5. Shipments table (stores optimization runs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            RunID TEXT,
            Warehouse TEXT,
            Customer TEXT,
            UnitsShipped INTEGER,
            UnitCost REAL,
            RouteCost REAL,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. HistoricalDemand table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HistoricalDemand (
            Month TEXT,
            Customer TEXT,
            Demand INTEGER,
            Sales_Index REAL,
            Festival_Flag INTEGER,
            Rain_Storm_Flag INTEGER,
            Promo_Discount_Pct REAL
        )
    """)

    # Alter Shipments table to ensure MILP integer and explainability columns exist
    try:
        cursor.execute("ALTER TABLE Shipments ADD COLUMN TruckTrips INTEGER DEFAULT 1")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE Shipments ADD COLUMN ExplainabilityRationale TEXT")
    except Exception:
        pass

    conn.commit()
    conn.close()

    # Seed data if tables are empty
    seed_data_from_csvs(overwrite=False)

def seed_data_from_csvs(overwrite=False):
    """Seed SQLite database tables from CSV files in the data/ folder."""
    conn = get_connection()
    try:
        # Check if tables are already populated
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Warehouses")
        w_count = cursor.fetchone()[0]
        
        if w_count == 0 or overwrite:
            if overwrite:
                for table in ["Warehouses", "Customers", "TransportationCost", "Trucks", "HistoricalDemand"]:
                    cursor.execute(f"DELETE FROM {table}")
                conn.commit()

            # Load CSVs and write to SQLite
            w_df = pd.read_csv(os.path.join(DATA_DIR, "warehouses.csv"))
            w_df.to_sql("Warehouses", conn, if_exists="replace", index=False)

            c_df = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
            c_df.to_sql("Customers", conn, if_exists="replace", index=False)

            tc_df = pd.read_csv(os.path.join(DATA_DIR, "transport_cost.csv"))
            tc_df.to_sql("TransportationCost", conn, if_exists="replace", index=False)

            tr_df = pd.read_csv(os.path.join(DATA_DIR, "trucks.csv"))
            tr_df.to_sql("Trucks", conn, if_exists="replace", index=False)

            if os.path.exists(os.path.join(DATA_DIR, "historical_demand.csv")):
                hd_df = pd.read_csv(os.path.join(DATA_DIR, "historical_demand.csv"))
                hd_df.to_sql("HistoricalDemand", conn, if_exists="replace", index=False)
                
            conn.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        conn.close()

def save_shipments(shipments_df):
    """Save optimized shipment plan to the Shipments table in SQLite."""
    if shipments_df is None or shipments_df.empty:
        return
    conn = get_connection()
    try:
        df_to_save = shipments_df.copy()
        if 'Units Shipped' in df_to_save.columns:
            df_to_save.rename(columns={'Units Shipped': 'UnitsShipped'}, inplace=True)
        # Drop columns that don't match table schema cleanly or ensure they exist
        cols_to_keep = ['RunID', 'Warehouse', 'Customer', 'UnitsShipped', 'UnitCost', 'RouteCost', 'Timestamp']
        if 'TruckTrips' in df_to_save.columns:
            cols_to_keep.append('TruckTrips')
        if 'ExplainabilityRationale' in df_to_save.columns:
            cols_to_keep.append('ExplainabilityRationale')
        
        df_to_save = df_to_save[[c for c in cols_to_keep if c in df_to_save.columns]]
        df_to_save.to_sql("Shipments", conn, if_exists="append", index=False)
    except Exception as e:
        print(f"Error saving shipments: {e}")
    finally:
        conn.close()

def execute_sql_query(query: str):
    """Execute arbitrary SELECT SQL queries and return results as DataFrame along with any error message."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn)
        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def get_table_data(table_name: str):
    """Fetch all rows from a specified table."""
    conn = get_connection()
    try:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

# =====================================================================
# ADVANCED SQL ANALYTICS QUERIES (Maersk Portfolio Flaw #8)
# =====================================================================
def get_shipment_history(run_id: str = None) -> pd.DataFrame:
    """Retrieves full historical audit trail of MILP optimization runs."""
    conn = get_connection()
    try:
        query = """
            SELECT RunID, Warehouse, Customer, UnitsShipped, UnitCost, RouteCost, 
                   COALESCE(TruckTrips, 1) as TruckTrips,
                   COALESCE(ExplainabilityRationale, 'Standard allocation') as Rationale,
                   Timestamp
            FROM Shipments
            ORDER BY id DESC LIMIT 100
        """
        if run_id:
            query = f"SELECT * FROM Shipments WHERE RunID = '{run_id}' ORDER BY id DESC"
        return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"SQL Error in get_shipment_history: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_warehouse_analytics() -> pd.DataFrame:
    """Aggregates total volume dispatched, total freight spend, and average route cost per warehouse hub."""
    conn = get_connection()
    try:
        query = """
            SELECT 
                w.Warehouse,
                w.Capacity as Max_Hub_Capacity,
                COALESCE(SUM(s.UnitsShipped), 0) as Total_Units_Dispatched,
                COALESCE(SUM(s.RouteCost), 0.0) as Total_Freight_Spend_INR,
                COALESCE(SUM(s.TruckTrips), 0) as Total_Truck_Trips_Assigned,
                ROUND(COALESCE(AVG(s.UnitCost), 0.0), 2) as Avg_Unit_Transport_Rate
            FROM Warehouses w
            LEFT JOIN Shipments s ON w.Warehouse = s.Warehouse
            GROUP BY w.Warehouse
            ORDER BY Total_Freight_Spend_INR DESC
        """
        return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"SQL Error in get_warehouse_analytics: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_monthly_cost_reports() -> pd.DataFrame:
    """Generates time-series financial aggregation of transportation burn by month."""
    conn = get_connection()
    try:
        query = """
            SELECT 
                SUBSTR(Timestamp, 1, 7) as Month_Period,
                COUNT(DISTINCT RunID) as Total_Optimization_Runs,
                SUM(UnitsShipped) as Monthly_TEUs_Moved,
                SUM(COALESCE(TruckTrips, 1)) as Total_Fleet_Dispatches,
                ROUND(SUM(RouteCost), 2) as Monthly_Total_Transport_Cost_INR,
                ROUND(AVG(RouteCost), 2) as Average_Route_Spend_INR
            FROM Shipments
            WHERE Timestamp IS NOT NULL
            GROUP BY SUBSTR(Timestamp, 1, 7)
            ORDER BY Month_Period DESC
        """
        return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"SQL Error in get_monthly_cost_reports: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_route_performance() -> pd.DataFrame:
    """Analyzes O-D pairwise corridor frequency, unit cost consistency, and volume throughput."""
    conn = get_connection()
    try:
        query = """
            SELECT 
                Warehouse as Origin_Hub,
                Customer as Destination_Node,
                COUNT(*) as Dispatch_Frequency,
                SUM(UnitsShipped) as Cumulative_TEUs_Moved,
                SUM(COALESCE(TruckTrips, 1)) as Total_Truck_Trips,
                ROUND(AVG(UnitCost), 2) as Mean_Unit_Freight_Rate_INR,
                ROUND(SUM(RouteCost), 2) as Total_Corridor_Spend_INR
            FROM Shipments
            GROUP BY Warehouse, Customer
            ORDER BY Cumulative_TEUs_Moved DESC
        """
        return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"SQL Error in get_route_performance: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialization and seeding complete.")
