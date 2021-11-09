#!/usr/bin/env python
# encoding: utf-8

import pyomo.environ as pe
from pyomo.opt import SolverFactory

def buildmodel():
	# Model
	model = pe.ConcreteModel()
	# variables
	model.gas = pe.Var(domain=pe.NonNegativeReals)
	model.chloride = pe.Var(domain=pe.NonNegativeReals)
	# objective
	model.obj = pe.Objective(expr = 40 * model.gas + 50 * model.chloride, sense=pe.maximize)
	# constraints
	model.c1 = pe.Constraint(expr = model.gas + model.chloride <= 50)
	model.c2 = pe.Constraint(expr = 3 * model.gas + 4 * model.chloride <= 180)
	model.c3 = pe.Constraint(expr = model.chloride <= 40)
	return model


if __name__ == '__main__':
	model = buildmodel()
	opt = SolverFactory('cplex_persistent')
	opt.set_instance(model)
	res = opt.solve(tee=False)
	print("gas =", pe.value(model.gas))
	print("chloride =", pe.value(model.chloride))
