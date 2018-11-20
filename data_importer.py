import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from math import *
import os
import csv
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime

base_directory = './csv_data_appendices'

files = [x for x in os.listdir(base_directory) if 'Simulation Case ' in x]


files.sort()

simulation_cases = {}

print ('Importing info: ...')
for file in files:

    #Importing Data
    imported_data = pd.read_csv(open(base_directory+'/'+file), sep=',')
    simulation_cases.update({file[-6:-4]:imported_data})
    print('  '+file+': DONE')

    
    #Showing Aircraft Ground Time
    plot_requirements = 0
    if plot_requirements:
    
        arrival_departure = imported_data[['ATA', 'ATD']]
        fig, ax = plt.subplots()
        
        for i in range(len(arrival_departure['ATA'])):
            
            ata = pd.to_datetime(arrival_departure['ATA'][i])
            atd = pd.to_datetime(arrival_departure['ATD'][i])
            
            ax.plot([ata, atd],[i+1, i+1], c='k')
            
        ax.set_title(file)
        myFmt = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(myFmt)
        ax.set_xlim([datetime.now().replace(hour=0 , minute=0 , second=0 , microsecond=0),
                     datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)])
        plt.show()


a2c = pd.read_csv(open(base_directory+'/Aircraft_type2capacity.csv'), sep=',')
bay_distances = pd.read_csv(open(base_directory+'/Bay Distances.csv'), sep=',') 


'''
result_files = ['Bay Assignments Results 02-06-2015.csv',
                'Bay Assignments Results 05-07-2015.csv']

results = []
for result_file in result_files:
    results.append(pd.read_csv(open(base_directory+'/'+result_file), sep=','))
'''

print ('Importing info: DONE')
    

