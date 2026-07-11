import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd

def plot_logistics_network(shipments_df, warehouses_df, customers_df):
    """Render an interactive directed bipartite network graph of the logistics network using NetworkX and Plotly."""
    G = nx.DiGraph()
    
    # Add Warehouse Nodes (Layer 0 on X axis)
    pos = {}
    w_list = warehouses_df['Warehouse'].tolist()
    for idx, w in enumerate(w_list):
        cap = int(warehouses_df.loc[warehouses_df['Warehouse']==w, 'Capacity'].values[0])
        G.add_node(w, node_type="Warehouse", capacity=cap)
        pos[w] = (0.15, 0.85 - (idx * 0.7 / max(1, len(w_list)-1)))

    # Add Customer Nodes (Layer 1 on X axis)
    c_list = customers_df['Customer'].tolist()
    for idx, c in enumerate(c_list):
        dem = int(customers_df.loc[customers_df['Customer']==c, 'Demand'].values[0])
        G.add_node(c, node_type="Customer", demand=dem)
        pos[c] = (0.85, 0.85 - (idx * 0.7 / max(1, len(c_list)-1)))

    # Add Directed Edges from optimal shipments
    if not shipments_df.empty:
        for _, row in shipments_df.iterrows():
            G.add_edge(row['Warehouse'], row['Customer'], units=row['UnitsShipped'], cost=row['RouteCost'])

    # Build Plotly traces for edges
    edge_traces = []
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        units = data.get('units', 0)
        cost = data.get('cost', 0.0)
        
        # Line width scales dynamically between 2 and 9 based on units
        width = max(2.0, min(9.0, units / 35.0))
        
        edge_trace = go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=width, color='#00E5FF'),
            hoverinfo='text',
            text=f"<b>Route: {u} ➔ {v}</b><br>Units Shipped: <b>{units}</b><br>Route Cost: ₹{cost:,.2f}",
            mode='lines'
        )
        edge_traces.append(edge_trace)

    # Build Plotly trace for nodes
    node_x, node_y, node_text, node_color, node_symbol = [], [], [], [], []
    for node, data in G.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        if data['node_type'] == 'Warehouse':
            node_text.append(f"<b>🏢 {node} (Warehouse)</b><br>Max Capacity: {data['capacity']} Units")
            node_color.append('#0088FF')
            node_symbol.append('square')
        else:
            node_text.append(f"<b>🛒 {node} (Customer)</b><br>Required Demand: {data['demand']} Units")
            node_color.append('#FFB300')
            node_symbol.append('circle')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[n for n in G.nodes()],
        textposition="top center",
        textfont=dict(color="white", size=14, family="Inter, Arial"),
        hovertext=node_text,
        marker=dict(showscale=False, color=node_color, size=30, symbol=node_symbol, line=dict(width=2.5, color='white'))
    )

    fig = go.Figure(data=edge_traces + [node_trace],
                 layout=go.Layout(
                    title=dict(text="<b>🌐 Optimized Bipartite Network Flow Map</b>", font=dict(size=18, color="white")),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=30, l=30, r=30, t=50),
                    paper_bgcolor='rgba(0,36,61,0.25)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.0, 1.0]),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.0, 1.0])
                 ))
    return fig

def plot_warehouse_utilization(util_df):
    """Generate stacked bar chart showing Shipped vs Remaining Capacity for each warehouse."""
    fig = px.bar(
        util_df, x='Warehouse', y=['Units Shipped', 'Remaining Capacity'],
        title="<b>🏢 Warehouse Capacity Utilization</b>",
        labels={'value': 'Units', 'variable': 'Status'},
        color_discrete_map={'Units Shipped': '#00E5FF', 'Remaining Capacity': '#1E3A5F'},
        barmode='stack',
        text_auto=True
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"), legend_title_text="Status",
        xaxis=dict(title="Warehouse Location"), yaxis=dict(title="Total Capacity (Units)")
    )
    return fig

def plot_cost_breakdown(shipments_df):
    """Generate sunburst chart illustrating transportation cost breakdown across routes."""
    if shipments_df.empty:
        return go.Figure()
    fig = px.sunburst(
        shipments_df, path=['Warehouse', 'Customer'], values='RouteCost',
        title="<b>💰 Transportation Cost Breakdown by Route (₹)</b>",
        color='RouteCost', color_continuous_scale='Blues'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"),
        margin=dict(t=40, l=10, r=10, b=10)
    )
    return fig

def plot_demand_comparison(base_df, ai_df):
    """Generate side-by-side grouped bar chart comparing Base vs AI Forecasted Demand."""
    merged = pd.merge(base_df, ai_df, on='Customer', suffixes=('_Base', '_Forecast'))
    df_melted = merged.melt(id_vars=['Customer'], value_vars=['Demand_Base', 'Demand_Forecast'],
                            var_name='Scenario', value_name='Units')
    df_melted['Scenario'] = df_melted['Scenario'].map({'Demand_Base': 'Base Scenario', 'Demand_Forecast': 'AI Forecasted Next Month'})
    
    fig = px.bar(
        df_melted, x='Customer', y='Units', color='Scenario',
        title="<b>📊 Base Demand vs AI Forecasted Next Month Demand</b>",
        barmode='group', text_auto=True,
        color_discrete_map={'Base Scenario': '#8E9AAF', 'AI Forecasted Next Month': '#00E5FF'}
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"), xaxis_title="Customer City", yaxis_title="Demand Units"
    )
    return fig
