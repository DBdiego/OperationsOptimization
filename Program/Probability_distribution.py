import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import os

import datetime
from math import *

# Imported data from data_importer script
import data_importer as DI


total_num_flights = len(DI.imported_data['Fl No. Arrival'].unique())

# Aircraft type distribution
AC_count = pd.DataFrame(DI.local_result['AC Type'].value_counts().reset_index())
AC_count.columns = ['AC Type', 'Count']

AC_count['Probs'] = AC_count['Count']/sum(list(AC_count['Count']))
AC_count = AC_count[['AC Type', 'Probs']]

AC_count.to_csv('../csv_data_appendices/input_distributions/AC_type_distribution.csv')



### TIME SAMPLING

def create_time_array(every_n_minutes):
    time_array = []
    num_hour_interv = 24
    num_min_interv  = int(60/every_n_minutes)
    for hour in range(num_hour_interv):
        for minute in range(num_min_interv):
            time = datetime.datetime.today().replace(hour=hour, minute=minute*every_n_minutes, second=0, microsecond=0)#.strftime('%H:%M')
            time_array.append(time)

    return np.array(time_array)


def sampler(sample_mold, to_be_sampeled):
    count = np.zeros(len(sample_mold))
    for i, sample in enumerate(to_be_sampeled):
        for j in range(1, len(sample_mold)):
            if sample_mold[j-1] <= sample < sample_mold[j]:
                count[j-1] += 1
  
    return count

arrival_times   = list(pd.to_datetime(DI.imported_data['ATA']))
departure_times = list(pd.to_datetime(DI.imported_data['ATD']))

for every_n_minutes in [10, 20, 30, 60]:
    times = create_time_array(every_n_minutes)

    number_arrivals   = sampler(times, arrival_times)
    number_departures = sampler(times, departure_times)

    number_flights_tarmac = []

    plots_wanted = 0
    if plots_wanted:
        fig, ax = plt.subplots()
        myFmt = mdates.DateFormatter('%H:%M')
        
        bar_width = 0.003 
        opacity = 0.8

        ax.bar(times-datetime.timedelta(hours=1*bar_width),
               number_arrivals  ,
               bar_width       ,
               alpha = opacity ,
               color = 'blue'   ,
               label = 'arrivals')
        
        ax.bar(times+datetime.timedelta(hours=1*bar_width),
               number_departures  ,
               bar_width       ,
               alpha = opacity ,
               color = 'red'   ,
               label = 'departures')
        
        ax.legend()
        ax.set_title('sampling every '+str(every_n_minutes)+' minutes')
        ax.xaxis.set_major_formatter(myFmt)
        ax.set_xlim([min(times)-datetime.timedelta(hours=1),
                     max(times)+datetime.timedelta(hours=1)])

        ax.set_ylabel('number of flights')
        plt.show()

    Arrival_count = pd.DataFrame(np.column_stack((times, number_arrivals)))
    Arrival_count.columns=['Time', 'Count']
    Arrival_count['Probs'] = Arrival_count['Count']/sum(list(Arrival_count['Count']))
    Arrival_count[['Time', 'Probs']].to_csv('../csv_data_appendices/input_distributions/arrival_sampling_'+str(every_n_minutes)+'.csv', sep=',')
    

        
        
















'''
np.random.choice
'''



