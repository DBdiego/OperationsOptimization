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



'''
=============================== -- INFO -- ===============================
The required inputs generated for the model described in the report were
found on p.65 (paragraph above table 9.3)

The inputs randomly generated using probabilistic reproductions of the
input data used in the report. (see Probability_distribution.py for
more info)
==========================================================================
'''


def generate_aircraft(sample_size=10, every_n_minutes=20, show_result=0):

    # Inputs:
    #   sample_size     : Is the number of flights to be generated
    #   every_n_minutes : Is the size of the timeintervals of the probability
    #                     distribuion csv's
    

    # Directory definitions
    base_directory = '../csv_data_appendices/input_distributions'


    # File Names
    file_AC_type_distr = base_directory + '/AC_type_distribution.csv'
    file_ATA_distr     = base_directory + '/Arrival_sampling_'  + str(every_n_minutes) + '.csv'
    file_STAY_distr    = base_directory + '/Duration_sampling_' + str(every_n_minutes) + '.csv'


    # Reading Distributions    
    AC_type_distr = pd.read_csv(open( file_AC_type_distr ), sep=',') # --> AC Type
    AC_ATA_distr  = pd.read_csv(open( file_ATA_distr     ), sep=',') # --> AC ATA 
    AC_STAY_distr = pd.read_csv(open( file_STAY_distr    ), sep=',') # --> AC STAY


    
    # Time Conversions
    AC_ATA_distr ['Time'] = pd.to_timedelta(AC_ATA_distr ['Time']) + pd.to_datetime('today')
    AC_STAY_distr['Time'] = pd.to_timedelta(AC_STAY_distr['Time'])

    # Conversion to lists 
    AC_type_distr_prob = [list(AC_type_distr['AC Type']),
                          list(AC_type_distr['Probs'  ])]
    
    AC_ATA_distr_prob  = [list(AC_ATA_distr ['Time'   ]),
                          list(AC_ATA_distr ['Probs'  ])]
    
    AC_STAY_distr_prob = [list(AC_STAY_distr['Time'   ]),
                          list(AC_STAY_distr['Probs'  ])]



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


    
    # Generating data
    generated_input_data = []
    for i in range(sample_size):
        
        # Random aircraft, time of arrival and duration of stay
        AC_type = np.random.choice(AC_type_distr_prob[0], p = AC_type_distr_prob[1])
        AC_ATA  = np.random.choice(AC_ATA_distr_prob [0], p = AC_ATA_distr_prob [1])
        AC_STAY = np.random.choice(AC_STAY_distr_prob[0], p = AC_STAY_distr_prob[1])


        # Computing time of departure
        AC_ATD  = AC_ATA + AC_STAY


        # If the stay is longer than 5h40 => long stay
        Long_stay = AC_STAY > datetime.timedelta(hours=5, minutes=40)


        # If the stay is longer than 5h40 => long stay
        Night_stay = AC_ATA.date() < AC_ATD.date()

        # Adapting flight departure time if between midnight and 6AM
        if Night_stay and (AC_ATD - datetime.datetime.today() < datetime.timedelta(hours=5, minutes=59)):
            
            #Midnight + 6h + random extra time (normal distributed)
            AC_ATD = pd.to_datetime('today')      + \
                     datetime.timedelta(hours=6)  + \
                     np.random.choice(time_deltas , p = night_probs)

        
            
        # Saving generated data
        generated_input_data.append({'flight index': i          ,
                                     'ac type'     : AC_type    ,
                                     'ata'         : AC_ATA     ,
                                     'atd'         : AC_ATD     ,
                                     'long stay'   : Long_stay  ,
                                     'night stay'  : Night_stay ,
                                     'Fl No. Arrival'  :'KQ117' ,
                                     'Fl No. Departure':'KQ116' ,
                                     })

    #Showing generated input to user
    if show_result:
        print ('GENERATED INPUT:')
        pandas_inputs = pd.DataFrame.from_records(generated_input_data)
        pandas_inputs['ata'] = pandas_inputs['ata'].dt.strftime('%H:%M (%d/%m)')
        pandas_inputs['atd'] = pandas_inputs['atd'].dt.strftime('%H:%M (%d/%m)')
        pandas_inputs = pandas_inputs[['flight index', 'ac type', 'Fl No. Arrival', 'ata', 'Fl No. Departure', 'atd', 'long stay', 'night stay']]
        print (pandas_inputs, '\n')

    return generated_input_data



