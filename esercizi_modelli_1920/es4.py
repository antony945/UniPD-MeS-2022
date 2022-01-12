#!/usr/bin/python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

centri = ["1", "2", "3", "4"]
citta = ["A", "B", "C", "D"]

costo_trasporto = { "1": {"A": 4, "B": 3, "C": 2, "D": 3},
                    "2": {"A": 2, "B": 4, "C": 3, "D": 1},
                    "3": {"A": 2, "B": 3, "C": 4, "D": 5},
                    "4": {"A": 3, "B": 1, "C": 2, "D": 2}}
disponibilita_frigoriferi = {"1": 1800, "2": 3000, "3": 1800, "4": 1000}
richiesta_citta = {"A": 1000, "B": 2000, "C": 1700, "D": 1300}
COSTO_APERTURA = 1000
DOMANDA_MINIMA_X_APERTURA = 600
MINIMUM_CITIES = 2

def demandRule(model, j):
    return sum(model.produzione[i,j]*model.x[i] for i in model.flaconi) >= model.richiesta[j]

def timeRule(model):
    return sum(model.SET_ for i in model.flaconi) <= model.TOTAL_TIME

def buildModel():
    model = ConcreteModel()
    # SETS
    model.centri = Set(initialize=centri)
    model.citta = Set(initialize=citta)
    # PARAM
    model.costo_trasporto = Param(model.centri, model.citta, initialize=lambda model,i,j:costo_trasporto[i][j])
    model.disponibilita = Param(model.centri, initialize=disponibilita_frigoriferi)
    model.richiesta = Param(model.citta, initialize=richiesta_citta)
    model.MINIMUM_DEMAND = Param(initialize=DOMANDA_MINIMA_X_APERTURA)
    model.MINIMUM_CITIES = Param(initialize=MINIMUM_CITIES)
    model.FIXED_COST = Param(initialize=COSTO_APERTURA)
    # VARIABLES
    # x is number of fridge distributed from centre i to city j
    model.x = Var(model.centri, model.citta, domain=NonNegativeIntegers) 
    # y is 1 if centre4 serves city j, 0 otherwise
    model.y = Var(model.citta, domain=Boolean)
    model.y_cst1 = Constraint(model.citta, rule=lambda model,j:model.x["4",j]<=1E8*model.y[j])
    model.y_cst2 = Constraint(model.citta, rule=lambda model,j:model.x["4",j]>=model.y[j])
    # openCondition1 is 1 if centre4 serves at least 2 cities, 0 otherwise
    model.openCondition1 = Var(domain=Boolean)
    model.openCondition1_cst1 = Constraint(expr=sum(model.y[j] for j in model.citta) <= (model.MINIMUM_CITIES-1) + 1E8*model.openCondition1)
    model.openCondition1_cst2 = Constraint(expr=sum(model.y[j] for j in model.citta) >= model.MINIMUM_CITIES*model.openCondition1)
    # openCondition2 is 1 if centre4 distribuites at least 600 fridges, 0 otherwise
    model.openCondition2 = Var(domain=Boolean)
    model.openCondition2_cst1 = Constraint(expr=sum(model.x["4",j] for j in model.citta) <= (model.MINIMUM_DEMAND-1) + 1E8*model.openCondition2)
    model.openCondition2_cst2 = Constraint(expr=sum(model.x["4",j] for j in model.citta) >= model.MINIMUM_DEMAND*model.openCondition2)
    # willOpen is 1 if openCondition1&&openCondition2, 0 otherwise
    model.willOpen = Var(domain=Boolean)
    model.willOpen_cst1 = Constraint(expr = model.willOpen<=model.openCondition1)
    model.willOpen_cst2 = Constraint(expr = model.willOpen<=model.openCondition2)
    model.willOpen_cst3 = Constraint(expr = model.willOpen>=model.openCondition1+model.openCondition2-1)
    model.willOpen_cst4 = Constraint(expr=sum(model.x["4",j] for j in model.citta) <= 1E8*model.willOpen)
    model.willOpen_cst5 = Constraint(expr=sum(model.x["4",j] for j in model.citta) >= model.willOpen)
    # OBJECTIVE FUNCTION
    model.obj = Objective(expr=sum(sum(model.costo_trasporto[i,j]*model.x[i,j] for j in model.citta) for i in model.centri) + model.FIXED_COST*model.willOpen, sense=minimize)
    # CONSTRAINTS
    # cities demand constr
    model.demand_cst = Constraint(model.citta, rule=lambda model,j:sum(model.x[i,j] for i in model.centri) == model.richiesta[j])
    # centre disponibility constr
    model.disponibility_cst = Constraint(model.centri, rule=lambda model,i:sum(model.x[i,j] for j in model.citta) <= model.disponibilita[i])
    # linking constraint, if centre4 will not open, model.x[4,j] must be 0 for each city
    return model

if __name__ == '__main__':
    model = buildModel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    model.display()
    print("==============================================================")
    for i,j in model.x:
        print("FROM centro {} TO città {} = {} frigoriferi".format(i, j, value(model.x[i,j])))
    print("\nIl centro 4 apre? {}".format(value(model.willOpen)))
    print("La spesa totale e' €{} ".format(value(model.obj)))