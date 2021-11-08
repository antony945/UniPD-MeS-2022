#!/usr/bin/env python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

gas = ["A", "B", "C"]
components = ["1", "2", "3", "4"]
compStock = {"1": 3000, "2": 2000, "3": 4000, "4": 1000}
purchasePrices = {"1": 3, "2": 6, "3": 4, "4": 5}
sellingPrices = {"A": 5.5, "B": 4.5, "C": 3.5}
lbDemand = {"A": {"1": 0.0, "2": 0.4, "3": 0.0, "4": 0.0}, "B": {"1": 0.0, "2": 0.1, "3": 0.0, "4": 0.0}, "C": {"1": 0.7, "2": 0.0, "3": 0.0, "4": 0.0}}
ubDemand = {"A": {"1": 0.3, "2": 1.0, "3": 0.5, "4": 1.0}, "B": {"1": 0.5, "2": 1.0, "3": 1.0, "4": 1.0}, "C": {"1": 1.0, "2": 1.0, "3": 1.0, "4": 1.0}}

def init_lbDemand(model, g, c):
    return lbDemand[g][c]

def init_ubDemand(model, g, c):
    return ubDemand[g][c]

# devo decidere la quantità di benzina da produrre per ogni tipo e il modo in cui è stata prodotta (la miscela di componenti usata per ogni benzina)

def obj_rule(model): # massimizzare il ricavo = profitto - costo
    return sum(model.y[g] * (model.sellingPrices[g] - sum(model.purchasePrices[c]*model.x[g,c] for c in model.components)) for g in model.gas)

def stock_rule(model, c): # vincolo di disponibilità
    return sum(model.x[g,c] for g in model.gas) <= model.compStock[c]

def blending_rule1(model, g, c): # vincolo di miscela
    return model.lbDemand[g,c] <= model.x[g,c]

def blending_rule2(model, g, c): # vincolo di miscela
    return model.x[g,c] <= model.ubDemand[g,c]

def integrity_rule1(model, g): # vincolo di integrità
    return model.y[g] >= sum(model.x[g,c] for c in model.components)

def integrity_rule2(model, g): # vincolo di integrità
    return model.y[g] <= sum(model.x[g,c] for c in model.components)

def buildmodel():
    model = ConcreteModel()
    # Set
    model.gas = Set(initialize=gas)
    model.components = Set(initialize=components)
    # Param
    model.compStock = Param(model.components, initialize=compStock)
    model.purchasePrices = Param(model.components, initialize=purchasePrices)
    model.sellingPrices = Param(model.gas, initialize=sellingPrices)
    model.lbDemand = Param(model.gas, model.components, initialize=init_lbDemand)
    model.ubDemand = Param(model.gas, model.components, initialize=init_ubDemand)
    # Variables
    model.x = Var(model.gas, model.components, domain=NonNegativeReals)
    model.y = Var(model.gas, domain=NonNegativeReals)
    # Objective
    model.obj = Objective(rule=obj_rule, sense=maximize)
    # Constraints
    model.c1a = Constraint(model.gas, rule=integrity_rule1)
    model.c1b = Constraint(model.gas, rule=integrity_rule2)
    model.c2 = Constraint(model.components, rule=stock_rule)
    model.c3a = Constraint(model.gas, model.components, rule=blending_rule1)
    model.c3b = Constraint(model.gas, model.components, rule=blending_rule2)   
    return model

if __name__ == '__main__':
    import sys
    model = buildmodel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    res.write()
    print("==========================================================================")
    model.display()
    print("==========================================================================")
    for p in model.x:
        print("x[{}] = {}".format(p, value(model.x[p])))