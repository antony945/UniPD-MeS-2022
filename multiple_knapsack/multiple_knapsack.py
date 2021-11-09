#!/usr/bin/env python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

objects = [1,2,3,4,5,6,7]
containers = [1,2,3]
weights = {1: 500, 2: 396, 3: 195, 4: 660, 5: 600, 6: 195, 7: 660}
profits = {1: 294, 2: 93, 3: 96, 4: 155, 5: 294, 6: 96, 7: 155}
CAPACITY = 884

# x_ij = 1 se prendo oggetto i nel contenitore j

def obj_rule(model):
    return sum(sum(model.profits[i]*model.x[i,j] for j in model.containers) for i in model.objects)

def weight_rule(model, j):
    return sum(model.weights[i]*model.x[i,j] for i in model.objects) <= model.CAPACITY

def object_rule(model, i): # oggetto può stare in massimo un contenitore
    return sum(model.x[i,j] for j in model.containers) <= 1

def buildmodel():
    model = ConcreteModel()
    # SET
    model.objects = Set(initialize=objects)
    model.containers = Set(initialize=containers)
    # PARAM
    model.weights = Param(model.objects, initialize=weights)
    model.profits = Param(model.objects, initialize=profits)
    model.CAPACITY = Param(initialize=CAPACITY)
    # VAR
    model.x = Var(model.objects, model.containers, domain=Boolean)
    # OBJ
    model.obj = Objective(rule=obj_rule, sense=maximize)
    # CONSTRS
    model.weight_constr = Constraint(model.containers, rule=weight_rule)
    model.object_constr = Constraint(model.objects, rule=object_rule)
    return model

if __name__ == '__main__':
    model = buildmodel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    model.display()
    print("=====================================================")
    for i,j in model.x:
        if not (value(model.x[i,j] == 0.0)):
            print("oggetto {} in contenitore {}".format(i,j))