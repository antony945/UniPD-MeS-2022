#!/usr/bin/env/python
#encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

weeks = ["1", "2", "3", "4"]
profit = {"1": 20, "2": 18, "3": 16, "4": 14}
RADIO_COST = 2
NORMAL_SALARY = 200
APPRENTICE_SALARY = 100
LEARNING_PERIOD = 1
WEEK_RADIO = 50
INITIAL_WORKERS = 40
MINIMUM_RADIO = 20000
MAX_APPRENTICE_FOR_TEACHER = 3

def obj_rule(model): # profitto radio * radio prodotte - costo dipendenti
    return sum((model.profit[i]-RADIO_COST)*WEEK_RADIO*model.executors[i] - NORMAL_SALARY*(model.executors[i]+model.teachers[i]) - APPRENTICE_SALARY*model.apprentices[i] for i in model.weeks)

def radio_rule(model): # radio prodotte > MINIMUM_RADIO
    return sum(WEEK_RADIO*model.executors[i] for i in model.weeks) >= MINIMUM_RADIO

def teacher_rule(model, i): # ogni insegnante ha al massimo MAX_APPRENTICE_FOR_TEACHER apprendisti
    return model.apprentices[i] <= 3*model.teachers[i]

def consistency_rule(model, i): # numero di lavoratori settimanale deve essere consistente
    weeks = ["1", "2", "3", "4"]
    return (model.executors[i]+model.teachers[i] == INITIAL_WORKERS+sum(model.apprentices[k] for k in model.weeks if weeks.index(k)<weeks.index(i)))

def buildmodel():
    model = ConcreteModel()
    # SET
    model.weeks = Set(initialize=weeks)
    # PARAM
    model.profit = Param(model.weeks, initialize=profit)
    model.RADIO_COST = Param(initialize=RADIO_COST)
    model.NORMAL_SALARY = Param(initialize=NORMAL_SALARY)
    model.APPRENTICE_SALARY = Param(initialize=APPRENTICE_SALARY)
    model.LEARNING_PERIOD = Param(initialize=LEARNING_PERIOD)
    model.MINIMUM_RADIO = Param(initialize=MINIMUM_RADIO)
    model.MAX_APPRENTICE_FOR_TEACHER = Param(initialize=MAX_APPRENTICE_FOR_TEACHER)
    # VAR
    model.executors = Var(model.weeks, domain=NonNegativeIntegers)
    model.teachers = Var(model.weeks, domain=NonNegativeIntegers)
    model.apprentices = Var(model.weeks, domain=NonNegativeIntegers)
    # OBJECTIVE
    model.obj = Objective(rule=obj_rule, sense=maximize)
    # CONSTRAINT
    model.c1 = Constraint(rule=radio_rule)
    model.c2 = Constraint(model.weeks, rule=teacher_rule)
    model.c3 = Constraint(model.weeks, rule=consistency_rule)
    return model

if __name__ == '__main__':
    model = buildmodel()
    # opt = SolverFactory('cplex_persistent')
    # opt.set_instance(model)
    # res = opt.solve(tee=True)
    opt = SolverFactory('glpk')
    res = opt.solve(model)
    res.write()
    print("====================================================================")
    model.display()
    print("====================================================================")
    for x,y,z in zip(model.executors, model.teachers, model.apprentices):
        print("executors[week{}] = {}".format(x, value(model.executors[x])))
        print("teachers[week{}] = {}".format(y, value(model.teachers[y])))
        print("apprentices[week{}] = {}".format(z, value(model.apprentices[z])))
        print("----------------------------------------------------------------")