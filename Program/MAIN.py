from scipy.optimize import linprog
from datetime import datetime
import pandas as pd
import numpy as np
from math import *

#Importing other file
import data_importer as DI
import Coefficient_calculator as CC

#Importing data
simulation_cases = DI.simulation_cases

simulation_case = simulation_cases['01']

#Objective function coefficients
coefficients = CC.coefficient_calculator(simulation_case, 'A')



#Final Optimization
c = [-1, 4] #coefficients
A = [[-3, 1], [1, 2]]
b = [6, 4]

bounds_ = []
for i in range(len(c)):
    bounds_.append((0,1))

    
res = linprog(c, A_ub=A, b_ub=b, bounds=bounds_, options={"disp": False})
print(res)

