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
        # Rename column to match table schema if needed
        df_to_save = shipments_df.copy()
        if 'Units Shipped' in df_to_save.columns:
            df_to_save.rename(columns={'Units Shipped': 'UnitsShipped'}, inplace=True)
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

if __name__ == "__main__":
    init_db()
    print("Database initialization and seeding complete.")
