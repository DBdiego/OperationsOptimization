from scipy.optimize import linprog
from datetime import datetime
import pandas as pd
import numpy as np
from math import *

#Importing other file
import data_importer as DI

#Importing data
simulation_cases  = DI.simulation_cases
aircraft2capacity = DI.aircraft2capacity
bay_distances     = DI.bay_distances
aircraft2group    = DI.aircraft2group

flight_no2aircraft_type = DI.flight_no2aircraft_type
group2bay_compliance    = DI.group2bay_compliance



simulation_case = simulation_cases['01']

# Determining coefficients of decision variables
for i in range(len(simulation_case)):
    flight_number = simulation_case['Fl No.'][i]
    
    aircraft_type = flight_no2aircraft_type.loc[flight_no2aircraft_type['Fl No.'].isin([flight_number])]
    #print ('Fl No.')
    print (flight_number, aircraft_type)
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

