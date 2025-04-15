from pulp import *

# Nodes
sources = ["BR", "W"]  # BR = Brazil, W = Warehouse
destinations = ["DE", "PL", "RO"]  # DE = Germany, PL = Poland, RO = Romania

# Supply from Brazil and the warehouse
supply = {
    "BR": 10000,
    "W": 0  # The warehouse only redistributes, it doesn't produce
}

# Factory demands
demand = {
    "DE": 5500,
    "PL": 2000,
    "RO": 1000
}

# Shipping costs per unit
costs = {
    ("BR", "W"): 5,
    ("BR", "DE"): 8,
    ("BR", "PL"): 7,
    ("BR", "RO"): 6,
    ("W", "DE"): 2,
    ("W", "PL"): 3,
    ("W", "RO"): 2
}

# Max capacity per shipping route
route_caps = {
    ("BR", "W"): 3000,
    ("BR", "DE"): 1000,
    ("BR", "PL"): 1500,
    ("BR", "RO"): 1200,
    ("W", "DE"): 800,
    ("W", "PL"): 1000,
    ("W", "RO"): 900
}

# Create the optimization problem
prob = LpProblem("Distribution_From_Brazil", LpMinimize)

# Possible routes
routes = [(s, d) for (s, d) in costs.keys()]

# Decision variables
vars = LpVariable.dicts("Route", (sources, destinations + ["W"]), 0, None, LpInteger)

# Objective function: minimize total transportation cost
prob += lpSum([vars[s][d] * costs[(s, d)] for (s, d) in routes]), "Total_Transportation_Cost"

# 1. Total supply limit from each source
for s in sources:
    prob += lpSum([vars[s][d] for d in destinations + ["W"] if (s, d) in routes]) <= supply[s], f"Supply_{s}"

# 2. Demand fulfillment at each destination
for d in destinations:
    prob += lpSum([vars[s][d] for s in sources if (s, d) in routes]) >= demand[d], f"Demand_{d}"

# 3. Warehouse flow conservation: what enters must leave
prob += lpSum([vars["BR"]["W"]]) == lpSum([vars["W"][d] for d in destinations if ("W", d) in routes]), "Warehouse_Flow"

# 4. Limit direct shipments from Brazil to factories
prob += (
    lpSum([vars["BR"][d] for d in destinations if ("BR", d) in routes]) <= 2000,
    "Max_Direct_Shipments_From_BR"
)

# 5. Minimum quantity routed through warehouse
prob += vars["BR"]["W"] >= 1000, "Min_Flow_Through_Warehouse"

# 6. Warehouse total capacity limit
prob += lpSum([vars["W"][d] for d in destinations if ("W", d) in routes]) <= 2500, "Warehouse_Capacity"

# 7. Route-specific capacity limits
for (s, d), cap in route_caps.items():
    prob += vars[s][d] <= cap, f"Route_Cap_{s}_{d}"

# Solve the problem
prob.solve()

################### Plot ####################

import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Node layout positions (manual for clear spacing)
positions = {
    "BR": (-2, 0),
    "W": (0, 1),
    "DE": (2, 2),
    "PL": (2, 1),
    "RO": (2, 0)
}

# Add nodes
G.add_nodes_from(positions.keys())

# Add edges with flows > 0
for (s, d) in costs.keys():
    flow = vars[s][d].varValue
    if flow is not None and flow > 0:
        G.add_edge(s, d, weight=flow)

# Draw nodes and labels
plt.figure(figsize=(10, 6))
nx.draw_networkx_nodes(G, positions, node_color='lightblue', node_size=1500)
nx.draw_networkx_labels(G, positions, font_size=12, font_weight='bold')

# Draw edges with arrows
nx.draw_networkx_edges(G, positions, arrowstyle='->', arrowsize=20, edge_color='gray')

# Add edge labels showing shipment amount
edge_labels = {(u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, positions, edge_labels=edge_labels, font_size=10)

# Show plot
plt.title("Optimal Shipping Network", fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.show()


# Output results
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("Total transportation cost =", value(prob.objective))
