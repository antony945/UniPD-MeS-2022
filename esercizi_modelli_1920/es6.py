#!/usr/bin/python
# encoding: utf-8
from pyomo.environ import *
from pyomo.opt import SolverFactory

# SETS
forma = ["cuore", "fiore", "stella", "chicco"]
gusto = ["latte", "fondente", "caffe"]
stabilimento = ["1", "2", "3"]
# PARAMETERS
disponibilita = {"latte": {"cuore": 1, "fiore": 1, "stella": 0, "chicco": 0},
                 "fondente": {"cuore": 1, "fiore": 0, "stella": 1, "chicco": 0},
                 "caffe": {"cuore": 0, "fiore": 1, "stella": 1, "chicco": 1}}
richiesta_minima = {"latte": {"1": 500, "2": 100, "3": 100},
                    "fondente": {"1": 100, "2": 500, "3": 100},
                    "caffe": {"1": 100, "2": 100, "3": 500}}

praline_per_confezione = {"cuore": 70, "fiore": 50, "stella": 100, "chicco": 200}
costo_per_confezione = {"latte": 30, "fondente": 50, "caffe": 40}
CIOCCOLATO_TOTALE = 900
SET_UP_COST = 200
MINIMO_CONF_CUORI_FONDENTI = 10
MINIMO_FORME = 3
COSTO_SE_NON_FORNISCO = 15000
peso_per_pralina = {"cuore": 30, "fiore": 50, "stella": 20, "chicco": 10}
#################################################################################

def buildModel():
    model = ConcreteModel()
    # SETS
    model.gusto = Set(initialize=gusto)
    model.forma = Set(initialize=forma)
    model.stabilimento = Set(initialize=stabilimento)
    # PARAMETERS
    model.disponibilita_conf = Param(model.gusto, model.forma, initialize=lambda model,g,f:disponibilita[g][f])
    model.richiesta_min = Param(model.gusto, model.stabilimento, initialize=lambda model,g,s:richiesta_minima[g][s])
    model.num_praline_conf = Param(model.forma, initialize=praline_per_confezione)
    model.costo_conf = Param(model.gusto, initialize=costo_per_confezione)
    model.peso_pral = Param(model.forma, initialize=peso_per_pralina)
    model.CIOCCOLATO_TOT = Param(initialize=CIOCCOLATO_TOTALE)
    model.SET_UP_COST = Param(initialize=SET_UP_COST)
    # VARIABLES
    # x[g,f] sono il numero di confezioni acquistate di gusto g e forma f
    model.x = Var(model.gusto, model.forma, domain=NonNegativeIntegers)
    # y[f] è var. binaria che dice se ho comprato o meno confezioni di forma f
    model.y = Var(model.forma, domain=Binary)
    model.y_cst1 = Constraint(model.forma, rule=lambda model,f:sum(model.x[g,f] for g in model.gusto) <= 1E8*model.y[f])
    model.y_cst2 = Constraint(model.forma, rule=lambda model,f:sum(model.x[g,f] for g in model.gusto) >= model.y[f])
    # z è var. binaria che dice se ho rifornito tutti e 3 (z=0) o solo 2 stabilimenti (z=1)
    model.z = Var(domain=Binary)
    model.z_cst1 = Constraint(expr=0==0)
    model.z_cst2 = Constraint(expr=0==0)
    # OBJECTIVE FUNCTION
    # devo minimizzare costo complessivo confezioni
    model.obj = Objective(expr=sum(model.x[g,f]*model.costo_conf[g] for g,f in model.gusto, model.forma) + model.SET_UP_COST*sum(model.y[f] for f in model.forma) + model.z*COSTO_SE_NON_FORNISCO, sense=minimize)
    # CONSTRAINTS
    # vincolo su peso 
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