#!/usr/bin/python
# encoding: utf-8
from pyomo.environ import *
from pyomo.opt import SolverFactory

# SETS
giochi = ["puzzle", "orsacchiotti", "trenini"]
destinazioni = ["Tanzania", "Kenya"]
partenze = ["1", "2", "3"]
# PARAMETERS
richieste = {"Tanzania": {"puzzle": 2500, "orsacchiotti": 3000, "trenini": 1400}, "Kenya": {"puzzle": 2100, "orsacchiotti": 2400, "trenini": 1300}}
pacchi_disponibili = {"1": 220, "2": 240, "3": 260}
contenuto_pacco = {"1": {"puzzle": 10, "orsacchiotti": 4, "trenini": 15}, "2": {"puzzle": 5, "orsacchiotti": 12, "trenini": 7}, "3": {"puzzle": 14, "orsacchiotti": 9, "trenini": 16}}
MAX_AEREI_CENTRO2 = 1
costo_fisso = {"1": 500, "2": 300, "3": 400}
costo_variabile = {"1": {"Tanzania": 10, "Kenya": 12}, "2": {"Tanzania": 15, "Kenya": 14}, "3": {"Tanzania": 5, "Kenya": 25}}
SOVRATTASSA_TANZANIA_PUZZLE = 1000
MIN_PUZZLE_TANZANIA = 500

def buildModel():
    model = ConcreteModel()
    # SETS
    model.giochi = Set(initialize=giochi)
    model.destinazioni = Set(initialize=destinazioni)
    model.partenze = Set(initialize=partenze)
    # PARAMETERS
    model.richieste = Param(model.destinazioni, model.giochi, initialize=lambda model,d,g:richieste[d][g])
    model.disponibilita = Param(model.partenze, initialize=pacchi_disponibili)
    model.contenuto = Param(model.partenze, model.giochi, initialize=lambda model,p,g:contenuto_pacco[p][g])
    model.costo_fisso = Param(model.partenze, initialize=costo_fisso)
    model.costo_variabile = Param(model.partenze, model.destinazioni, initialize=lambda model,p,d:costo_variabile[p][d])
    # VARIABLES
    # quanti pacchi mandare da partenza p a destinazione d
    model.x = Var(model.partenze, model.destinazioni, domain=NonNegativeIntegers)
    # vale 1 se ho inviato almeno un pacco da partenza p a destinazione d
    model.y = Var(model.partenze, model.destinazioni, domain=Binary)
    model.y_cst1 = Constraint(model.partenze, model.destinazioni, rule=lambda model,p,d:model.x[p,d] <= 1E8*model.y[p,d])
    model.y_cst2 = Constraint(model.partenze, model.destinazioni, rule=lambda model,p,d:model.x[p,d] >= model.y[p,d])
    # vale 1 se ho inviato meno di MIN_PUZZLE_TANZANIA in tanzania
    model.z = Var(domain=Binary)
    model.z_cst1 = Constraint(expr=sum(model.contenuto[p,"puzzle"]*model.x[p,"Tanzania"] for p in model.partenze) >= (MIN_PUZZLE_TANZANIA)*(1-model.z))
    # OBJECTIVE FUNCTION
    # minimizzare costi pacchi -> somma su tutte le partenze del costo_fisso*
    # model.obj = Objective(expr=SOVRATTASSA_TANZANIA_PUZZLE*model.z+sum(model.costo_fisso[p]*model.y[p,d] for p,d in model.partenze,model.destinazioni)+sum(model.costo_variabile[p,d]*model.x[p,d] for p,d in model.partenze,model.destinazioni), sense=minimize)
    model.obj = Objective(expr=SOVRATTASSA_TANZANIA_PUZZLE*model.z+sum(sum(model.costo_fisso[p]*model.y[p,d] + model.costo_variabile[p,d]*model.x[p,d] for d in model.destinazioni) for p in model.partenze), sense=minimize)
    
    # CONSTRAINTS
    # soddisfare richiesta di giochi per ogni destinazione e per ogni gioco
    model.demand_cst = Constraint(model.destinazioni, model.giochi, rule=lambda model,d,g:sum(model.contenuto[p,g]*model.x[p,d] for p in model.partenze) >= model.richieste[d,g])
    # non inviare più pacchi della disponibilità per ogni centro di partenza
    model.disponibility_cst = Constraint(model.partenze, rule=lambda model,p:sum(model.x[p,d] for d in model.destinazioni) <= model.disponibilita[p])
    # centro 2 ha solo 1 aereo a disposizione (o manda in tanzania o in kenya)
    model.xor_cst = Constraint(expr=sum(model.y["2",d] for d in model.destinazioni) <= MAX_AEREI_CENTRO2)
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