# Imports
# --> Modules
import pandas as pd
import numpy as np
import datetime

# --> Module classes
import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
from scipy.stats import norm
from math import *

# --> Home made files
import Data_importer as DI


'''
=============================== -- INFO -- ===============================
The tables found in the appendices approximated in this code are:
    - All "Simulation Case ##.csv" files
    - "Bay Assignments Results 02-06-2015.csv"
    - "Bay Assignments Results 05-07-2015.csv"

The Distributions are found using descrete probability theory. Mostly
counting the number of occurences of a certain event (e.g. # of times
the A787-800 lands) compared to the total of events (total # arriving
aircraft).

Values approximated are:
    - Aircraft Type (model)
    - Actual Time of Arrival (ATA)
    - Duration of Stay at the airport
  ! - Domestic/International Flight    *!!! NOT DONE YET !!!*
==========================================================================
'''

imported_data   = DI.simulation_cases['01']
appendix_result = DI.appendix_result


print ('Approximating probability disitributions: ...')


total_num_flights = len(imported_data['Fl No. Arrival'].unique())

### AIRCRAFT TYPE
AC_count = pd.DataFrame(appendix_result['AC Type'].value_counts().reset_index())
AC_count.columns = ['AC Type', 'Count']

AC_count['Probs'] = AC_count['Count']/sum(list(AC_count['Count']))
AC_probs = AC_count[['AC Type', 'Probs']]

AC_probs.to_csv('../csv_data_appendices/input_distributions/AC_type_distribution.csv')



# AIRLINE CODE DISTR
airlines = pd.DataFrame(imported_data['Fl No. Arrival'].unique())[0].str[:2]
AL_count = pd.DataFrame(airlines.value_counts().reset_index())
AL_count.columns = ['AL Code', 'Count']

AL_count['Probs'] = AL_count['Count']/sum(list(AL_count['Count']))
AL_probs = AL_count[['AL Code', 'Probs']]

AL_probs.to_csv('../csv_data_appendices/input_distributions/AL_code_distribution.csv')


# DOMESTIC - INTERNATIONAL PROBABILITIES
imported_data_flights = imported_data[['Fl No. Arrival', 'Origin', 'Fl No. Departure', 'Dest']].drop_duplicates().reset_index()
airports = pd.read_csv(open('../csv_data_appendices/Airports.csv'  ), sep=',')

domestic_airport_codes = list(airports[airports['Country']=='Kenya']['Airport Code'])

flight_ranges = []
for flight_origin in list(imported_data_flights['Origin']):
    
    if flight_origin in domestic_airport_codes:
        flight_ranges.append('DOM')
    else:
        flight_ranges.append('INT')
        
imported_data_flights['Flight Range'] = flight_ranges
FR_count = pd.DataFrame(imported_data_flights['Flight Range'].value_counts().reset_index())
FR_count.columns = ['Flight Range', 'Count']

FR_count['Probs'] = FR_count['Count']/sum(list(FR_count['Count']))
FR_probs = FR_count[['Flight Range', 'Probs']]


# Counting occurences
airline_dom_int = {}
for i, flight_number in enumerate(list(imported_data_flights['Fl No. Arrival'])):
    try:
        airline = flight_number[:2]
        
        if not (airline in airline_dom_int):
            airline_dom_int.update({airline:{'dom_count':0, 'int_count':0}})
                            
        flight_origin = imported_data_flights['Origin'].iloc[i]
        
        if flight_origin in domestic_airport_codes:
            airline_dom_int[airline]['dom_count']+=1
        else:
            airline_dom_int[airline]['int_count']+=1
            
    except TypeError:
        pass

list_dom_int = []
for key in airline_dom_int:
    info = airline_dom_int[key]
    info.update({'airline': key,
                 'total'  : airline_dom_int[key]['dom_count'] + \
                            airline_dom_int[key]['int_count']  })
    list_dom_int.append(info)

#Calculating the Probabilities
AL_DOM_INT = pd.DataFrame(list_dom_int)
AL_DOM_INT['dom_probs'] = AL_DOM_INT['dom_count']/AL_DOM_INT['total']
AL_DOM_INT['int_probs'] = AL_DOM_INT['int_count']/AL_DOM_INT['total']

AL_probs_dom_int = AL_DOM_INT[['airline', 'dom_probs', 'int_probs']]
AL_probs_dom_int.to_csv('../csv_data_appendices/input_distributions/Al_domestic_international.csv')



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

def create_stays_array(every_n_minutes, aircraft_data):
    stay_array = np.arange(0, max(aircraft_stay)+every_n_minutes*60, every_n_minutes*60)
    return stay_array
        

def sampler(sample_mold, to_be_sampeled):
    count = np.zeros(len(sample_mold))
    for i, sample in enumerate(to_be_sampeled):
        for j in range(1, len(sample_mold)):
            if sample_mold[j-1] <= sample < sample_mold[j]:
                count[j-1] += 1
  
    return count


# Getting Arrival and Departure times of flight numbers (split flights will be combined as one)
arrival_times   = []
departure_times = []
flight_numbers  = list(imported_data['Fl No. Arrival'].unique())
for i, flight_number in enumerate(flight_numbers):
    
    flight_data = imported_data[imported_data['Fl No. Arrival'] == flight_number]
    
    if len(flight_data) == 1:
        arrival_times  .append(list(pd.to_datetime(flight_data['ATA']))[0])
        departure_times.append(list(pd.to_datetime(flight_data['ATD']))[0])
        
    elif len(flight_data) > 1:
        arrival_times  .append(list(pd.to_datetime(flight_data[flight_data['Flight Type']=='Arr']['ATA']))[0])
        departure_times.append(list(pd.to_datetime(flight_data[flight_data['Flight Type']=='Dep']['ATD']))[0])
        
    

aircraft_stay = []
count = 0
for i in range(len(arrival_times)):
    
    if departure_times[i] > arrival_times[i]:
        duration = departure_times[i] - arrival_times[i]        
    else:
        duration = arrival_times[i] - departure_times[i]
        
    if duration > datetime.timedelta(hours=5, minutes=40):
        count += 1

    aircraft_stay.append(duration.total_seconds())
print (round(100*count/len(arrival_times), 2), '% of flights are "long stay" flights')



for every_n_minutes in [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30]:

    # Generating Sampling 'molds' (in which data is classified/sampled)
    times = create_time_array (every_n_minutes)
    stays = create_stays_array(every_n_minutes, aircraft_stay)

    # Sampling the imported data
    number_arrivals   = sampler(times, arrival_times   )
    number_departures = sampler(times, departure_times )
    number_duration   = sampler(stays, aircraft_stay   )

    stays = [datetime.timedelta(seconds=x) for x in stays]


    #Generating Arrival Time Probabilities
    Arrival_count = pd.DataFrame(np.column_stack((times, number_arrivals)))
    Arrival_count.columns=['Time', 'Count']
    Arrival_count['Probs'] = Arrival_count['Count']/sum(list(Arrival_count['Count']))
    Arrival_count['Time'] = Arrival_count['Time'] - pd.to_datetime('today')
    Arrival_count[['Time', 'Probs']].to_csv('../csv_data_appendices/input_distributions/Arrival_sampling_'+str(every_n_minutes)+'.csv', sep=',')

    #Generating Duration on tarmac Probabilities
    Duration = pd.DataFrame(np.column_stack((stays, number_duration)))
    Duration.columns=['Time', 'Count']
    Duration['Probs'] = Duration['Count']/sum(list(Duration['Count']))
    Duration[['Time', 'Probs']].to_csv('../csv_data_appendices/input_distributions/Duration_sampling_'+str(every_n_minutes)+'.csv', sep=',')

    
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

        
print ('Approximating probability disitributions: DONE')       










