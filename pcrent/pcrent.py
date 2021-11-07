#!/usr/bin/env python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

# Azienda deve affittare un certo numero di pc secondo certi fabbisogni mensili. Può affittarli per uno, due o tre mesi con i prezzi indicati.
# Trovare politica di affitto che minimizza il costo complessivo.

# Costo complessivo è dato da prodotto prezzi*numero computer acquistati in mese i per durata j
def obj_rule(model):
    return sum(sum(model.prices[j]*model.x[i,j] for j in model.duration) for i in model.months)

# Numero di pc disponibili a mese i >= richiesta di pc per mese i
# pc disponibil a mese i = pc affittati in mese i per ogni durata j + pc di mese i-1 con durate a partire da j+1 + pc di mese i-2 con durate a partire da j+2
def constr_rule(model, i):
    # define months list
    m = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    # get index of current month
    idx = m.index(i)
    if i == "gennaio":
        return sum(model.x[i,j] for j in model.duration) >= model.demand[i]
    elif i == "febbraio":
        return sum(model.x[i,j] for j in model.duration) + sum(model.x[m[idx-1],j] for j in model.duration if not j=="1month") >= model.demand[i]
    else:
        return sum(model.x[i,j] for j in model.duration) + sum(model.x[m[idx-1],j] for j in model.duration if not j=="1month") + sum(model.x[m[idx-2],j] for j in model.duration if not(j=="1month" or j=="2months")) >= model.demand[i]

def buildmodel():
    model = AbstractModel()
    # Set
    model.months = Set()
    model.duration = Set()
    # Param
    model.demand = Param(model.months)
    model.prices = Param(model.duration)
    # Variables
    model.x = Var(model.months, model.duration, domain=NonNegativeIntegers)
    # Objective
    model.obj = Objective(rule=obj_rule, sense=minimize)
    # Constraints
    model.constrs = Constraint(model.months, rule=constr_rule)
    return model

if __name__ == '__main__':
    import sys
    model = buildmodel()
    opt = SolverFactory('glpk')
    instance = model.create_instance(sys.argv[1])
    res = opt.solve(instance)
    res.write()
    print("==========================================================================")
    instance.display()
    print("==========================================================================")
    for p in instance.x:
        print("x[{}] = {}".format(p, value(instance.x[p])))