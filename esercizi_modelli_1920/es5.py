#!/usr/bin/python
# encoding: utf-8
from pyomo.environ import *
from pyomo.opt import SolverFactory

# SETS
investimento = ["A", "B", "C", "D"]
mesi = ["Aprile", "Maggio", "Giugno", "Luglio"]
# PARAMETERS
BUDGET = 100000
OBIETTIVO = 150000
durata_mesi = {"A": 1, "B": 2, "C": 3, "D": 1}
rendimento = {"A": 0.1, "B": 0.19, "C": 0.33, "D": 0.15}
rischio = {"A": 2, "B": 3, "C": 5, "D": 4}

#################################################################################

def buildModel():
    model = ConcreteModel()
    # SETS
    model.investments = Set(initialize=investimento)
    model.months = Set(initialize=mesi)
    # PARAMETERS
    model.duration = Param(model.investments, initialize=durata_mesi)
    model.efficiency = Param(model.investments, initialize=rendimento)
    model.risk = Param(model.investments, initialize=rischio)
    model.BUDGET = Param(initialize=BUDGET)
    model.GOAL = Param(initialize=OBIETTIVO)    
    # VARIABLES
    model.x = Var(model.investments, model.months, domain = NonNegativeIntegers)
    model.invested = Var(model.months, domain = NonNegativeIntegers)
    model.earned = Var(model.months, domain = NonNegativeReals)
    model.capital = Var(model.months, domain = NonNegativeReals)
    model.y = Var(model.investments, model.months, domain = Binary)
    # y is 1 if x > 0, 0 if x = 0
    model.y_cst1 = Constraint(model.investments, model.months, rule=lambda model,i,j:model.x[i,j] <= 1E8*model.y[i,j])
    model.y_cst2 = Constraint(model.investments, model.months, rule=lambda model,i,j:model.x[i,j] >= model.y[i,j])
    # variables constraints
    model.invested_cst = Constraint(model.months, rule=lambda model,j:model.invested[j] == 1000*sum(model.x[i,j] for i in model.investments))
    model.earned_cst_April = Constraint(expr = model.earned["Aprile"] == sum((1+model.efficiency[i])*1000*model.x[i,"Aprile"] for i in model.investments if model.duration[i]==1))
    model.earned_cst_May = Constraint(expr = model.earned["Maggio"] == sum((1+model.efficiency[i])*1000*model.x[i,"Maggio"] for i in model.investments if model.duration[i]==1) +
                                                sum((1+model.efficiency[i])*1000*model.x[i,"Aprile"] for i in model.investments if model.duration[i]==2))
    model.earned_cst_June = Constraint(expr = model.earned["Giugno"] == sum((1+model.efficiency[i])*1000*model.x[i,"Giugno"] for i in model.investments if model.duration[i]==1) +
                                                sum((1+model.efficiency[i])*1000*model.x[i,"Maggio"] for i in model.investments if model.duration[i]==2) +
                                                sum((1+model.efficiency[i])*1000*model.x[i,"Aprile"] for i in model.investments if model.duration[i]==3))
    model.earned_cst_July = Constraint(expr = model.earned["Luglio"] == sum((1+model.efficiency[i])*1000*model.x[i,"Luglio"] for i in model.investments if model.duration[i]==1) +
                                                sum((1+model.efficiency[i])*1000*model.x[i,"Giugno"] for i in model.investments if model.duration[i]==2) +
                                                sum((1+model.efficiency[i])*1000*model.x[i,"Maggio"] for i in model.investments if model.duration[i]==3))
    model.capital_cst_April = Constraint(expr = model.capital["Aprile"] == model.BUDGET)
    model.capital_cst_May = Constraint(expr = model.capital["Maggio"] == model.capital["Aprile"] - model.invested["Aprile"] + model.earned["Aprile"])
    model.capital_cst_June = Constraint(expr = model.capital["Giugno"] == model.capital["Maggio"] - model.invested["Maggio"] + model.earned["Maggio"])
    model.capital_cst_July = Constraint(expr = model.capital["Luglio"] == model.capital["Giugno"] - model.invested["Giugno"] + model.earned["Giugno"])
    # model.capital_cst = Constraint(model.months, rule=lambda model,j:model.capital[j] == model.capital[j-1] - model.invested[j-1] + model.earned[j-1])
    # OBJECTIVE FUNCTION
    model.obj = Objective(expr=sum(model.risk[i]*sum(model.x[i,j] for j in model.months) for i in model.investments), sense=minimize)
    # CONSTRAINTS
    # budget monthly constraint
    model.budget_cst = Constraint(model.months, rule=lambda model,j:model.invested[j] <= model.capital[j])
    # reaching goal constraint
    model.goal_cst = Constraint(expr = model.capital["Luglio"] - model.invested["Luglio"] + model.earned["Luglio"] >= model.GOAL)
    # not possible to invest at the same time on B and C in may
    model.may_cst = Constraint(expr = model.y["B","Maggio"]+model.y["C","Maggio"] <= 1)
    # in order to invest in A in april, you must invest 10k on B (c1) and 30k on D (c2) in april
    model.c1 = Var(domain = Boolean)
    model.c1_cst1 = Constraint(expr = model.x["B","Aprile"] <= (10-1) + 1E8*model.c1)
    model.c1_cst2 = Constraint(expr = model.x["B","Aprile"] >= 10*model.c1)
    model.c2 = Var(domain = Boolean)
    model.c2_cst1 = Constraint(expr = model.x["D","Aprile"] <= (30-1) + 1E8*model.c2)
    model.c2_cst2 = Constraint(expr = model.x["D","Aprile"] >= 30*model.c2)
    # yA_April is c1 && c2
    model.and_cst1 = Constraint(expr = model.y["A","Aprile"] <= model.c1)
    model.and_cst2 = Constraint(expr = model.y["A","Aprile"] <= model.c2)
    model.and_cst3 = Constraint(expr = model.y["A","Aprile"] >= model.c1+model.c2-1)
    return model

if __name__ == '__main__':
    model = buildModel()
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    model.display()
    print("====================================================")
    # Print variables
    for j in model.months:
        print("{}\n".format(j))
        for i in model.investments:
            print("\tInvested in {} = €{}k".format(i, value(model.x[i,j])))
    print("FINAL BUDGET= €{}".format(value(model.goal_cst)))