#!/usr/bin/env python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

# Sets
products = ["gas", "chloride"]
components = ["nitrogen", "hydrogen", "chlorine"]

# Data
demand = {"gas": {"nitrogen": 1, "hydrogen": 3, "chlorine": 0}, "chloride": {"nitrogen": 1, "hydrogen": 4, "chlorine": 1}}
profit = {"gas": 40, "chloride": 50}
stock = {"nitrogen": 50, "hydrogen": 180, "chlorine": 40}

# Initialize data
def init_demand(model, p, c):
    return demand[p][c]
def init_profit(model, p):
    return profit[p]
def init_stock(model, c):
    return stock[c]

# Define rule for objective function
def obj_rule(model):
    return sum(model.profit[p]*model.x[p] for p in model.products)

# Define rule for constraints
def constr_rule(model, c):
    return sum(model.demand[p,c]*model.x[p] for p in model.products) <= stock[c]

# Build concrete model
def buildmodel():
    # Model
    model = ConcreteModel()
    # Sets
    model.products = Set(initialize=products)
    model.components = Set(initialize=components)
    # Param
    model.demand = Param(model.products, model.components, initialize=init_demand)
    model.profit = Param(model.products, initialize=init_profit)
    model.stock = Param(model.components, initialize=init_stock)
    # Variables
    model.x = Var(model.products, domain=NonNegativeReals)
    # Objective
    model.obj = Objective(rule = obj_rule, sense = maximize)
    # Constraints
    model.constrs = Constraint(model.components, rule = constr_rule)
    return model

if __name__ == '__main__':
    # Define model
    model = buildmodel()
    # Define solver
    opt = SolverFactory('glpk')
    # Solve model
    res = opt.solve(model)
    res.write()
    if res.solver.status:
        model.display()
    # Print variables values
    print("==================================================================================")
    for p in model.x:
        print("x[{}] = {}".format(p, value(model.x[p])))