# Imports
# --> Modules
import pandas as pd
import numpy as np
import datetime
import pulp
import time

# --> Module classes
from scipy.optimize import linprog
from math import *

# --> Home made files
import Coefficient_calculator as CC
import Constraint_generator as CONSTR
import Input_generator as IG
import Data_importer as DI



# [0] Generate Input Data
input_data = IG.generate_aircraft(sample_size=102, show_result=0)


# [1] Objective function coefficients
coefficients = CC.coefficient_calculator(input_data, alpha=1, beta=1)
flight_var_indices = [x for x in coefficients]


# [2] Definition of initial problem
Bay_Assignement = pulp.LpProblem('Bay Assignment', pulp.LpMaximize)


# [3] Defining Variables of the problem
flight_vars = pulp.LpVariable.dicts('x',flight_var_indices,0, 1, pulp.LpBinary)


# [4] Objective Function
Bay_Assignement += pulp.lpSum([coefficients[i]*flight_vars[i] for i in flight_var_indices]), 'Object to maximize'


# [5] Constraints
print ('Adding Constraints: ...')
start_constraints = time.time()

# --> Bay Compliance
Bay_Assignement, bay_constraints  = CONSTR.add_bay_compliance(input_data, Bay_Assignement, flight_vars)

# --> Time Constraint
Bay_Assignement, time_conflicts   = CONSTR.add_time_constraint(input_data, Bay_Assignement, flight_vars)

# --> Fuel Constraint
Bay_Assignement, fuel_constraints = CONSTR.add_fuelling_constraint(input_data, Bay_Assignement, flight_vars)

# --> Adjancy Constraint
#Bay_Assignement = Bay_Assignement

# --> Night Stay Constraint
#Bay_Assignement = Bay_Assignement

print ('Adding Constraints: DONE ('+str(round(time.time() - start_constraints, 3))+' seconds)\n')



# [6] The problem data is written to an .lp file
Bay_Assignement.writeLP('./Bay_Assignment.lp')


# [7] The problem is SOLVED using PuLP's choice of Solver
print('Solving the problem: ...')
start_solve = time.time()
Bay_Assignement.solve()
print('Solving the problem: DONE ('+str(round(time.time() - start_solve, 3))+' seconds)\n')


# [8] Displaying solved problem solution to user
# --> The status of the solution is printed to the screen
print ("Solution is:", pulp.LpStatus[Bay_Assignement.status])









'''
# --> Each of the variables is printed with it's resolved optimum value
for v in Bay_Assignement.variables():
    if int(v.varValue):
        print (v.name, "=", v.varValue)

# --> The optimised objective function value is printed to the screen    
print ("Total Cost of Ingredients per can = ", pulp.value(Bay_Assignement.objective))
'''


