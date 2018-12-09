# Imports
# --> Modules
import pandas as pd
import numpy as np
import datetime

# --> Module classes
import matplotlib.patches as patches
import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
from scipy.stats import norm
from math import *

# --> Home made files
import Data_importer as DI
import Chart_creator as ChC


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
    - Domestic/International Flight
==========================================================================
'''

imported_data   = DI.simulation_cases['01']
appendix_result = DI.appendix_result
total_num_flights = len(imported_data['Fl No. Arrival'].unique())

base_directory = '../csv_data_appendices/input_distributions/'

if 1:
    


    print ('Approximating probability disitributions: ...')



    ### [1] AIRCRAFT TYPE
    # Count
    AC_count = pd.DataFrame(appendix_result['AC Type'].value_counts().reset_index())
    AC_count.columns = ['AC Type', 'Count']

    # Discrete Probabilities
    AC_count['Probs'] = AC_count['Count']/sum(list(AC_count['Count']))
    AC_type_probs = AC_count[['AC Type', 'Probs']]

    # Writing to file
    #AC_type_probs.to_csv(base_directory + 'AC_type_distribution.csv', sep=',', index=False)




    ### [2] AIRLINE CODE DISTR
    # Count
    airlines = pd.DataFrame(imported_data['Fl No. Arrival'].unique())[0].str[:2]
    AL_count = pd.DataFrame(airlines.value_counts().reset_index())
    AL_count.columns = ['AL Code', 'Count']

    # Discrete Probabilities
    AL_count['Probs'] = AL_count['Count']/sum(list(AL_count['Count']))
    AL_probs = AL_count[['AL Code', 'Probs']]

    # Writing to file
    #AL_probs.to_csv(base_directory + 'AL_code_distribution.csv', sep=',', index=False)




    ### [3] DOMESTIC - INTERNATIONAL PROBABILITIES
    # Selecting Required data
    imported_data_flights = imported_data[['Fl No. Arrival'  ,
                                           'Origin'          ,
                                           'Fl No. Departure',
                                           'Dest'           ]].drop_duplicates().reset_index()
    Airports = pd.read_csv(open('../csv_data_appendices/Airports.csv'  ), sep=',')
    domestic_airport_codes = list(Airports[Airports['Country']=='Kenya']['Airport Code'])

    # Counting occurences
    airline_dom_int = {}
    for i, flight_number in enumerate(list(imported_data_flights['Fl No. Arrival'])):
        try:
            airline = flight_number[:2]
            
            if not (airline in airline_dom_int):
                airline_dom_int.update({airline:{'dom_count' : 0, 'int_count' : 0}})
                                
            flight_origin = imported_data_flights['Origin'].iloc[i]
            
            if flight_origin in domestic_airport_codes:
                airline_dom_int[airline]['dom_count'] += 1
            else:
                airline_dom_int[airline]['int_count'] += 1
                
        except TypeError:
            pass

    # Conversion to dict for a pandas dataframe
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

    # Writing to file
    AL_probs_dom_int = AL_DOM_INT[['airline', 'dom_probs', 'int_probs']]
    #AL_probs_dom_int.to_csv(base_directory + 'Al_domestic_international.csv', sep=',', index=False)




    ### TIME SAMPLING
    # Creating a time frame in which flights can be grouped
    def create_time_array(every_n_minutes):
        time_array = []
        num_hour_interv = 24
        num_min_interv  = int(60/every_n_minutes)
        for hour in range(num_hour_interv):
            for minute in range(num_min_interv):
                time = datetime.datetime.today().replace(hour=hour, minute=minute*every_n_minutes, second=0, microsecond=0)
                time_array.append(time)

        return np.array(time_array)


    # Creating a stay-time frame in which fligth stay durations can be grouped
    def create_stays_array(every_n_minutes, aircraft_data):
        stay_timedeltas = []
        stay_array = np.arange(0, (1440+every_n_minutes)*60, every_n_minutes*60)
        for stay_int in stay_array:
            stay_timedeltas.append(datetime.timedelta(seconds=float(stay_int)))
        return stay_timedeltas

            
    # Putting data in the according frame interval (a.k.a. bucket)
    def sampler(sample_mold, to_be_sampeled):
        count = np.zeros(len(sample_mold))
        for i, sample in enumerate(to_be_sampeled):
            for j in range(1, len(sample_mold)):
                if sample_mold[j-1] < sample <= sample_mold[j]:
                    count[j] += 1
      
        return count


    # Getting Arrival and Departure times of flight numbers (split flights will be combined as one)
    arrival_times   = []
    departure_times = []
    flight_numbers  = list(imported_data['Fl No. Arrival'].unique())

    for i, flight_number in enumerate(flight_numbers):
        
        flight_data = imported_data[imported_data['Fl No. Arrival'] == flight_number]
        
        if len(flight_data) == 1:
            ata = list(pd.to_datetime(flight_data['ATA']))[0]
            atd = list(pd.to_datetime(flight_data['ATD']))[0]
            
        elif len(flight_data) > 1:
            ata = list(pd.to_datetime(flight_data[flight_data['Flight Type']=='Arr']['ATA']))[0]
            atd = list(pd.to_datetime(flight_data[flight_data['Flight Type']=='Dep']['ATD']))[0]

        if atd < ata:
            atd = atd + datetime.timedelta(days=1)

        arrival_times  .append(ata)
        departure_times.append(atd)


            
        
    # Count & Probablity of Long Stays
    aircraft_stay = []
    count = 0
    for i in range(len(arrival_times)):
        duration = departure_times[i] - arrival_times[i]
        
        if duration < datetime.timedelta(hours=1):
            duration = datetime.timedelta(hours=1, minutes=np.random.randint(15))
        if duration > datetime.timedelta(hours=5, minutes=40):
            count += 1
        

        aircraft_stay.append(duration)

    #print (round(100*count/len(arrival_times), 2), '% of flights are "long stay" flights\n')



    print ('Time Sampling')
    # Sampling the arrival times and stay durations
    for every_n_minutes in [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30]:
        print ('   |---> every ' + str(every_n_minutes) + ' minutes ...')

        # Generating Sampling 'molds' (in which data is classified/sampled)
        times = create_time_array (every_n_minutes)
        stays = create_stays_array(every_n_minutes, aircraft_stay)
        
        # Sampling the imported data
        number_arrivals   = sampler(times, arrival_times   )
        number_departures = sampler(times, departure_times )
        number_duration   = sampler(stays, aircraft_stay   )

        # Generating Arrival Time Probabilities
        Arrival_count = pd.DataFrame(np.column_stack((times, number_arrivals)))
        Arrival_count.columns=['Time', 'Count']
        Arrival_count['Probs'] = Arrival_count['Count']/sum(list(Arrival_count['Count']))
        Arrival_count['Time'] = Arrival_count['Time'] - pd.to_datetime('today')
        #Arrival_count[['Time', 'Probs']].to_csv(base_directory + 'Arrival_sampling_'+str(every_n_minutes)+'.csv', sep=',', index=False)

        # Generating Duration on tarmac Probabilities
        Duration = pd.DataFrame(np.column_stack((stays, number_duration)))
        Duration.columns=['Time', 'Count']
        Duration['Probs'] = Duration['Count']/sum(list(Duration['Count']))
        #Duration[['Time', 'Probs']].to_csv(base_directory + 'Duration_sampling_'+str(every_n_minutes)+'.csv', sep=',', index=False)


        ChC.time_bar_chart(Arrival_count['Time'], Arrival_count['Probs'],
                           'Arrival Time Probability Distribution',
                           resolution=every_n_minutes,
                           fill_color='#4F81BD'    ,
                           edge_color='#4F81BD'    ,
                           xlabel='Arrival Time'   ,
                           ylabel='Probability [%]',
                           add_end_x   = 1800      ,
                           show = 1,
                           save = 0)


            
    print ('Approximating probability disitributions: DONE')       


#################### INPUT DATA SHARELATEX PLOTS ######################
duration_data = pd.read_csv(open(base_directory + 'Duration_sampling_'+ str( 5)+'.csv'), sep=',')
arrival_data  = pd.read_csv(open(base_directory + 'Arrival_sampling_' + str(30)+'.csv'), sep=',')

duration_data['Time'] = pd.to_timedelta(duration_data['Time'])
arrival_data ['Time'] = pd.to_timedelta(arrival_data ['Time'])

midnight_today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)


# Probability Distribution for Arrival Times
ChC.time_bar_chart(arrival_data['Time'], arrival_data['Probs'],
                   'Arrival Time Probability Distribution',
                   resolution = 30           ,
                   fill_color = '#4F81BD'    ,
                   edge_color = '#4F81BD'    ,
                   xlabel = 'Arrival Time'   ,
                   ylabel = 'Probability [%]',
                   add_end_x = 1800      ,
                   show = 0,
                   save = 1)



# Probability Distribution for Ground Times
ChC.time_bar_chart(duration_data['Time'], duration_data['Probs'],
                   'Ground Time Probability Distribution',
                   resolution = 5            ,
                   fill_color = '#C0504D'    ,
                   edge_color = '#C0504D'    ,
                   xlabel = 'Time on Ground' ,
                   ylabel = 'Probability [%]',
                   add_start_x = 3000        ,
                   add_end_x   = 1800        ,
                   show = 0,
                   save = 1)




