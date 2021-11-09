#!/usr/bin/env python
# encoding: utf-8

from pyomo.environ import *
from pyomo.opt import SolverFactory

# Sets
products = ["gas", "chloride"]
components = ["nitrogen", "hydrogen", "chlorine"]


# Data
demand = {"gas": {"nitrogen": 1, "hydrogen": 3, "chlorine": 0},
          "chloride": {"nitrogen": 1, "hydrogen": 4, "chlorine": 1}}
profit = {"gas": 40, "chloride": 50}
stock = {"nitrogen": 50, "hydrogen": 180, "chlorine": 40}


def init_demand(model, p, c):
	return demand[p][c]


def constr_rule(model, c):
	return sum(model.demand[p,c] * model.x[p] for p in model.products) <= model.stock[c]


def buildmodel():
	# Model
	model = ConcreteModel()
	# sets
	model.products = Set(initialize=products)
	model.components = Set(initialize=components)
	# params
	model.demand = Param(model.products, model.components, initialize=init_demand)
	model.profit = Param(model.products, initialize=profit)
	model.stock = Param(model.components, initialize=stock)
	# variables
	model.x = Var(model.products, domain=NonNegativeReals)
	# objective
	model.obj = Objective(expr = sum(model.profit[p] * model.x[p] for p in model.products), sense=maximize)
	# constraints
	model.constrs = Constraint(model.components, rule=constr_rule)
	return model


if __name__ == '__main__':
	model = buildmodel()
	opt = SolverFactory('cplex_persistent')
	opt.set_instance(model)
	res = opt.solve(tee=True)
	for p in model.x:
		print("x[{}] = {}".format(p, value(model.x[p])))