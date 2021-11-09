#!/usr/bin/python
# encoding: utf-8

porte = ["standard", "lusso"]
fasi = ["assemblaggio", "verniciatura"]

prod_max = {"standard": 500, "lusso": 300}
ricavo = {"standard": 300, "lusso": 400}
operai = {"assemblaggio": 20, "verniciatura": 30}
tempo = {"standard": {"assemblaggio": 2, "verniciatura": 3}, "lusso": {"assemblaggio": 4, "verniciatura": 5}}
WEEK_WORK = 40
# porte di lusso <= 1/2(portelusso + standard)

from pyomo.environ import *
from pyomo.opt import SolverFactory

def c2_rule(model, f):
    return sum(model.tempo[p,f]*model.x[p] for p in model.porte) <= WEEK_WORK*model.operai[f]

def buildmodel():
    model = ConcreteModel()
    # Set
    model.porte = Set(initialize=porte)
    model.fasi = Set(initialize=fasi)
    # Param
    model.prod_max = Param(model.porte, initialize=prod_max)
    model.ricavo = Param(model.porte, initialize=ricavo)
    model.operai = Param(model.fasi, initialize=operai)
    model.tempo = Param(model.porte, model.fasi, initialize=lambda model,d,p:tempo[d][p])
    model.WEEK_WORK = Param(initialize=40)
    # Var
    model.x = Var(model.porte, domain=NonNegativeIntegers, bounds=lambda model,p:(0,model.prod_max[p]))
    # Obj
    model.obj = Objective(expr=sum(model.ricavo[p]*model.x[p] for p in model.porte), sense=maximize)
    # Constraints
    model.c1 = Constraint(expr=model.x["lusso"] <= 1/2*sum(model.x[p] for p in model.porte))
    model.c2 = Constraint(model.fasi, rule=c2_rule)
    return model

if __name__ == '__main__':
    # opt = SolverFactory('cplex_persistent')
    # opt.set_instance(model)
    # res = opt.solve(tee=False)
    model = buildmodel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    model.display()
    print("=====================================================")
    for p in model.x:
        print("x[{}] = {}".format(p, value(model.x[p])))