#!/usr/bin/python
# encoding: utf-8
from pyomo.environ import *
from pyomo.opt import SolverFactory

# SETS
prodotti = ["1", "2", "3", "4"]
benzine = ["A", "B", "C"]
# PARAMETERS
disponibilita = {"1": 3000, "2": 2000, "3": 4000, "4": 1000}
costo = {"1": 3, "2": 6, "3": 4, "4": 5}
lower_bound_miscela = {"A": {"1": 0, "2": 0.4, "3": 0, "4": 0},
                        "B": {"1": 0, "2": 0.1, "3": 0, "4": 0},
                        "C": {"1": 0.7, "2": 0, "3": 0, "4": 0}}
upper_bound_miscela = {"A": {"1": 0.3, "2": 1, "3": 0.5, "4": 1},
                        "B": {"1": 0.5, "2": 1, "3": 1, "4": 1},
                        "C": {"1": 1, "2": 1, "3": 1, "4": 1}}
ricavo = {"A": 5.5, "B": 4.5, "C": 3.5}
#################################################################################

def buildModel():
    model = ConcreteModel()
    # SETS
    model.prodotti = Set(initialize=prodotti)
    model.benzine = Set(initialize=benzine)
    # PARAMETERS
    model.disp = Param(model.prodotti, initialize=disponibilita)
    model.costo = Param(model.prodotti, initialize=costo)
    model.lb = Param(model.benzine, model.prodotti, initialize=lambda model,b,p:lower_bound_miscela[b][p])
    model.ub = Param(model.benzine, model.prodotti, initialize=lambda model,b,p:upper_bound_miscela[b][p])
    model.ricavo = Param(model.benzine, initialize=ricavo)
    # VARIABLES
    # qta di prodotto p usato per benzina b
    model.x = Var(model.benzine, model.prodotti, domain=NonNegativeReals)
    # quanto prodotto di tipo p produco
    model.y = Var(model.benzine, domain=NonNegativeReals)
    # OBJECTIVE FUNCTION
    # massimizzare profitto
    model.obj = Objective(expr=sum(model.ricavo[b]*model.y[b] - sum(model.costo[p]*model.x[b,p] for p in model.prodotti) for b in model.benzine), sense=maximize)
    # CONSTRAINTS
    # vincolo di coerenza
    model.coherence_cst = Constraint(model.benzine, rule=lambda model,b:sum(model.x[b,p] for p in model.prodotti) == model.y[b])
    # vincolo su disponibilità per ogni prodotto p
    model.disp_cst = Constraint(model.prodotti, rule=lambda model,p:sum(model.x[b,p] for b in model.benzine) <=model.disp[p])
    # vincolo su composizione delle benzine
    model.lb_cst = Constraint(model.benzine, model.prodotti, rule=lambda model,b,p:model.x[b,p] >= model.lb[b,p]*model.y[b])
    model.ub_cst = Constraint(model.benzine, model.prodotti, rule=lambda model,b,p:model.x[b,p] <= model.ub[b,p]*model.y[b])    
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