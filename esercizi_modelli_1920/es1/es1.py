#!/usr/bin/python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

flaconi = ["1", "2", "3"]
essenze = ["rosa", "mughetto", "limone"]
costo = {"1": 90, "2": 120, "3": 170}
ore = {"1": 20, "2": 16, "3": 12}
produzione = {"1": {"rosa": 100, "mughetto": 110, "limone": 320}, "2": {"rosa": 120, "mughetto": 290, "limone": 210}, "3": {"rosa": 160, "mughetto": 330, "limone": 130}}
richiesta = {"rosa": 10000, "mughetto": 5000, "limone": 8000}
TOTAL_TIME = 1500
SET_UP_TIME = 8
FIXED_COST = 20
# ogni ordine per un tipo diverso di flaconi costa 20€
# si vogliono acquistare flaconi di almeno 2 tipi

def demandRule(model, j):
    return sum(model.produzione[i,j]*model.x[i] for i in model.flaconi) >= model.richiesta[j]

def timeRule(model):
    return sum(model.SET_ for i in model.flaconi) <= model.TOTAL_TIME

def buildModel():
    model = ConcreteModel()
    # SETS
    model.flaconi = Set(initialize=flaconi)
    model.essenze = Set(initialize=essenze)
    # PARAM
    model.costo = Param(model.flaconi, initialize=costo)
    model.ore = Param(model.flaconi, initialize=ore)
    model.richiesta = Param(model.essenze, initialize=richiesta)
    model.produzione = Param(model.flaconi, model.essenze, initialize=lambda model,f,e:produzione[f][e])
    model.TOTAL_TIME = Param(initialize=TOTAL_TIME)
    model.SET_UP_TIME = Param(initialize=SET_UP_TIME)
    model.FIXED_COST = Param(initialize=FIXED_COST)
    # VARIABLES
    model.x = Var(model.flaconi, domain=NonNegativeIntegers)
    model.y = Var(model.flaconi, domain=Boolean)
    # OBJECTIVE FUNCTION
    model.obj = Objective(expr=sum(model.FIXED_COST*model.y[i]+model.costo[i]*model.x[i] for i in model.flaconi), sense=minimize)
    # CONSTRAINTS
    # fixed cost constr
    model.fixed_cost_cst1 = Constraint(model.flaconi, rule=lambda model,i:model.x[i]<=1E8*model.y[i])
    model.fixed_cost_cst2 = Constraint(model.flaconi, rule=lambda model,i:model.x[i]>=model.y[i])
    # demand constr
    model.demand_cst = Constraint(model.essenze, rule=demandRule)
    # time constr
    model.time_cst = Constraint(expr=sum(model.SET_UP_TIME*model.y[i]+model.ore[i]*model.x[i] for i in model.flaconi) <= model.TOTAL_TIME)
    # at least 2 different types of bottles constr
    model.different_types_cst = Constraint(expr=sum(model.y[i] for i in model.flaconi) >= 2)
    return model

if __name__ == '__main__':
    model = buildModel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    model.display()
    print("==============================================================")
    for p in model.x:
        print("# flaconi acquistati di tipo {} = {}".format(p, value(model.x[p])))