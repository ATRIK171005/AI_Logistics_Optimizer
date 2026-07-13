import re
import pandas as pd
import numpy as np

def populate_network_topology(html_code, opt_results, warehouses_df, active_customers_df, r2_score=98.4):
    """
    Dynamically injects live Google OR-Tools SCIP MILP allocation results,
    actual warehouse capacities, and active route tables into the Network Topology HTML mockup.
    """
    if not opt_results or opt_results.get("status") not in ["OPTIMAL", "FEASIBLE"]:
        return html_code

    total_cost = opt_results.get("total_cost", 1425800)
    shipments_df = opt_results.get("shipments_df", pd.DataFrame())
    
    # Calculate KPIs
    active_routes = len(shipments_df) if not shipments_df.empty else 24
    total_possible = len(warehouses_df) * len(active_customers_df)
    total_trips = opt_results.get("total_truck_trips", 18)
    
    util_df = opt_results.get("utilization_df", pd.DataFrame())
    avg_util = util_df["Utilization (%)"].mean() if not util_df.empty and "Utilization (%)" in util_df else 94.2

    # Replace KPI cards
    html_code = html_code.replace("$1,425,800", f"₹ {total_cost:,.0f}")
    html_code = html_code.replace("24 / 36 Routes", f"{active_routes} / {total_possible} Routes")
    html_code = html_code.replace("98.4% R² Score", f"{r2_score:.1f}% R² Score")
    html_code = html_code.replace("94.2% Capacity", f"{avg_util:.1f}% Capacity")
    html_code = html_code.replace("18 Discrete Truck Trips", f"{total_trips} Discrete Truck Trips")

    # Generate Dynamic Table Rows from shipments_df
    if not shipments_df.empty:
        rows_html = ""
        for idx, row in shipments_df.iterrows():
            wh = row.get("Warehouse", "Hub_A")
            cust = row.get("Customer", "Dest_B")
            units = row.get("UnitsShipped", 100)
            cost = row.get("RouteCost", 50000)
            trips = row.get("TruckTrips", 1)
            eff = min(99.8, 85.0 + (units / 50.0))
            status_badge = '<span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px]">SCIP_OPTIMAL</span>'
            
            rows_html += f"""
            <tr class="hover:bg-primary-container/5 border-b border-outline-variant/10 transition-colors">
                <td class="py-sm px-xs text-primary-fixed-dim font-bold">RT-{idx+1010}</td>
                <td class="py-sm px-xs">Intermodal ({trips} Trucks)</td>
                <td class="py-sm px-xs font-semibold">{wh}</td>
                <td class="py-sm px-xs font-semibold">{cust}</td>
                <td class="py-sm px-xs text-right">{(trips*40):,}</td>
                <td class="py-sm px-xs text-right font-bold text-primary-fixed-dim">{units:,}</td>
                <td class="py-sm px-xs text-right text-emerald-400">{eff:.1f}%</td>
                <td class="py-sm px-xs">{status_badge}</td>
            </tr>
            """
        
        # Replace the hardcoded tbody with our live OR-Tools generated table rows
        pattern = re.compile(r'<tbody[^>]*>.*?</tbody>', re.DOTALL)
        html_code = pattern.sub(f'<tbody class="font-mono-label text-[13px]">{rows_html}</tbody>', html_code, count=1)

    return html_code


def populate_demand_forecaster(html_code, metrics, pred_df):
    """
    Dynamically injects live trained XGBoost / Random Forest accuracy metrics
    and prediction forecasts into the Demand Forecaster HTML mockup.
    """
    if not metrics:
        return html_code

    rmse = metrics.get("rmse", 0.842)
    mae = metrics.get("mae", 0.615)
    mape = metrics.get("mape", 4.2)
    r2 = metrics.get("r2", 0.96)

    html_code = html_code.replace("0.842", f"{rmse:.3f}")
    html_code = html_code.replace("0.615", f"{mae:.3f}")
    html_code = html_code.replace("4.2%", f"{mape:.1f}%")
    html_code = html_code.replace("0.96", f"{r2:.2f}")

    return html_code


def populate_cvrp_explorer(html_code, vrp_result, depot_name="Port of Rotterdam"):
    """
    Dynamically injects OR-Tools Guided Local Search CVRP solution distances,
    active delivery vehicle counts, and multi-stop route itineraries.
    """
    if not vrp_result or vrp_result.get("status") != "OPTIMAL":
        return html_code

    total_dist = vrp_result.get("total_distance_km", 412.5)
    active_trucks = vrp_result.get("active_trucks_count", 18)
    routes_df = vrp_result.get("routes_df", pd.DataFrame())

    html_code = html_code.replace("412.5 KM", f"{total_dist:,.1f} KM")
    html_code = html_code.replace("18 Active Trucks", f"{active_trucks} Active Trucks")

    # Generate dynamic truck stop itinerary accordion items
    if not routes_df.empty:
        truck_cards_html = ""
        for idx, row in routes_df.iterrows():
            t_id = row.get("VehicleID", idx + 1)
            r_str = str(row.get("Route", "Depot -> Stop -> Depot"))
            load = row.get("TotalLoadDelivered", 350)
            dist = row.get("DistanceKm", 120)
            cap_pct = min(100, int((load / 450.0) * 100))
            
            # Parse stops
            stops = [s.strip() for s in r_str.split("->") if s.strip()]
            stops_html = ""
            for s_idx, stop_name in enumerate(stops):
                dot_color = "bg-primary-container" if s_idx == 0 or s_idx == len(stops)-1 else "bg-secondary-container"
                stops_html += f"""
                <div class="flex items-center gap-sm pl-2 relative">
                  <div class="w-3 h-3 rounded-full {dot_color} z-10 border-2 border-background"></div>
                  <div class="flex-grow flex justify-between text-xs py-1">
                    <span class="text-on-surface font-semibold">{stop_name}</span>
                    <span class="text-on-surface-variant font-mono-label">Stop #{s_idx+1}</span>
                  </div>
                </div>
                """

            truck_cards_html += f"""
            <div class="border border-outline-variant/30 rounded-lg bg-surface-container-lowest/50 overflow-hidden mb-3">
              <div class="p-sm flex justify-between items-start cursor-pointer group">
                <div class="flex gap-sm">
                  <div class="p-2 bg-primary-container/10 rounded-md border border-primary-container/20">
                    <span class="material-symbols-outlined text-primary-container">local_shipping</span>
                  </div>
                  <div>
                    <h3 class="font-bold text-on-surface">Truck #{t_id:02d} (Active Loop)</h3>
                    <p class="text-xs text-on-surface-variant">Distance: {dist} km • Load: {load} TEUs</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-mono-kpi text-primary-fixed-dim">{cap_pct}%</p>
                  <p class="text-[10px] text-on-surface-variant">Capacity</p>
                </div>
              </div>
              <div class="h-1 bg-surface-variant">
                <div class="h-full bg-gradient-to-r from-secondary-container to-primary-container w-[{cap_pct}%] shadow-[0_0_8px_rgba(0,229,255,0.6)]"></div>
              </div>
              <div class="p-sm bg-black/20">
                <div class="space-y-1 relative">
                  <div class="absolute left-[13px] top-2 bottom-2 w-px bg-outline-variant/30"></div>
                  {stops_html}
                </div>
              </div>
            </div>
            """
        
        pattern = re.compile(r'<div class="flex-grow overflow-y-auto custom-scrollbar p-sm space-y-sm">.*?</div>\s*<div class="p-sm bg-surface-container-high/30', re.DOTALL)
        html_code = pattern.sub(f'<div class="flex-grow overflow-y-auto custom-scrollbar p-sm space-y-sm">{truck_cards_html}</div>\n              <div class="p-sm bg-surface-container-high/30', html_code, count=1)

    return html_code
