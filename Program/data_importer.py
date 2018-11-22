import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import os

from datetime import datetime
from math import *

import Converters as CONV


#Directory definitions
base_directory = '../csv_data_appendices'
simulation_files = [x for x in os.listdir(base_directory) if 'Simulation Case ' in x]

simulation_files.sort()


print ('Importing info: ...')

simulation_cases = {}
for simulation_file in simulation_files:

    #Importing Simulation Data
    imported_data = pd.read_csv(open(base_directory+'/'+simulation_file), sep=',')
    simulation_cases.update({simulation_file[-6:-4]:imported_data})

    
    #Showing Aircraft Ground Time
    plot_requirements = 0
    if plot_requirements:
    
        arrival_departure = imported_data[['ATA', 'ATD']]

        #Plot Characteristics
        fig, ax = plt.subplots()
        myFmt = mdates.DateFormatter('%H:%M')
        
        for i in range(len(arrival_departure['ATA'])):
            
            ata = pd.to_datetime(arrival_departure['ATA'][i])
            atd = pd.to_datetime(arrival_departure['ATD'][i])
            
            ax.plot([ata, atd],[i+1, i+1], c='k')
            
        ax.set_title(simulation_file)
        
        ax.xaxis.set_major_formatter(myFmt)
        ax.set_xlim([datetime.now().replace(hour=0 , minute=0 , second=0 , microsecond=0),
                     datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)])
        plt.show()


#Importing Remaining Information
#-- pandas
group2bay_compliance = pd.read_csv(open(base_directory+'/Bay Compliance.csv'  ), sep=',')
bay_distances        = pd.read_csv(open(base_directory+'/Bay Distances.csv'   ), sep=',')
preferences          = pd.read_csv(open(base_directory+'/Preference Table.csv'), sep=',')

#-- csv to dictionary
flight_no2aircraft_type = CONV.csv2dict(base_directory+'/flight_no2aircraft_type.csv', sep=',')
aircraft_type2capacity  = CONV.csv2dict(base_directory+'/Aircraft_type2capacity.csv' , sep=',', main_cat='AC Type')
aircraft_type2group     = CONV.csv2dict(base_directory+'/Aircraft_type2Group.csv'    , sep=',')



print ('Importing info: DONE \n')













'''
result_files = ['Bay Assignments Results 02-06-2015.csv',
                'Bay Assignments Results 05-07-2015.csv']

results = []
test = []
for result_file in result_files:
    local_result = pd.read_csv(open(base_directory+'/'+result_file), sep=',')
    results.append(local_result)
    flight_no2ac_type = local_result[['Fl No.', 'AC Type']]
    test_value = flight_no2ac_type[flight_no2ac_type['Fl No.'].notnull()]
    test_value.to_csv(base_directory+'/conv_'+result_file,sep=',')
    test.append(test_value)
'''


    

