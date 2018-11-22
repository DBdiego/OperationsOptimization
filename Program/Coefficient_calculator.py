from scipy.optimize import linprog
from datetime import datetime
import pandas as pd
import numpy as np
from math import *

#Importing other file
import data_importer as DI

#Importing data
simulation_cases  = DI.simulation_cases
bay_distances     = DI.bay_distances

flight_no2aircraft_type = DI.flight_no2aircraft_type
aircraft_type2capacity  = DI.aircraft_type2capacity
group2bay_compliance    = DI.group2bay_compliance
aircraft_type2group     = DI.aircraft_type2group



simulation_case = simulation_cases['01']

terminal = 'A'

z1_coefficients = []
z2_coefficients = []

# Determining coefficients of decision variables

flight_numbers = simulation_case['Fl No.'].unique()
for i in range(len(flight_numbers)):
    flight_number = flight_numbers[i]
    
    if flight_number in flight_no2aircraft_type:

        #Find number of passengers in an aircraft
        aircraft_type     = flight_no2aircraft_type[flight_number]
        aircraft_capacity = int(aircraft_type2capacity[aircraft_type]['Capacity'])
        aircraft_group    = aircraft_type2group[aircraft_type]

        #Possible bays for aircraft model
        bay_compliance    = group2bay_compliance[['Bay', aircraft_group]] 
        possible_bays = list(bay_compliance.loc[bay_compliance[aircraft_group].isin([1])]['Bay'].unique())
        #preference
        print (flight_number, aircraft_type, aircraft_group, aircraft_capacity)#, preference)
        
        for j in range(len(possible_bays)):
            bay = possible_bays[j]
            terminal_distances = bay_distances[['Bay', terminal]]
            distance = int(terminal_distances.loc[terminal_distances['Bay'].isin([bay])].iloc[0, 1])
            z1_coefficients.append(aircraft_capacity * distance)
            #z2_coefficients.append(1)

            

z1_coefficients = np.array(z1_coefficients)
z2_coefficients = np.array(z2_coefficients)






c = [-1, 4] #coefficients
A = [[-3, 1], [1, 2]]
b = [6, 4]

bounds_ = []
for i in range(len(c)):
    bounds_.append((0,1))

    
res = linprog(c, A_ub=A, b_ub=b, bounds=bounds_, options={"disp": True})
print(res)

