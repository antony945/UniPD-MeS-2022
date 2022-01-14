#!/usr/bin/python
# encoding: utf-8
from pyomo.environ import *
from pyomo.opt import SolverFactory

# SETS
tipo = ["A", "B", "C", "D"]
pezzi = ["sottopattini", "bulloni", "perni"]
confezioni = ["1", "2"]
# PARAMETERS
richiesta = {"A": {"sottopattini": 2, "bulloni": 10, "perni": 20},
            "B": {"sottopattini": 4, "bulloni": 12, "perni": 25},
            "C": {"sottopattini": 0, "bulloni": 5, "perni": 30},
            "D": {"sottopattini": 0, "bulloni": 9, "perni": 25}}
costo_manodopera = {"A": 25, "B": 20, "C": 35, "D": 30}
contenuto = {"1": {"sottopattini": 5, "bulloni": 30, "perni": 70},
            "2": {"sottopattini": 7, "bulloni": 45, "perni": 90}}
costo_confezione = {"1": 20, "2": 25}
SCONTO_CONF1 = 500
MIN_CONF1_X_SCONTO = 200
TIPO_MEZZI_CIRCOLANTI = 3
MIN_MEZZI_TOTALI = 1200
AIUTANTI_BABBONATALE = 600
AIUTANTI_BEFANA = 900
#################################################################################

def buildModel():
    model = ConcreteModel()
    # SETS
    model.tipo = Set(initialize=tipo)
    model.pezzi = Set(initialize=pezzi)
    model.confezioni = Set(initialize=confezioni)
    # PARAMETERS
    model.richiesta = Param(model.tipo, model.pezzi, initialize=lambda model,t,p:richiesta[t][p])
    model.costo_manodopera = Param(model.tipo, initialize=costo_manodopera)
    model.contenuto = Param(model.confezioni, model.pezzi, initialize=lambda model,t,p:contenuto[t][p])
    model.costo_confezione = Param(model.confezioni, initialize=costo_confezione)
    # VARIABLES
    # numero di mezzi di tipo t da utilizzare
    model.x = Var(model.tipo, domain=NonNegativeIntegers)
    # vale 1 se utilizzo almeno 1 mezzo di tipo t
    model.w = Var(model.tipo, domain=Binary)
    model.w_cst1 = Constraint(model.tipo, rule=lambda model,t:model.x[t] <= 1E8*model.w[t])
    model.w_cst2 = Constraint(model.tipo, rule=lambda model,t:model.x[t] >= model.w[t])
    # numero di confezioni di tipo c da comprare
    model.y = Var(model.confezioni, domain=NonNegativeIntegers)
    # vale 1 se ho comprato almeno MIN_CONF1_X_SCONTO confezioni 1
    model.z = Var(domain=Binary)
    model.z_cst1 = Constraint(expr=model.y["1"] <= (MIN_CONF1_X_SCONTO-1) + 1E8*model.z)
    model.z_cst2 = Constraint(expr=model.y["1"] >= MIN_CONF1_X_SCONTO*model.z)
    # OBJECTIVE FUNCTION
    # minimizzare costi di manutenzione (ricambio e manodopera)
    model.obj = Objective(expr=sum(model.costo_manodopera[t]*model.x[t] for t in model.tipo)+sum(model.costo_confezione[c]*model.y[c] for c in model.confezioni)-SCONTO_CONF1*model.z, sense=minimize)
    # CONSTRAINTS
    # possono circolare esattamente TIPO_MEZZI_CIRCOLANTI tipi di mezzi
    model.c1 = Constraint(expr=sum(model.w[t] for t in model.tipo) == TIPO_MEZZI_CIRCOLANTI)
    # somma di slitte deve essere <= aiutanti babbo natale
    model.c2 = Constraint(expr=model.x["A"]+model.x["B"] <= AIUTANTI_BABBONATALE)
    # somma di scope deve essere <= aiutanti befana
    model.c3 = Constraint(expr=model.x["C"]+model.x["D"] <= AIUTANTI_BEFANA)
    # somma di mezzi totali in giro deve essere >= MIN_MEZZI_TOTALI
    model.c4 = Constraint(expr=sum(model.x[t] for t in model.tipo) >= MIN_MEZZI_TOTALI)
    # bisogna soddisfare richiesta di pezzi
    model.c5 = Constraint(model.pezzi, rule=lambda model,p:sum(model.y[c]*model.contenuto[c,p] for c in model.confezioni) >= sum(model.x[t]*model.richiesta[t,p] for t in model.tipo)) 
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