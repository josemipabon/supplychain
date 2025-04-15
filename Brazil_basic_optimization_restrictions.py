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

# Output results
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("Total transportation cost =", value(prob.objective))
