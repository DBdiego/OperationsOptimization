# Imports
# --> Modules
import pandas as pd
import numpy as np
import datetime
import csv
import os

# --> Module classes
import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
from math import *

# --> Home made files
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
        unique_flight_numbers = list(imported_data['Fl No. Arrival'].unique())
    
        arrival_departure = imported_data[['ATA', 'ATD']]

        #Plot Characteristics
        fig, ax = plt.subplots()
        myFmt = mdates.DateFormatter('%H:%M')

        atas = []
        atds = []
        
        for i, flight_number in enumerate(unique_flight_numbers):
            flight_number_index = list(imported_data['Fl No. Arrival']).index(flight_number)

            #Color and times of arrival & departure
            flight_type = imported_data['Flight Type'].iloc[flight_number_index]
            if flight_type.lower() == 'full':
                color = 'blue'
                
                ata = pd.to_datetime(imported_data['ATA'].iloc[flight_number_index])
                atd = pd.to_datetime(imported_data['ATD'].iloc[flight_number_index])
            else:
                color = 'red'

                ata = pd.to_datetime(imported_data['ATA'].iloc[flight_number_index])
                atd = pd.to_datetime(imported_data['ATD'].iloc[flight_number_index+2])

            #Date correction if needed
            if atd < ata:
                atd = atd + datetime.timedelta(days=1)

            atas.append(ata)
            atds.append(atd)

            #Ploting the data
            ax.plot([ata, atd],[i+1, i+1], c=color)

        #Other plot characteristics          
        ax.set_title(simulation_file)
        
        ax.xaxis.set_major_formatter(myFmt)
        ax.set_xlim([min(atas)-datetime.timedelta(hours=1),
                     max(atds)+datetime.timedelta(hours=1)])
        
        ax.set_ylabel('flight number')
        plt.savefig('./plots/Ground_time_SC'+ simulation_file[-6:-4]+'.pdf')
        plt.show()


#Importing Remaining Information
#-- pandas
group2bay_compliance = pd.read_csv(open(base_directory+'/Bay Compliance.csv'  ), sep=',')
bay_distances        = pd.read_csv(open(base_directory+'/Bay Distances.csv'   ), sep=',')
preferences          = pd.read_csv(open(base_directory+'/Preference Table.csv'), sep=',')

#-- csv to dictionary
aircraft_type2characteristics = CONV.csv2dict(base_directory+'/Aircraft_type2characteristics.csv' , sep=',', main_cat='AC Type')
flight_no2aircraft_type       = CONV.csv2dict(base_directory+'/flight_no2aircraft_type.csv'       , sep=',')
#aircraft_type2group           = CONV.csv2dict(base_directory+'/Aircraft_type2Group.csv'           , sep=',')


print ('Importing info: DONE \n')






result_files = ['Bay Assignments Results 02-06-2015.csv',
                'Bay Assignments Results 05-07-2015.csv']

appendix_result = pd.read_csv(open(base_directory+'/'+result_files[0]), sep=',')






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


    

