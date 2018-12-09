# Imports
# --> Modules
import pandas as pd
import numpy as np
import datetime
import os

# --> Module classes
import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
from math import *

# Home made files
import Converters as CONV



'''
=============================== -- INFO -- ===============================
The required inputs generated for the model described in the report were
found on p.65 (paragraph above table 9.3)

The inputs randomly generated using probabilistic reproductions of the
input data used in the report. (see Probability_distribution.py for
more info)
==========================================================================
'''


def generate_aircraft(use_existing, sample_size=10, resolution_ata=30, resolution_stay=5, show_result=0):

    # Inputs:
    #   use_existing    : Is a boolean telling the program to import an existing file or generating new data
    #   sample_size     : Is the number of flights to be generated
    #   every_n_minutes : Is the size of the timeintervals of the probability
    #                     distribuion csv's

    # If an existing file is wanted
    if use_existing:
        all_files = [x for x in os.listdir('./inputs') if x[0] != '.']

        if len(all_files) == 1:
            selected_file = all_files[0]
            
        else:
            print('  Select Input Data file')
            for i, file_name in enumerate(all_files):
                print('\t'+ str(i+1) + ')  ' + file_name)
            print('  !! to avoid a selection, only place 1 csv file in the "inputs" folder !!')
            user_input = input('  Type the number next to the desired file:  ')
            print()
            selected_file = all_files[int(user_input) - 1]
                      

        input_dataframe = pd.read_csv(open('./inputs/' + selected_file), sep=',')
        input_dataframe['ata'] = pd.to_datetime(input_dataframe['ata'], format='%H:%M (%d/%m)')
        input_dataframe['atd'] = pd.to_datetime(input_dataframe['atd'], format='%H:%M (%d/%m)')

        generated_input_data = input_dataframe.to_dict('records')


    else:

        # Directory definitions
        base_directory = '../csv_data_appendices/input_distributions'
        every_n_minutes_ATA  = resolution_ata
        every_n_minutes_STAY = resolution_stay        

        # File Names
        file_AL_range_distr = base_directory + '/AL_domestic_international.csv'
        file_AC_type_distr  = base_directory + '/AC_type_distribution.csv'
        file_AL_code_distr  = base_directory + '/AL_code_distribution.csv'
        file_ATA_distr      = base_directory + '/Arrival_sampling_'  + str(every_n_minutes_ATA ) + '.csv'
        file_STAY_distr     = base_directory + '/Duration_sampling_' + str(every_n_minutes_STAY) + '.csv'
        

        # Reading Distributions    
        AC_type_distr  = pd.read_csv(open( file_AC_type_distr  ), sep=',') # --> AC Type
        AL_code_distr  = pd.read_csv(open( file_AL_code_distr  ), sep=',') # --> AIRLINE
        AC_ATA_distr   = pd.read_csv(open( file_ATA_distr      ), sep=',') # --> AC ATA 
        AC_STAY_distr  = pd.read_csv(open( file_STAY_distr     ), sep=',') # --> AC STAY

        AL_connection_distr = CONV.csv2dict( file_AL_range_distr, sep=',') # --> DOMESTIC/INTERNATIONAL

        
        # Time Conversions
        midnight_today = pd.to_datetime('today').replace(hour=0, minute=0, second=0, microsecond=0)
        AC_ATA_distr ['Time'] = pd.to_timedelta(AC_ATA_distr ['Time']) + midnight_today
        AC_STAY_distr['Time'] = pd.to_timedelta(AC_STAY_distr['Time'])

        # Conversion to lists 
        AC_type_distr_prob  = [list(AC_type_distr ['AC Type']),
                               list(AC_type_distr ['Probs'  ])]

        AL_code_distr_prob  = [list(AL_code_distr ['AL Code']),
                               list(AL_code_distr ['Probs'  ])]
        
        AC_ATA_distr_prob   = [list(AC_ATA_distr  ['Time'   ]),
                               list(AC_ATA_distr  ['Probs'  ])]
        
        AC_STAY_distr_prob  = [list(AC_STAY_distr ['Time'   ]),
                               list(AC_STAY_distr ['Probs'  ])]


        # Night Stay exeption in probability
        sigma      = 5400                  #[seconds] standard deviation is 1h30
        mu         = 5400                  #[seconds] in 1h30
        resolution = resolution_stay * 60  #[seconds]

        # Number of intervals between 6AM and 12:00
        number_intervals = datetime.timedelta(hours   = 6               )/  \
                           datetime.timedelta(minutes = resolution_stay )

        time_deltas = []
        night_probs = []
        for k in range(int(number_intervals)):
            time_added = k * resolution
            night_prob = 1/( sigma * sqrt(2*pi) ) * e**( -((time_added - mu)**2)/(2*sigma**2) )
            
            time_deltas.append(datetime.timedelta(seconds=time_added))
            night_probs.append(night_prob)
            
        night_probs = list(np.array(night_probs)/np.sum(night_probs))
        
        time_deltas.append(datetime.timedelta(seconds=0))  # for interval randomisation later
        night_probs.append(0)                              # for interval randomisation later

        

        # Other variables
        move_types = ['Arr', 'Park', 'Dep']
        tomorrow_midnight = midnight_today + datetime.timedelta(days=1)
        
        # Generating data
        count = 0
        generated_input_data = []
        used_flight_numbers = []
        for i in range(sample_size):
            
            # Random aircraft, time of arrival and duration of stay, Airline
            AC_type = np.random.choice(AC_type_distr_prob [0], p = AC_type_distr_prob [1])
            Airline = np.random.choice(AL_code_distr_prob [0], p = AL_code_distr_prob [1])
            AC_ATA_inter  = np.random.choice(AC_ATA_distr_prob [0][:-1], p = AC_ATA_distr_prob [1][:-1])
            AC_STAY_inter = np.random.choice(AC_STAY_distr_prob[0][:-1], p = AC_STAY_distr_prob[1][:-1])

            # Random ATA within interval
            ACA_ATA_int_index = AC_ATA_distr_prob[0].index(AC_ATA_inter)
            AC_ATA_int_delta = AC_ATA_distr_prob[0][ACA_ATA_int_index+1] - AC_ATA_distr_prob[0][ACA_ATA_int_index]
            AC_ATA = AC_ATA_inter + np.random.random() * AC_ATA_int_delta
            #AC_ATA.replace(second=0, microsecond=0)

            # Random STAY within interval
            ACA_STAY_int_index = AC_STAY_distr_prob[0].index(AC_STAY_inter)
            AC_STAY_int_delta = AC_STAY_distr_prob[0][ACA_STAY_int_index+1] - AC_STAY_distr_prob[0][ACA_STAY_int_index]
            AC_STAY = AC_STAY_inter + np.random.random() * AC_STAY_int_delta
            #AC_STAY = ((midnight_today + AC_STAY).replace(second=0, microsecond=0))-midnight_today
            

            # Random 'domestic' or 'international' flight
            connection_probs = [AL_connection_distr[Airline]['dom_probs'],
                                AL_connection_distr[Airline]['int_probs']]
            AL_connection = np.random.choice(['DOM', 'INT'], p = connection_probs)
            if Airline =='KQ':
                if AL_connection =='DOM':
                    terminal_ref = 'A'
                else:
                    terminal_ref = 'D'
            else:
                terminal_ref = np.random.choice(['B', 'C'], p=[0.5, 0.5])
                

            # Flight Number
            ref_number = np.random.randint(100, 999)
            while ref_number in used_flight_numbers: #Checking for doubles
                ref_number = np.random.randint(100, 999)
                
            flight_number_in  = Airline + str(ref_number)
            flight_number_out = Airline + str(ref_number + np.random.choice([-1, 1], p=[0.5, 0.5]))
            
            used_flight_numbers.append(ref_number)
            
            # Computing time of departure
            AC_ATD  = AC_ATA + AC_STAY


            # Night stay determination
            Night_stay = AC_ATA.date() < AC_ATD.date()

            # Adapting flight departure time if between midnight and 6AM
            if Night_stay and (tomorrow_midnight < AC_ATD) and ( (AC_ATD - tomorrow_midnight) < datetime.timedelta(hours=5, minutes=59) ):

                random_time_added_inter = np.random.choice(time_deltas[:-1] , p = night_probs[:-1])
                random_time_added_int_ind = time_deltas.index(random_time_added_inter)
                random_time_added_int_delta = time_deltas[random_time_added_int_ind+1]-time_deltas[random_time_added_int_ind]
                random_time_added = time_deltas[random_time_added_int_ind] + np.random.random() * random_time_added_int_delta
                
                #Midnight + 6h + random extra time (normal distributed) #datetime.timedleta(days=1) 
                AC_ATD = tomorrow_midnight            + \
                         datetime.timedelta(hours=6)  + \
                         random_time_added  #np.random.choice(time_deltas , p = night_probs)
                
                AC_STAY = AC_ATD - AC_ATA


            # If the stay is longer than 5h40 => long stay (a.ka. splitTED flight)
            Long_stay = AC_STAY > datetime.timedelta(hours=5, minutes=40)


            # Saving generated data (in case of long stay, the flight is split)
            if Long_stay:
                count += 1
                
                time_arrival_procedure   = np.random.randint(30, 90) # [minutes]
                time_departure_procedure = np.random.randint(30, 90) # [minutes]

                time_intervals = {move_types[0]:[AC_ATA, AC_ATA + datetime.timedelta(minutes=time_arrival_procedure)],
                                  move_types[1]:[AC_ATA + datetime.timedelta(minutes=time_arrival_procedure  ),
                                                 AC_ATD - datetime.timedelta(minutes=time_departure_procedure)],
                                  move_types[2]:[AC_ATD - datetime.timedelta(minutes=time_departure_procedure), AC_ATD]}
                
                for move_type in move_types:
                    generated_input_data.append({'flight index': i            ,
                                                 'move type'   : move_type    ,
                                                 'airline'     : Airline      ,
                                                 'ac type'     : AC_type      ,
                                                 'ata'         : time_intervals[move_type][0],
                                                 'atd'         : time_intervals[move_type][1],
                                                 'long stay'   : Long_stay    ,
                                                 'night stay'  : Night_stay   ,
                                                 'connection'  : AL_connection, 
                                                 'Fl No. Arrival'  :flight_number_in  ,
                                                 'Fl No. Departure':flight_number_out ,
                                                 'terminal'    : terminal_ref
                                                 })
                
            else:
                generated_input_data.append({'flight index': i            ,
                                             'move type'   : 'Full'       ,
                                             'airline'     : Airline      ,
                                             'ac type'     : AC_type      ,
                                             'ata'         : AC_ATA       ,
                                             'atd'         : AC_ATD       ,
                                             'long stay'   : Long_stay    ,
                                             'night stay'  : Night_stay   ,
                                             'connection'  : AL_connection, 
                                             'Fl No. Arrival'  :flight_number_in   ,
                                             'Fl No. Departure':flight_number_out  ,
                                             'terminal'    : terminal_ref
                                             })

    #Showing generated input to user
    if show_result:
        print ('GENERATED INPUT:')
        inputs_dataframe = CONV.inputs_list2dataframe(generated_input_data)
        print (inputs_dataframe, '\n')


    return generated_input_data





