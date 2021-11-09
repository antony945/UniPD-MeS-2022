#!/usr/bin/env/python
#encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

productionLines = ["1", "2", "3"]
machines = ["A", "B", "C"]
PRODUCT_PRICE = 90
productionPrice = {"1": 6, "2": 3, "3": 7}
machinesTime = {"A": 2000, "B": 3000, "C": 600}
machinesPrice = {"A": 5, "B": 4, "C": 3}
demand = {"1": {"A": 3, "B": 3, "C": 3}, "2": {"A": 2, "B": 2, "C": 2}, "3": {"A": 6, "B": 6, "C": 6}}

def obj_rule(model):
    return sum((model.PRODUCT_PRICE - model.productionPrice[i] - sum(model.x[i]*model.machinesPrice[j]*model.demand[i,j] for j in model.machines))*model.x[i] for i in model.productionLines)

def constr_rule(model, j):
    return sum(model.demand[i,j]*model.x[i] for i in model.productionLines) <= model.machinesTime[j]

def buildmodel():
    model = ConcreteModel()
    # SET
    model.productionLines = Set(initialize=productionLines)
    model.machines = Set(initialize=machines)
    # PARAM
    model.PRODUCT_PRICE = Param(initialize=PRODUCT_PRICE)
    model.productionPrice = Param(model.productionLines, initialize=productionPrice)
    model.machinesTime = Param(model.machines, initialize=machinesTime)
    model.machinesPrice = Param(model.machines, initialize=machinesPrice)
    model.demand = Param(model.productionLines, model.machines, initialize=lambda model,i,j: demand[i][j])
    # VAR
    model.x = Var(model.productionLines, domain=NonNegativeIntegers)
    # OBJECTIVE
    model.obj = Objective(rule=obj_rule, sense=maximize)
    # CONSTRAINT
    model.constrs = Constraint(model.machines, rule=constr_rule)
    return model

if __name__ == '__main__':
    model = buildmodel()
    opt = SolverFactory('cplex_persistent')
    opt.set_instance(model)
    res = opt.solve(tee=True)
    # opt = SolverFactory('glpk')
    # res = opt.solve(model)
    # res.write()
    print("====================================================================")
    model.display()
    print("====================================================================")
    for p in model.x:
        print("x[{}] = {}".format(p, value(model.x[p])))