# Imports
# --> Modules
import pandas as pd
import numpy as np
import datetime
import pulp
#import cplex as cpx


import time

# --> Module classes
from docplex.mp.model import Model
from docplex.mp.conflict_refiner import ConflictRefiner
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
input_data = IG.generate_aircraft(USE_PREGENERATED_DATA, sample_size=110, show_result=0)


# [1] Objective function coefficients & Weights
coefficients = CoC.coefficient_calculator(input_data, fb=1)
flight_var_indices = [x for x in coefficients]


# [2] Definition of initial problem
#Bay_Assignment = pulp.LpProblem('Bay Assignment', pulp.LpMaximize) #pulp.LpMinimize)
Bay_Assignment = Model('Bay Assignment 2')




# [3] Defining Variables of the problem
#flight_vars = pulp.LpVariable.dicts('DV',flight_var_indices,0, 1, pulp.LpBinary)
flight_vars = Bay_Assignment.binary_var_dict(keys=flight_var_indices, name='DV')




# [4] Objective Function
#Bay_Assignment += pulp.lpSum([coefficients[i]*flight_vars[i] for i in flight_var_indices]), 'Object to maximize'
Objective_function = Bay_Assignment.sum(coefficients[i]*flight_vars[i] for i in flight_var_indices)
Bay_Assignment.maximize(Objective_function)


# [5] Constraints
print ('Adding Constraints: ...')
start_constraints = time.time()

# --> Bay Compliance
num_BC = 0
#Bay_Assignment, bay_constraints , num_BC = CONSTR_P.add_bay_compliance(input_data, Bay_Assignment, flight_vars, fb=1)
Bay_Assignement, bay_constraints , num_BC = CONSTR.add_bay_compliance(input_data, Bay_Assignment, flight_vars, fb=1)

# --> Time Constraint
num_T = 0
#Bay_Assignment, time_conflicts  , num_T = CONSTR_P.add_time_constraint(input_data, Bay_Assignment, flight_vars, fb=1)
Bay_Assignment, time_conflicts  , num_T = CONSTR.add_time_constraint(input_data, Bay_Assignment, flight_vars, fb=1)

# --> Fuel Constraint
num_F= 0
#Bay_Assignment, fuel_constraints, num_F = CONSTR.add_fuelling_constraint(input_data, Bay_Assignment, flight_vars, fb=1)
Bay_Assignment, fuel_constraints, num_F = CONSTR.add_fuelling_constraint(input_data, Bay_Assignment, flight_vars, fb=1)

# --> Adjacency Constraint
num_A = 0
#Bay_Assignment, num_A = CONSTR_P.add_adjancy_constraint(input_data, Bay_Assignment, flight_vars, fb=1)
Bay_Assignment, num_A = CONSTR.add_adjancy_constraint(input_data, Bay_Assignment, flight_vars, fb=1)

# --> Night Stay Constraint
num_NS = 0
#Bay_Assignment, num_NS = CONSTR_P.add_split_constraint(input_data, Bay_Assignment, flight_vars, fb=1)
Bay_Assignment, num_NS = CONSTR.add_split_constraint(input_data, Bay_Assignment, flight_vars, fb=1)

print ('Adding Constraints: DONE ('+str(round(time.time() - start_constraints, 3))+' seconds)\n')


# [5.1] Checking for conflicting constraints
print ('Checking for conflicting constraints: ...')
crefiner = ConflictRefiner()
conflicts = crefiner.refine_conflict(Bay_Assignment)
print ('Checking for conflicting constraints: DONE ('+ str(len(conflicts))+' found)\n')

# [5.2] Adding KPI's
Bay_Assignment.add_kpi(Bay_Assignment.sum(coefficients[i]*flight_vars[i] for i in flight_var_indices if 'x' in i), 'Passenger Distance')
#Bay_Assignment.report()

# [6] Writing .lp file
print('Writing to .lp file: ...')
start_writing = time.time()

#Bay_Assignment.writeLP('./Bay_Assignment.lp')
Bay_Assignment.export('./Bay_Assignment.lp')

print('Writing to .lp file: DONE ('+str(round(time.time() - start_writing, 3))+' seconds)\n')




# [7] The problem is SOLVED using CPLEX
extra_info = 0
if extra_info:
    Bay_Assignment.print_information()
    
print('Solving the problem: ...')
start_solve = time.time()
Bay_Assignment.solve()
print('Solving the problem: DONE ('+str(round(time.time() - start_solve, 3))+' seconds)\n\n')


solve_status = Bay_Assignment.solve_details.status
if extra_info:
    print (Bay_Assignment.solve_details)



    


# [8] Displaying solved problem solution to user
print ('======= - STATUS - ======= ')
print ('Objective: Maximize Z'      )
print (str(len(flight_var_indices)) + ' Decision variables')
print (str(sum([num_BC, num_T, num_F, num_A, num_NS]))+' Constraints: ')
print ('  |--> Time           : ' + str(num_T ))
print ('  |--> Fuelling       : ' + str(num_F ))
print ('  |--> Adjacency      : ' + str(num_A ))
print ('  |--> Night Stay     : ' + str(num_NS))
print ('  |--> Bay Compliance : ' + str(num_BC))
print ('Solution is ' + str(solve_status))
print ('Z = '         + str(Bay_Assignment.objective_value))
print ('========================== \n\n')



# [9] Saving Overview of problem solution
solve_status = solve_status.split(' ')[1].replace(',', '') #= Bay_Assignment.solve_details.status.split(' ')[1]
output_dataframe = DE.save_data(input_data, Bay_Assignment, solve_status)


