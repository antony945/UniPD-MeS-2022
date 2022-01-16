#!/usr/bin/python
# encoding: utf-8
from pyomo.environ import *
from pyomo.opt import SolverFactory

# SETS
investimenti = ["1", "2", "3", "4", "5", "6", "7"]
# PARAMETERS
profitto = {"1": 17, "2": 10, "3": 15, "4": 19, "5": 7, "6": 13, "7": 9}
capitale_richiesto = {"1": 43, "2": 28, "3": 34, "4": 48, "5": 17, "6": 32, "7": 23}
CAPITALE_TOTALE = 100
#################################################################################

def buildModel():
    model = ConcreteModel()
    # SETS
    model.investimenti = Set(initialize=investimenti)
    # PARAMETERS
    model.profitto = Param(model.investimenti, initialize=profitto)
    model.capitale_richiesto = Param(model.investimenti, initialize=capitale_richiesto)
    model.CAPITALE_TOTALE = Param(initialize=CAPITALE_TOTALE)
    # VARIABLES
    # ho effettuato/non ho effettuato investimento i
    model.x = Var(model.investimenti, domain=Binary)
    # OBJECTIVE FUNCTION
    # massimizzare profitto totale
    model.obj = Objective(expr=sum(model.profitto[i]*model.x[i] for i in model.investimenti), sense=maximize)
    # CONSTRAINTS
    # vincolo su capitale a disposizione
    model.capital_cst = Constraint(expr=sum(model.capitale_richiesto[i]*model.x[i] for i in model.investimenti) <= model.CAPITALE_TOTALE)
    # invest. 1 e 2 sono mutualmente esclusivi
    model.cst_1 = Constraint(expr=model.x["1"]+model.x["2"]<=1)
    # invest. 3 e 4 sono mutualmente esclusivi
    model.cst_2 = Constraint(expr=model.x["3"]+model.x["4"]<=1)
    # invest. 3 (o 4) non possono essere fatti se non è stato fatto invest. 1 (o 2)
    model.cst_1 = Constraint(expr=model.x["3"]+model.x["4"]<=model.x["1"]+model.x["2"])
    return model

if __name__ == '__main__':
    model = buildModel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    model.display()
    print("====================================================")
    # Print variables
    for p in model.x:
        print("x[{}] = {}".format(p, value(model.x[p])))