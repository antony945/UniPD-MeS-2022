from pyomo.environ import *

def printVarOnFile(instance):
    # Write solution to a file
    with open(__file__[:-3]+'.txt', 'w') as f:
        for p in instance.x:
            f.write("x[{}] = {}\n".format(p, value(instance.x[p])))