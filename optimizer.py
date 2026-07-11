from ortools.linear_solver import pywraplp
import pandas as pd
import uuid
from datetime import datetime

class LogisticsOptimizer:
    def __init__(self, warehouses_df, customers_df, cost_df, trucks_df):
        self.warehouses_df = warehouses_df
        self.customers_df = customers_df
        self.cost_df = cost_df
        self.trucks_df = trucks_df
        self.solver = pywraplp.Solver.CreateSolver('GLOP')

    def solve(self):
        """Build and solve the linear programming network optimization model using Google OR-Tools."""
        if not self.solver:
            return {
                "status": "ERROR",
                "message": "Could not create GLOP Linear Solver. Please ensure ortools is installed properly."
            }

        # Clear any previous variables or constraints
        self.solver.Clear()

        # Extract data mappings
        warehouses = self.warehouses_df['Warehouse'].tolist()
        capacities = dict(zip(self.warehouses_df['Warehouse'], self.warehouses_df['Capacity']))
        
        customers = self.customers_df['Customer'].tolist()
        demands = dict(zip(self.customers_df['Customer'], self.customers_df['Demand']))
        
        # Build pairwise cost dictionary: (warehouse, customer) -> cost
        costs = {}
        for _, row in self.cost_df.iterrows():
            costs[(row['Warehouse'], row['Customer'])] = float(row['Cost'])

        total_truck_capacity = float(self.trucks_df['Capacity'].sum()) if not self.trucks_df.empty else 999999.0
        total_demand = sum(demands.values())
        total_wh_capacity = sum(capacities.values())

        # Pre-check feasibility
        if total_demand > total_wh_capacity:
            return {
                "status": "INFEASIBLE",
                "message": f"Infeasible network: Total required customer demand ({total_demand}) exceeds total warehouse capacity ({total_wh_capacity})."
            }
        if total_demand > total_truck_capacity:
            return {
                "status": "INFEASIBLE",
                "message": f"Infeasible network: Total required customer demand ({total_demand}) exceeds total available truck fleet capacity ({total_truck_capacity})."
            }

        # 1. Decision Variables x[w, c]: units shipped from warehouse w to customer c
        x = {}
        for w in warehouses:
            for c in customers:
                x[w, c] = self.solver.NumVar(0, self.solver.infinity(), f"x_{w}_{c}")

        # 2. Objective Function: Minimize Total Transportation Cost
        objective = self.solver.Objective()
        for w in warehouses:
            for c in customers:
                unit_cost = costs.get((w, c), 9999.0)  # High penalty if route missing
                objective.SetCoefficient(x[w, c], unit_cost)
        objective.SetMinimization()

        # 3. Constraints
        # Constraint A: Warehouse Capacity Limit
        for w in warehouses:
            constraint = self.solver.Constraint(0, capacities[w], f"Warehouse_Cap_{w}")
            for c in customers:
                constraint.SetCoefficient(x[w, c], 1.0)

        # Constraint B: Customer Demand Fulfillment (Exact demand required)
        for c in customers:
            constraint = self.solver.Constraint(demands[c], demands[c], f"Customer_Demand_{c}")
            for w in warehouses:
                constraint.SetCoefficient(x[w, c], 1.0)

        # Constraint C: Total Truck Fleet Capacity Limit across all shipments
        fleet_constraint = self.solver.Constraint(0, total_truck_capacity, "Fleet_Capacity_Limit")
        for w in warehouses:
            for c in customers:
                fleet_constraint.SetCoefficient(x[w, c], 1.0)

        # Solve the Linear Program
        status = self.solver.Solve()

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            run_id = f"RUN-{str(uuid.uuid4())[:8].upper()}"
            shipments = []
            total_cost = float(self.solver.Objective().Value())
            total_units_shipped = 0

            for w in warehouses:
                for c in customers:
                    units = x[w, c].solution_value()
                    if units > 0.01:
                        units_int = int(round(units))
                        unit_cost = costs.get((w, c), 0.0)
                        route_cost = round(units_int * unit_cost, 2)
                        total_units_shipped += units_int
                        shipments.append({
                            "RunID": run_id,
                            "Warehouse": w,
                            "Customer": c,
                            "UnitsShipped": units_int,
                            "UnitCost": unit_cost,
                            "RouteCost": route_cost,
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

            # Compute Warehouse Utilization breakdown
            utilization = []
            for w in warehouses:
                shipped = sum(s['UnitsShipped'] for s in shipments if s['Warehouse'] == w)
                cap = capacities[w]
                util_pct = round((shipped / cap) * 100, 1) if cap > 0 else 0.0
                utilization.append({
                    "Warehouse": w,
                    "Max Capacity": cap,
                    "Units Shipped": shipped,
                    "Remaining Capacity": cap - shipped,
                    "Utilization %": util_pct
                })

            # Compute Customer Fulfillment check
            fulfillment = []
            for c in customers:
                received = sum(s['UnitsShipped'] for s in shipments if s['Customer'] == c)
                req = demands[c]
                fulfillment.append({
                    "Customer": c,
                    "Required Demand": req,
                    "Units Received": received,
                    "Status": "✅ Fulfilled" if received == req else f"⚠️ Short by {req - received}"
                })

            return {
                "status": "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else "FEASIBLE",
                "total_cost": round(total_cost, 2),
                "total_units_shipped": total_units_shipped,
                "shipments_df": pd.DataFrame(shipments),
                "utilization_df": pd.DataFrame(utilization),
                "fulfillment_df": pd.DataFrame(fulfillment),
                "run_id": run_id
            }
        else:
            return {
                "status": "INFEASIBLE",
                "message": "OR-Tools could not find a feasible solution under the current constraints."
            }
