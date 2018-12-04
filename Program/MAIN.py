# Imports
# --> Modules
import pandas as pd
import numpy as np
import datetime
import pulp
import time

# --> Module classes
from math import *

# --> Home made files
import Coefficient_calculator as CoC
import Constraint_generator as CONSTR
import Input_generator as IG
import Data_importer as DI
import Data_exporter as DE
import Converters as CONV


USE_PREGENERATED_DATA = 0 # Use existing file as input

# [0] Generate Input Data
input_data = IG.generate_aircraft(USE_PREGENERATED_DATA, sample_size=50, show_result=0)


# [1] Objective function coefficients & Weights
coefficients = CoC.coefficient_calculator(input_data)
flight_var_indices = [x for x in coefficients]



# [2] Definition of initial problem
Bay_Assignment = pulp.LpProblem('Bay Assignment', pulp.LpMaximize)



# [3] Defining Variables of the problem
flight_vars = pulp.LpVariable.dicts('DV',flight_var_indices,0, 1, pulp.LpBinary)



# [4] Objective Function
Bay_Assignment += pulp.lpSum([coefficients[i]*flight_vars[i] for i in flight_var_indices]), 'Object to maximize'



# [5] Constraints
print ('Adding Constraints: ...')
start_constraints = time.time()

# --> Bay Compliance
Bay_Assignment, bay_constraints  = CONSTR.add_bay_compliance(input_data, Bay_Assignment, flight_vars)

# --> Time Constraint
Bay_Assignment, time_conflicts   = CONSTR.add_time_constraint(input_data, Bay_Assignment, flight_vars)

# --> Fuel Constraint
Bay_Assignment, fuel_constraints = CONSTR.add_fuelling_constraint(input_data, Bay_Assignment, flight_vars)

# --> Adjancy Constraint
Bay_Assignement = CONSTR.add_adjancy_constraint(input_data, Bay_Assignment, flight_vars)

# --> Night Stay Constraint
Bay_Assignement = CONSTR.add_split_constraint(input_data, Bay_Assignment, flight_vars)

print ('Adding Constraints: DONE ('+str(round(time.time() - start_constraints, 3))+' seconds)\n')



# [6] The problem data is written to an .lp file
Bay_Assignment.writeLP('./Bay_Assignment.lp')



# [7] The problem is SOLVED using PuLP's choice of Solver (LPSolve)
print('Solving the problem: ...')
start_solve = time.time()
Bay_Assignment.solve()
print('Solving the problem: DONE ('+str(round(time.time() - start_solve, 3))+' seconds)\n\n')


# [8] Displaying solved problem solution to user
print ('======= - STATUS - ======= ')
print ('Objective: Maximize Z'      )
print ('Solution is ' + str(pulp.LpStatus[Bay_Assignment.status]))
print ('Z = '         + str(pulp.value(Bay_Assignement.objective)))
print ('========================== \n\n')


# [9] Saving Overview of problem solution
output_dataframe = DE.save_data(input_data, Bay_Assignement)




