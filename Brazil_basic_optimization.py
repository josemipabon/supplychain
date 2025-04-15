from pulp import *

# Nodes
sources = ["BR", "W"]  # BR = Brazil, W = Warehouse
destinations = ["DE", "PL", "RO"]  # DE = Germany, PL = Poland, RO = Romania

# Supply from Brazil and the warehouse
supply = {
    "BR": 5000,
    "W": 0  # The warehouse only redistributes, it doesn't produce
}

# Factory demands
demand = {
    "DE": 1500,
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

# Create the optimization problem
prob = LpProblem("Distribution_From_Brazil", LpMinimize)

# Possible routes
routes = [(s, d) for (s, d) in costs.keys()]

# Decision variables
vars = LpVariable.dicts("Route", (sources, destinations + ["W"]), 0, None, LpInteger)

# Objective function
prob += lpSum([vars[s][d] * costs[(s, d)] for (s, d) in routes]), "Total_Transportation_Cost"

# Supply constraints
for s in sources:
    prob += lpSum([vars[s][d] for d in destinations + ["W"] if (s, d) in routes]) <= supply[s], f"Supply_{s}"

# Demand constraints
for d in destinations:
    prob += lpSum([vars[s][d] for s in sources if (s, d) in routes]) >= demand[d], f"Demand_{d}"

# Warehouse flow constraint: what enters the warehouse must leave
prob += lpSum([vars["BR"]["W"]]) == lpSum([vars["W"][d] for d in destinations if ("W", d) in routes]), "Warehouse_Flow"

# Solve the problem
prob.solve()

# Display results
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("Total transportation cost =", value(prob.objective))
