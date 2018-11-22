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
preferences             = DI.preferences



simulation_case = simulation_cases['01']

terminal = 'A'

z1_coefficients = []
z2_coefficients = []

# Determining coefficients of decision variables

print ('Generating Coefficients: ...')
flight_numbers_arrival = simulation_case['Fl No. Arrival'].unique()
flight_numbers_departure = simulation_case['Fl No. Departure'].unique()
for i in range(len(flight_numbers_arrival)):
    flight_number_arrival = flight_numbers_arrival[i]
    
    if flight_number_arrival in flight_no2aircraft_type:

        #Find number of passengers in an aircraft
        aircraft_type     = flight_no2aircraft_type[flight_number_arrival]
        aircraft_capacity = int(aircraft_type2capacity[aircraft_type]['Capacity'])
        aircraft_group    = aircraft_type2group[aircraft_type]

        #Possible bays for aircraft model
        bay_compliance    = group2bay_compliance[['Bay', aircraft_group]] 
        possible_bays = list(bay_compliance.loc[bay_compliance[aircraft_group].isin([1])]['Bay'].unique())

        #Preference
        preference_bay = ''
        if flight_number_arrival in preferences['Fl No.'].unique():
            flight_index_pref = list(preferences['Fl No.']).index(flight_number_arrival)
            preference_bays = (preferences['Bay'].iloc[flight_index_pref]).split(',')
            
            #print (flight_number_arrival, aircraft_type, aircraft_group, aircraft_capacity, preference_bay)
            
        else:
            #-- finding departure flight number
            flight_index = list(simulation_case['Fl No. Arrival']).index(flight_number_arrival)
            flight_number_departure = simulation_case['Fl No. Departure'].iloc[flight_index]

            if flight_number_departure in preferences['Fl No.'].unique():
                flight_index_pref = list(preferences['Fl No.']).index(flight_number_departure)
                preference_bays = (preferences['Bay'].iloc[flight_index_pref]).split(',')
                
                #print (flight_number_arrival, aircraft_type, aircraft_group, aircraft_capacity, preference_bay)
                
        
        for j in range(len(possible_bays)):
            bay = possible_bays[j]
            terminal_distances = bay_distances[['Bay', terminal]]
            distance = int(terminal_distances.loc[terminal_distances['Bay'].isin([bay])].iloc[0, 1])
            z1_coefficients.append(aircraft_capacity * distance)

            if j in preference_bays:
                z2_coefficients.append(1)
            else:
                z2_coefficients.append(0)

z1_coefficients = np.array(z1_coefficients)
z2_coefficients = np.array(z2_coefficients)

print ('Generating Coefficients: DONE\n')
            

alpha = 1
beta = 1

final_coefficients = (alpha*(-1* z1_coefficients)) + (beta * z2_coefficients)






c = [-1, 4] #coefficients
A = [[-3, 1], [1, 2]]
b = [6, 4]

bounds_ = []
for i in range(len(c)):
    bounds_.append((0,1))

    
res = linprog(c, A_ub=A, b_ub=b, bounds=bounds_, options={"disp": True})
print(res)

