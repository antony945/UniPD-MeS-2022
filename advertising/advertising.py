#!/usr/bin/env python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

BUDGET = 150000
media = ["tv", "paper"]
ranges = [1, 2, 3]
prices = {"tv": 10000, "paper": 1000}
maxAds = {"tv": 15, "paper": 30} # non necessario, informazione già in adsForRange
audience = {"tv": {1: 10000, 2: 5000, 3: 2000}, "paper": {1: 900, 2: 600, 3: 300}}
adsForRange = {"tv": {1: 5, 2: 5, 3: 5}, "paper": {1: 10, 2: 10, 3: 10}}

# f(x) = numero di persone totali raggiunte
# somma di persone raggiunte con annuncio in fascia j su mezzo i * numero di annunci in fascia j su mezzo i
def obj_rule(model):
    return sum(sum(model.audience[i,j]*model.x[i,j] for j in model.ranges) for i in model.media)

# soldi spesi devono essere minori di budget totale
# soldi spesi = numero di annunci in fascia j su mezzo i * prezzo annuncio in fascia j su mezzo i
def budget_rule(model):
    return sum(model.prices[i]*sum(model.x[i,j] for j in model.ranges) for i in model.media) <= model.budget

# numero di annunci per fascia è limitato ad un certo numero
def constr_rule(model, i, j):
    return model.x[i,j] <= model.adsForRange[i,j]

def init_audience(model, i, j):
    return audience[i][j]

def init_adsForRange(model, i, j):
    return adsForRange[i][j]

def buildmodel():
    model = ConcreteModel()
    # SET
    model.media = Set(initialize=media)
    model.ranges = Set(initialize=ranges)
    # PARAM
    model.budget = Param(initialize=BUDGET)
    model.prices = Param(model.media, initialize=prices)
    model.audience = Param(model.media, model.ranges, initialize=init_audience)
    model.adsForRange = Param(model.media, model.ranges, initialize=init_adsForRange)
    # VAR
    # x_ij indica numero di annunci da fare in fascia j di mezzo i
    model.x = Var(model.media, model.ranges, domain=NonNegativeIntegers)
    # OBJECTIVE
    model.obj = Objective(rule=obj_rule, sense=maximize)
    # CONSTRAINTS
    # vincolo sul budget
    model.c1 = Constraint(rule=budget_rule)
    model.c2 = Constraint(model.media, model.ranges, rule=constr_rule)
    return model

if __name__ == '__main__':
    model = buildmodel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    res.write()
    model.display()
    for p in model.x:
        print("x[{}] = {}".format(p, value(model.x[p])))