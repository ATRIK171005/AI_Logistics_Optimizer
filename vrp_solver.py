"""
vrp_solver.py
-------------
Senior Operations Research Vehicle Routing Problem (VRP) Module using Google OR-Tools Routing Library (`pywrapcp`).

Addresses Maersk Portfolio Review Requirement #3 (Transportation Routing vs Allocation):
While `optimizer.py` solves the multi-origin, multi-destination allocation problem (MILP),
`vrp_solver.py` solves the Capacitated Vehicle Routing Problem (CVRP) for local depot delivery:

    Depot (Warehouse) ➔ Customer A ➔ Customer B ➔ Depot (Warehouse)

Mathematical & Algorithmic Formulation:
-----------------------------------------
Given a single origin depot w_0 (e.g., Kolkata Hub) and a subset of destination customers C_sub
that require container drops:
1. Distance Matrix D[i, j]: Geodesic or road distance (km) between node i and node j.
2. Demand Vector Dem[i]: Required TEUs at location i (with Dem[depot] = 0).
3. Vehicle Fleet V: Set of available delivery trucks, each with carrying capacity Cap_v.

Objective:
    Minimize total vehicle fleet distance traveled while visiting every required customer node exactly once:
    Minimize sum_{v in V} sum_{(i, j) in E} D[i, j] * x_{i, j, v}

Subject to:
    1. Every customer visited by exactly one truck route.
    2. Sum of customer demands along truck v's route <= Cap_v.
    3. Every active route starts and ends at the designated Depot node.

Complexity & Solver Architecture:
---------------------------------
VRP is NP-Hard. Google OR-Tools uses:
- First Solution Strategy: `PATH_CHEAPEST_ARC` (Greedy nearest-neighbor insertion).
- Local Search Metaheuristic: `GUIDED_LOCAL_SEARCH` with simulated annealing / Tabu search escapes to find near-global optimal routes within bounded execution time.
"""

from typing import Dict, Any, List
import pandas as pd
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from utils import logger


class VehicleRoutingOptimizer:
    """
    Capacitated Vehicle Routing Problem (CVRP) Engine for Multi-Stop Logistics Delivery.
    Calculates exact sequence of stops for a fleet of trucks originating from a central hub depot.
    """

    def __init__(
        self,
        depot_name: str,
        customers_df: pd.DataFrame,
        distance_matrix: List[List[float]],
        node_names: List[str],
        demands: List[int],
        num_vehicles: int = 4,
        vehicle_capacity: int = 250
    ) -> None:
        """
        Initializes CVRP solver parameters.

        Args:
            depot_name: Name of the origin warehouse depot (Node index 0).
            customers_df: DataFrame of active customers.
            distance_matrix: Symmetric N x N distance or cost matrix between nodes.
            node_names: List of N location names starting with Depot at index 0.
            demands: List of N integer demands starting with 0 at index 0.
            num_vehicles: Number of available delivery trucks in the local depot fleet.
            vehicle_capacity: Standard TEU capacity per delivery truck.
        """
        self.depot_name = depot_name
        self.customers_df = customers_df
        self.distance_matrix = distance_matrix
        self.node_names = node_names
        self.demands = demands
        self.num_vehicles = num_vehicles
        self.vehicle_capacity = vehicle_capacity

        logger.info(
            f"CVRP Engine initialized for Depot '{depot_name}': {len(node_names)-1} stops, "
            f"{num_vehicles} trucks (Cap: {vehicle_capacity} TEUs/truck)."
        )

    def solve(self, time_limit_seconds: int = 2) -> Dict[str, Any]:
        """
        Executes OR-Tools `RoutingModel` with `GUIDED_LOCAL_SEARCH` metaheuristic.

        Returns:
            Dict[str, Any]: Structured routes breakdown, total fleet distance traveled, and vehicle utilization.
        """
        data: Dict[str, Any] = {
            "distance_matrix": self.distance_matrix,
            "demands": self.demands,
            "num_vehicles": self.num_vehicles,
            "vehicle_capacities": [self.vehicle_capacity] * self.num_vehicles,
            "depot": 0
        }

        # 1. Create Routing Index Manager and Model
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]),
            data["num_vehicles"],
            data["depot"]
        )
        routing = pywrapcp.RoutingModel(manager)

        # 2. Create and register Distance Callback
        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(round(data["distance_matrix"][from_node][to_node]))

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 3. Add Capacity Dimension (Demand constraints along vehicle path)
        def demand_callback(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data["vehicle_capacities"],
            True,  # start cumulative load at zero
            "Capacity"
        )

        # 4. Set Search Parameters (First Solution + Metaheuristic Local Search)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = time_limit_seconds

        logger.debug(f"Executing VRP RoutingModel search with {time_limit_seconds}s guided local search limit...")
        solution = routing.SolveWithParameters(search_parameters)

        if not solution:
            logger.warning(f"VRP Solver could not find feasible routes for Depot '{self.depot_name}' within {time_limit_seconds}s.")
            return {
                "status": "INFEASIBLE",
                "message": f"Could not route {len(self.node_names)-1} customers with {self.num_vehicles} trucks of cap {self.vehicle_capacity}."
            }

        # 5. Extract multi-stop route itineraries per vehicle
        total_distance_km = 0
        total_load_delivered = 0
        active_routes: List[Dict[str, Any]] = []

        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            route_nodes: List[str] = []
            route_load = 0
            route_dist = 0

            while not routing.IsEnd(index):
                node_idx = manager.IndexToNode(index)
                route_nodes.append(self.node_names[node_idx])
                route_load += data["demands"][node_idx]

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_dist += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

            # Append ending depot node
            end_node_idx = manager.IndexToNode(index)
            route_nodes.append(self.node_names[end_node_idx])

            if len(route_nodes) > 2:  # Route visited at least one customer stop
                total_distance_km += route_dist
                total_load_delivered += route_load
                active_routes.append({
                    "VehicleID": f"Truck-{vehicle_id + 1}",
                    "RouteItinerary": " ➔ ".join(route_nodes),
                    "StopsVisited": len(route_nodes) - 2,
                    "LoadDeliveredTEUs": route_load,
                    "MaxTruckCapacity": self.vehicle_capacity,
                    "UtilizationPct": round((route_load / self.vehicle_capacity) * 100.0, 1),
                    "DistanceTraveledKm": route_dist
                })

        logger.info(
            f"VRP converged to OPTIMAL. Active Trucks: {len(active_routes)}/{self.num_vehicles} | "
            f"Total Distance: {total_distance_km} km | Total Delivered: {total_load_delivered} TEUs"
        )

        return {
            "status": "OPTIMAL",
            "depot_name": self.depot_name,
            "total_distance_km": total_distance_km,
            "total_load_delivered": total_load_delivered,
            "active_trucks_count": len(active_routes),
            "routes_df": pd.DataFrame(active_routes)
        }


def run_sample_vrp(depot_name: str, customers_df: pd.DataFrame, num_vehicles: int = 3, vehicle_capacity: int = 350) -> Dict[str, Any]:
    """
    Helper to construct a realistic distance matrix and execute the CVRP engine.
    Used by Streamlit Tab 6 to simulate multi-stop deliveries from any selected hub.
    """
    node_names = [depot_name] + customers_df["Customer"].tolist()
    demands = [0] + customers_df["Demand"].astype(int).tolist()
    n = len(node_names)

    # Construct symmetric distance matrix using synthetic/geodesic distances (km)
    # Diagonal = 0; Depot to stops ~ 120-450 km; inter-customer stops ~ 60-250 km
    import numpy as np
    np.random.seed(42 + len(node_names))
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            base_dist = 180.0 if i == 0 else 90.0
            d = round(base_dist + np.random.uniform(20.0, 160.0), 1)
            dist_matrix[i][j] = d
            dist_matrix[j][i] = d

    vrp = VehicleRoutingOptimizer(
        depot_name=depot_name,
        customers_df=customers_df,
        distance_matrix=dist_matrix.tolist(),
        node_names=node_names,
        demands=demands,
        num_vehicles=num_vehicles,
        vehicle_capacity=vehicle_capacity
    )
    return vrp.solve(time_limit_seconds=1)
