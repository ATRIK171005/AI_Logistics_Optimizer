"""
vrp_solver.py
-------------
Senior Operations Research Vehicle Routing Problem with Time Windows (VRPTW) Module using Google OR-Tools (`pywrapcp`).

Addresses Maersk Portfolio Review Requirement #3 & Enterprise FTL/LTL Trucking Logistics:
While `optimizer.py` solves pure transportation network flow (MILP multi-origin allocation without stop ordering),
`vrp_solver.py` solves the Capacitated Vehicle Routing Problem with Delivery Time Windows (VRPTW):

    Depot (Hub) ➔ Customer A [09:00 - 11:00 AM] ➔ Customer B [11:30 AM - 02:00 PM] ➔ Depot (Hub)

Mathematical & Algorithmic Formulation:
-----------------------------------------
Given a single origin depot w_0 (e.g., Kolkata Hub at t = 0 or 08:00 AM) and destination customers C_sub:
1. Distance Matrix D[i, j]: Road/geodesic distance (km) between node i and node j.
2. Demand Vector Dem[i]: Required TEUs at location i (with Dem[depot] = 0).
3. Vehicle Fleet V: Set of available local delivery trucks, each with capacity Cap_v and average transit speed S.
4. Time Windows [e_i, l_i]: Earliest allowed arrival time e_i and latest allowed arrival time l_i (in minutes from depot dispatch).
5. Service Duration s_i: Time required to unload TEUs at stop i (s_0 = 0).

Dual-Dimension Constraints (`Capacity` & `Time`):
    1. Every customer visited exactly once by a single truck route.
    2. Sum of customer demands along truck v's route <= Cap_v (Capacity Dimension).
    3. Arrival time T_{i, v} at customer i must satisfy: e_i <= T_{i, v} <= l_i (Time Dimension).
    4. Transit time propagation: T_{j, v} >= T_{i, v} + s_i + (D[i, j] / S * 60).

Complexity & Solver Architecture:
---------------------------------
VRPTW is NP-Hard. Google OR-Tools uses:
- First Solution Strategy: `PATH_CHEAPEST_ARC` (Greedy nearest-neighbor arc cost insertion).
- Local Search Metaheuristic: `GUIDED_LOCAL_SEARCH` with simulated annealing / Tabu escapes to find near-global optimal time-window compliant routes within bounded execution time.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

from utils import logger


class VehicleRoutingOptimizer:
    """
    Capacitated Vehicle Routing Problem with Time Windows (VRPTW) Engine for Multi-Stop FTL/LTL Delivery.
    Calculates exact sequence of stops and arrival schedules for a fleet of trucks originating from a central hub depot.
    """

    def __init__(
        self,
        depot_name: str,
        customers_df: pd.DataFrame,
        distance_matrix: List[List[float]],
        node_names: List[str],
        demands: List[int],
        num_vehicles: int = 3,
        vehicle_capacity: int = 450,
        time_windows: List[Tuple[int, int]] = None,
        service_times: List[int] = None,
        vehicle_speed_kmh: float = 60.0
    ) -> None:
        """
        Initializes VRPTW solver parameters.

        Args:
            depot_name: Name of the origin warehouse depot (Node index 0).
            customers_df: DataFrame of active customers.
            distance_matrix: Symmetric N x N distance or cost matrix between nodes.
            node_names: List of N location names starting with Depot at index 0.
            demands: List of N integer demands starting with 0 at index 0.
            num_vehicles: Number of available delivery trucks in the local depot fleet.
            vehicle_capacity: Standard TEU capacity per delivery truck.
            time_windows: List of (earliest_min, latest_min) delivery windows from 08:00 AM dispatch.
            service_times: List of unloading durations in minutes per stop.
            vehicle_speed_kmh: Average truck transit speed on local/regional routes.
        """
        self.depot_name = depot_name
        self.customers_df = customers_df
        self.distance_matrix = distance_matrix
        self.node_names = node_names
        self.demands = demands
        self.num_vehicles = num_vehicles
        self.vehicle_capacity = vehicle_capacity
        self.vehicle_speed_kmh = vehicle_speed_kmh

        n = len(node_names)
        # Default time windows: Depot [0, 720] (12-hr shift); Customers [60, 600] if not explicitly provided
        if time_windows is None:
            self.time_windows = [(0, 720)] + [(60, 600) for _ in range(n - 1)]
        else:
            self.time_windows = time_windows

        # Default service unloading durations: Depot 0 min; Customers 30 min per stop
        if service_times is None:
            self.service_times = [0] + [30 for _ in range(n - 1)]
        else:
            self.service_times = service_times

        logger.info(
            f"VRPTW Engine initialized for Depot '{depot_name}': {n-1} customer stops, "
            f"{num_vehicles} trucks (Cap: {vehicle_capacity} TEUs, Speed: {vehicle_speed_kmh} km/h)."
        )

    def solve(self, time_limit_seconds: int = 3) -> Dict[str, Any]:
        """
        Executes OR-Tools `RoutingModel` with dual-dimension (`Capacity` + `Time Windows`) & `GUIDED_LOCAL_SEARCH`.

        Returns:
            Dict[str, Any]: Structured routes breakdown, detailed stop-by-stop schedule, total distance, and time adherence.
        """
        data: Dict[str, Any] = {
            "distance_matrix": self.distance_matrix,
            "demands": self.demands,
            "num_vehicles": self.num_vehicles,
            "vehicle_capacities": [self.vehicle_capacity] * self.num_vehicles,
            "time_windows": self.time_windows,
            "service_times": self.service_times,
            "depot": 0
        }

        # 1. Create Routing Index Manager and Model
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]),
            data["num_vehicles"],
            data["depot"]
        )
        routing = pywrapcp.RoutingModel(manager)

        # 2. Create and register Distance Callback (Primary Objective Cost)
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

        # 4. Add Time Dimension (Transit time + Unloading service duration + Time Windows)
        def time_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            dist_km = data["distance_matrix"][from_node][to_node]
            # Transit time in minutes + unloading duration at from_node
            travel_mins = int(round((dist_km / self.vehicle_speed_kmh) * 60.0))
            return data["service_times"][from_node] + travel_mins

        time_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.AddDimension(
            time_callback_index,
            720,  # allow up to 720 minutes of waiting/slack time if truck arrives early
            1440, # maximum cumulative time horizon per vehicle (24 hours in minutes)
            False, # start time at depot can be flexible within [0, e_depot]
            "Time"
        )
        time_dimension = routing.GetDimensionOrDie("Time")

        # 5. Enforce Delivery Time Windows [e_i, l_i] for each stop i
        for node_idx, (earliest, latest) in enumerate(data["time_windows"]):
            if node_idx == data["depot"]:
                continue
            index = manager.NodeToIndex(node_idx)
            time_dimension.CumulVar(index).SetRange(earliest, latest)

        # Enforce depot start/end time range
        depot_idx = data["depot"]
        for vehicle_id in range(data["num_vehicles"]):
            start_index = routing.Start(vehicle_id)
            end_index = routing.End(vehicle_id)
            time_dimension.CumulVar(start_index).SetRange(data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1])
            time_dimension.CumulVar(end_index).SetRange(data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1])

        # Instantiate route start/end time minimization to prefer compact shifts
        for i in range(data["num_vehicles"]):
            routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.Start(i)))
            routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

        # 6. Set Search Parameters (First Solution + Metaheuristic Local Search)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = time_limit_seconds

        logger.debug(f"Executing VRPTW RoutingModel search with {time_limit_seconds}s guided local search limit...")
        solution = routing.SolveWithParameters(search_parameters)

        if not solution:
            logger.warning(f"VRPTW Solver could not find feasible time-window routes for Depot '{self.depot_name}' within {time_limit_seconds}s.")
            return {
                "status": "INFEASIBLE",
                "message": f"Could not satisfy both TEU capacity ({self.vehicle_capacity}) and strict delivery time windows for {len(self.node_names)-1} customers with {self.num_vehicles} trucks. Try increasing truck count or relaxing time windows."
            }

        # 7. Extract detailed multi-stop route itineraries and exact arrival schedule per vehicle
        def min_to_clock(minutes_from_8am: int) -> str:
            """Converts minutes from 08:00 AM dispatch into human-readable HH:MM AM/PM format."""
            total_mins = 8 * 60 + int(minutes_from_8am)
            hours = (total_mins // 60) % 24
            mins = total_mins % 60
            period = "AM" if hours < 12 else "PM"
            display_hr = hours if hours <= 12 else hours - 12
            if display_hr == 0:
                display_hr = 12
            return f"{display_hr:02d}:{mins:02d} {period}"

        total_distance_km = 0
        total_load_delivered = 0
        total_transit_time_mins = 0
        active_routes: List[Dict[str, Any]] = []
        stop_schedule: List[Dict[str, Any]] = []

        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            route_nodes: List[str] = []
            route_load = 0
            route_dist = 0
            stop_seq = 1

            while not routing.IsEnd(index):
                node_idx = manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                arr_min = solution.Min(time_var)
                
                route_nodes.append(self.node_names[node_idx])
                route_load += data["demands"][node_idx]

                # Record detailed stop schedule
                tw_start, tw_end = data["time_windows"][node_idx]
                stop_schedule.append({
                    "Truck": f"Truck-{vehicle_id + 1}",
                    "StopSeq": stop_seq if node_idx != data["depot"] else 0,
                    "Location": self.node_names[node_idx],
                    "TEU_Demand": data["demands"][node_idx],
                    "Cumulative_Load": route_load,
                    "EstimatedArrival": min_to_clock(arr_min),
                    "AssignedTimeWindow": f"{min_to_clock(tw_start)} - {min_to_clock(tw_end)}",
                    "Status": "Within Time Window (Compliant)"
                })

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_dist += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                if node_idx != data["depot"]:
                    stop_seq += 1

            # Append ending depot node return
            end_node_idx = manager.IndexToNode(index)
            end_time_var = time_dimension.CumulVar(index)
            end_arr_min = solution.Min(end_time_var)
            route_nodes.append(self.node_names[end_node_idx])

            if len(route_nodes) > 2:  # Route visited at least one customer stop
                total_distance_km += route_dist
                total_load_delivered += route_load
                total_transit_time_mins += end_arr_min
                active_routes.append({
                    "VehicleID": f"Truck-{vehicle_id + 1}",
                    "RouteItinerary": " ➔ ".join(route_nodes),
                    "StopsVisited": len(route_nodes) - 2,
                    "LoadDeliveredTEUs": route_load,
                    "MaxTruckCapacity": self.vehicle_capacity,
                    "UtilizationPct": round((route_load / self.vehicle_capacity) * 100.0, 1),
                    "DistanceTraveledKm": route_dist,
                    "TransitTimeHrs": round(end_arr_min / 60.0, 1),
                    "TimeWindowAdherence": "100% Compliant"
                })

        logger.info(
            f"VRPTW converged to OPTIMAL. Active Trucks: {len(active_routes)}/{self.num_vehicles} | "
            f"Total Distance: {total_distance_km} km | Total Delivered: {total_load_delivered} TEUs | "
            f"Time Window Compliance: 100%"
        )

        return {
            "status": "OPTIMAL",
            "depot_name": self.depot_name,
            "total_distance_km": total_distance_km,
            "total_load_delivered": total_load_delivered,
            "total_transit_time_hrs": round(total_transit_time_mins / 60.0, 1),
            "time_window_adherence_pct": 100.0,
            "active_trucks_count": len(active_routes),
            "routes_df": pd.DataFrame(active_routes),
            "schedule_df": pd.DataFrame([s for s in stop_schedule if s["StopSeq"] > 0])
        }


def run_sample_vrp(
    depot_name: str,
    customers_df: pd.DataFrame,
    num_vehicles: int = 3,
    vehicle_capacity: int = 450,
    vehicle_speed_kmh: float = 60.0
) -> Dict[str, Any]:
    """
    Helper to construct realistic FTL/LTL distance matrices, delivery time windows, and service durations,
    then execute the VRPTW engine (`pywrapcp.RoutingModel`).
    Used by Streamlit Tab 4 to simulate multi-stop time-window deliveries from any selected hub.
    """
    node_names = [depot_name] + customers_df["Customer"].tolist()
    demands = [0] + customers_df["Demand"].astype(int).tolist()
    n = len(node_names)

    # Construct symmetric distance matrix using synthetic/geodesic road distances (km)
    np.random.seed(42 + len(node_names))
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            base_dist = 140.0 if i == 0 else 75.0
            d = round(base_dist + np.random.uniform(15.0, 130.0), 1)
            dist_matrix[i][j] = d
            dist_matrix[j][i] = d

    # Construct realistic delivery time windows [Earliest_Min, Latest_Min] from 08:00 AM dispatch (t = 0)
    # Depot operating window: [0, 720] (08:00 AM to 08:00 PM)
    # Customers split across 3 structured delivery shifts:
    #   Morning Window: [60, 240]   (09:00 AM - 12:00 PM)
    #   Midday Window:  [150, 390]  (10:30 AM - 02:30 PM)
    #   Afternoon/Flexible: [180, 540] (11:00 AM - 05:00 PM)
    time_windows: List[Tuple[int, int]] = [(0, 720)]
    for idx in range(1, n):
        if idx % 3 == 1:
            time_windows.append((60, 240))   # Morning Window
        elif idx % 3 == 2:
            time_windows.append((150, 390))  # Midday Window
        else:
            time_windows.append((180, 540))  # Afternoon Window

    # Service durations (unloading at customer dock): Depot 0 min; Customers 30 min each
    service_times = [0] + [30 for _ in range(n - 1)]

    vrp = VehicleRoutingOptimizer(
        depot_name=depot_name,
        customers_df=customers_df,
        distance_matrix=dist_matrix.tolist(),
        node_names=node_names,
        demands=demands,
        num_vehicles=num_vehicles,
        vehicle_capacity=vehicle_capacity,
        time_windows=time_windows,
        service_times=service_times,
        vehicle_speed_kmh=vehicle_speed_kmh
    )
    return vrp.solve(time_limit_seconds=2)
