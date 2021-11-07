#!/usr/bin/env python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

# Si devono definire i turni settimanali per un ospedale. Un infermiere lavora 5 giorni consecutivi per poi avere 2 giorni liberi.
# Ogni giorno c'è bisogno di una disponibilità di infermieri indicata in tabella.
# Minimizzare numero totale di infermieri da assumere

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
demand = {"Monday":17,"Tuesday":13,"Wednesday":15,"Thursday":19,"Friday":14,"Saturday":16,"Sunday":11}
CONSECUTIVE_DAYS = 5
FREE_DAYS = 2

# Numero totale infermieri è dato da numero infermiere assunti in giorno i
def obj_rule(model):
    return sum(model.x[i] for i in model.days)

# infermieri disponibili giorno i >= richiesta di infermieri per giorno i
# infermieri assunti giorno i + assunti giorno i-1 + ... + assunti giorno i-4 >= richiesta giorno i ((i+j+2)%6 con j da 0 a 4)
def constr_rule(model, i):
    idx = days.index(i)
    allowed = [days[d] for d in [(idx+j+FREE_DAYS)%(CONSECUTIVE_DAYS+FREE_DAYS-1) for j in range(CONSECUTIVE_DAYS)]]
    return sum(model.x[p] for p in model.x if p in allowed) >= model.demand[i]

def buildmodel():
    model = ConcreteModel()
    # Set
    model.days = Set(initialize = days)
    # Param
    model.demand = Param(model.days, initialize=demand)
    # Variables
    model.x = Var(model.days, domain=NonNegativeIntegers)
    # Objective
    model.obj = Objective(rule=obj_rule, sense=minimize)
    # Constraints
    model.constrs = Constraint(model.days, rule=constr_rule)
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