# Imports
# --> Modules
import pandas as pd
import numpy as np
import time
import pulp

# --> Home made files
import Data_importer as DI

# Importing data
input_data = IG.generate_aircraft(sample_size=20, show_result=1)


time_departure_overlap = np.zeros((len(input_data), len(input_data)))
time_overlap_adjacent_bay = np.zeros((len(input_data), len(input_data)))


#Find overlap in departure time between flights and note these flights
for i in range(len(input_data)):

        # Defining the inbound flight data
        flight_data         = input_data[i]
        flight_departure    = flight_data['atd']
        flight_arrival      = flight_data['ata']
        
        
        for j, comparator_data in enumerate(input_data):
            if (i <= j):
                
                # if comparator departure is within the stay of the subject flight, so there is overlap
                if flight_arrival < comparator_data['atd'] < flight_departure:

                    time_departure_overlap[i,j] = 1
                    time_overlap_adjacent_bay[i,j] = '10.'
                    #now all the overlapping flights have idication of 1.
                    #check for these flights that are complaint at gate 10
                    
#                    comparator_group = aircraft_type2characteristics[comparator_data['ac type']]['Group']
 #                   comparator_bays  = group2bay_compliance[comparator_group]

                  #make a constraint:
                    constraint_name = 'TCI'+str(i)+'O'+str(j)+'B'+'10'
                            
                    constraint_vars = [str(i)+'_'+'10', str(j)+'_'+'11']
                    constraint_coef = {str(i)+'_'+'10': 1, str(j)+'_'+'11': 1}
                            
                    
                    
                    
                    
                    
                    
                    
                #check for gates 10 and 11 amongs the overlapping flights
 #                   if (bay_i = 10 and bay_j = 11) or (bay_i = 11) and 
                
 
 
#                for k in range((len(input_data))-i):
 #                   if time_departure
                    
                
        
        

#List  all pairs that are in bay 11&10 and 5&6


#Insert these pairs in a soft constraint, where penalty is (-)1



