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

# Determining coefficients of decision variables
for i in range(len(simulation_case)):
    flight_number = simulation_case['Fl No.'][i]
    
    if flight_number in flight_no2aircraft_type:

        #Find number of passengers in an aircraft
        aircraft_type     = flight_no2aircraft_type[flight_number]
        aircraft_capacity = aircraft_type2capacity[aircraft_type]['Capacity']
        aircraft_group    = aircraft_type2group[aircraft_type]
        bay_compliance    = group2bay_compliance[['Bay', aircraft_group]] 
        print (flight_number, aircraft_type, aircraft_group, aircraft_capacity)
        
        for j in range(len(bay_distances)):
            
            
            
            
            pass





c = [-1, 4]
A = [[-3, 1], [1, 2]]
b = [6, 4]

x0_bounds = (None, None)
x1_bounds = (-3, None)
bounds_ = []

for i in range(len(c)):
    bounds_.append((0,1))

    
res = linprog(c, A_ub=A, b_ub=b, bounds=bounds_, options={"disp": True})
print(res)

