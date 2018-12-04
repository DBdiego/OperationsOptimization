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


def generate_aircraft(use_existing, sample_size=10, every_n_minutes=12, show_result=0):

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


        # File Names
        file_AL_range_distr = base_directory + '/AL_domestic_international.csv'
        file_AC_type_distr  = base_directory + '/AC_type_distribution.csv'
        file_AL_code_distr  = base_directory + '/AL_code_distribution.csv'
        file_ATA_distr      = base_directory + '/Arrival_sampling_'  + str(every_n_minutes) + '.csv'
        file_STAY_distr     = base_directory + '/Duration_sampling_' + str(every_n_minutes) + '.csv'
        

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
        resolution = every_n_minutes * 60  #[seconds]
        
        number_intervals = datetime.timedelta(hours   = 6               )/  \
                           datetime.timedelta(minutes = every_n_minutes )

        time_deltas = []
        night_probs = []
        for k in range(int(number_intervals)):
            time_added = k * resolution
            night_prob = 1/( sigma * sqrt(2*pi) ) * e**( -((time_added - mu)**2)/(2*sigma**2) )
            
            time_deltas.append(datetime.timedelta(seconds=time_added))
            night_probs.append(night_prob)
            
        night_probs = list(np.array(night_probs)/np.sum(night_probs))


        # Other variables
        move_types = ['Arr', 'Park', 'Dep']
        tomorrow_midnight = midnight_today + datetime.timedelta(days=1)
        
        # Generating data
        count = 0
        generated_input_data = []
        for i in range(sample_size):
            
            # Random aircraft, time of arrival and duration of stay, Airline
            AC_type  = np.random.choice(AC_type_distr_prob [0], p = AC_type_distr_prob [1])
            Airline  = np.random.choice(AL_code_distr_prob [0], p = AL_code_distr_prob [1])
            AC_ATA   = np.random.choice(AC_ATA_distr_prob  [0], p = AC_ATA_distr_prob  [1])
            AC_STAY  = np.random.choice(AC_STAY_distr_prob [0], p = AC_STAY_distr_prob [1])

            # Random 'domestic' or 'international' flight
            connection_probs = [AL_connection_distr[Airline]['dom_probs'],
                                AL_connection_distr[Airline]['int_probs']]
            AL_connection = np.random.choice(['DOM', 'INT'], p = connection_probs)

            # Flight Number
            ref_number = np.random.randint(100, 999)
            flight_number_in  = Airline + str(ref_number)
            flight_number_out = Airline + str(ref_number + np.random.choice([-1, 1], p=[0.5, 0.5]))
            
            # Computing time of departure
            AC_ATD  = AC_ATA + AC_STAY


            # Night stay determination
            Night_stay = AC_ATA.date() < AC_ATD.date()

            # Adapting flight departure time if between midnight and 6AM
            if Night_stay and (AC_ATD > tomorrow_midnight) and ( (AC_ATD - tomorrow_midnight) < datetime.timedelta(hours=5, minutes=59) ):

                #Midnight + 6h + random extra time (normal distributed) #datetime.timedleta(days=1) 
                AC_ATD = tomorrow_midnight            + \
                         datetime.timedelta(hours=6)  + \
                         np.random.choice(time_deltas , p = night_probs)
                
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
                                             'Fl No. Departure':flight_number_out   ,
                                             })

    #Showing generated input to user
    if show_result:
        print ('GENERATED INPUT:')
        inputs_dataframe = CONV.inputs_list2dataframe(generated_input_data)
        print (inputs_dataframe, '\n')


    return generated_input_data





