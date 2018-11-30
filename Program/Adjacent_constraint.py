# Imports
# --> Modules
import pandas as pd
import numpy as np
import time
import pulp

# --> Home made files
import Data_importer as DI
import Input_generator as IG
import Coefficient_calculator as CC
import Constraint_generator as CONSTR


# Importing data
#input_data = DI.imported_data
input_data = IG.generate_aircraft(sample_size=10, every_n_minutes=12, show_result=0)
Bay_Assignement = pulp.LpProblem('Bay Assignment', pulp.LpMaximize)

coefficients = CC.coefficient_calculator(input_data, alpha=1, beta=1)
flight_var_indices = [x for x in coefficients]

flight_vars = pulp.LpVariable.dicts('x',flight_var_indices,0, 1, pulp.LpBinary)


time_departure_overlap = np.zeros((len(input_data), len(input_data)))
time_overlap_adjacent_bay = np.zeros((len(input_data), len(input_data)))


#Find overlap in departure time between flights and note these flights
for i in range(len(input_data)):

        # Defining the flight data
        flight_data         = input_data[i]
        flight_departure    = flight_data['atd']
        flight_arrival      = flight_data['ata']
        flight_type         = flight_data['move type']
        
        constraint1 = {}
        constraint_vars1 = []
        constraint2 = {}
        constraint_vars2 = []
        
        #check if the flight in question is departing or short stay
        if flight_type =='Full' or flight_type == 'Dep':
        
            for j, comparing_flight in enumerate(input_data):
                
                constraint1 = {}
                constraint_vars1 = []
                constraint2 = {}
                constraint_vars2 = []
                #check if the flight in question is departing or short stay
                if (i <= j) and (comparing_flight['move type'] =='Full' or comparing_flight['move type'] == 'Dep'):
                    
                    
                # if comparator departure is within the stay of the subject flight, so there is overlap
                    if (flight_arrival < comparing_flight['atd'] < flight_departure) or (comparing_flight['ata'] < flight_departure < comparing_flight['atd']):
                        #now all the overlapping flights have idication of 1.
                        time_departure_overlap[i,j] = 1
                        print(i, 'conflicts with', j )
                        #make constraints:
            
                        constraint1.update({str(i)+'_10':1,
                                            str(i)+'_11':1,
                                            str(j)+'_10':1,
                                            str(j)+'_11':1})
    
                        constraint_vars1 = constraint_vars1 +[str(i)+'_10',
                                            str(i)+'_11',
                                            str(j)+'_10',
                                            str(j)+'_11']
                        print(constraint_vars1)
                        
                        Bay_Assignement += pulp.lpSum([constraint1[k]*flight_vars[k] for k in constraint_vars1]) == 1, 'ADJ1011I'+str(i)+'O'+str(j)
                        
                        constraint2.update({str(i)+'_5':1,
                                            str(i)+'_6':1,
                                            str(j)+'_5':1,
                                            str(j)+'_6':1})
    
                        constraint_vars2 = constraint_vars2 +[str(i)+'_5',
                                            str(i)+'_6',
                                            str(j)+'_5',
                                            str(j)+'_6']
                        
                        Bay_Assignement += pulp.lpSum([constraint2[k]*flight_vars[k] for k in constraint_vars2]) == 1, 'ADJ56I'+str(i)+'O'+str(j)
