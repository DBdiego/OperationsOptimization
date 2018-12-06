# Imports
# --> Modules
import pandas as pd
import numpy as np
import time

# --> Home made files
import Data_importer as DI


# Importing data
aircraft_type2characteristics = DI.aircraft_type2characteristics
group2bay_compliance = DI.group2bay_compliance
bay_distances        = DI.bay_distances
preferences          = DI.preferences

def coefficient_calculator(input_data, fb = 1):

    # Creating Variables
    coefficients = {}

    all_bays = DI.all_bays
    
    # Creating arrays for coefficients of the 2 objective functions
    max_possibilities = len(input_data)*len(all_bays)
    z1_coefficients = np.zeros(max_possibilities)
    z2_coefficients = np.zeros(max_possibilities)
    

    if fb:
        print ('Generating Coefficients & Weights: ...')
        start_time = time.time()


    # Determining coefficients of decision variables
    gobal_index = 0
    for i in range(len(input_data)):

        # Defining the inbound flight data
        flight_data = input_data[i]
        flight_number_arrival   = flight_data['Fl No. Arrival'  ]
        flight_number_departure = flight_data['Fl No. Departure']
        

        # Determining Aircraft Type Information
        aircraft_type      = flight_data['ac type'] 
        aircraft_capacity  = int(aircraft_type2characteristics[aircraft_type]['Capacity'])
        
        # Preference of Flight if any
        if flight_number_arrival in preferences['Fl No.'].unique():
            flight_index_pref = list(preferences['Fl No.']).index(flight_number_arrival)
            preference_bays = (preferences['Bay'].iloc[flight_index_pref]).split(',')
            
        elif flight_number_departure in preferences['Fl No.'].unique():
            flight_index_pref = list(preferences['Fl No.']).index(flight_number_departure)
            preference_bays = (preferences['Bay'].iloc[flight_index_pref]).split(',')
        else:
            preference_bays = []

        # Determining the reference point of the flight
        terminal_distances = bay_distances[['Bay', flight_data['terminal']]]
            
        # Loop over all possible bays
        for j, bay in enumerate(all_bays):
            

            # Find terminal Distance
            distance = int(terminal_distances.loc[terminal_distances['Bay'].isin([bay])].iloc[0, 1])

            # Calculating the weights
            max_distance_bay = max( list(bay_distances.loc[bay_distances['Bay'].isin([bay])].iloc[0, 1:]) )
            alpha = 1
            beta  = aircraft_capacity * max_distance_bay
            gamma = 1e9 #3 * beta     #max_distance_bay


            # Compute coefficient of first objective function
            z1_coefficients[gobal_index] = aircraft_capacity * distance

            if flight_data['move type']=='Park':
                coefficient = (aircraft_capacity * distance)*(-1) * alpha #0
            else:
                coefficient = (aircraft_capacity * distance)*(-1) * alpha

            # Coefficient of second objective function
            if j in preference_bays:
                z2_coefficients[gobal_index] = 1
                coefficient += 0 * beta
            else:
                z2_coefficients[gobal_index] = 0
                coefficient += 0 * beta




            # Assigning Coefficient to a decision variable name
            if flight_data['move type'] == 'Arr':
                coefficients.update({'x_' + str(i) + '_' + bay : coefficient ,
                                     'v_' + str(i) + '_' + bay : -gamma      ,
                                     'w_' + str(i+1) + '_' + bay : -gamma      })


            elif flight_data['move type'] == 'Park':
                #print('v_' + str(i) + '_' + bay)
                coefficients.update({'x_' + str(i) + '_' + bay : coefficient ,
                                     'v_' + str(i) + '_' + bay : -gamma      ,
                                     'w_' + str(i+1) + '_' + bay : -gamma      })


            elif flight_data['move type'] == 'Dep':
                coefficients.update({'x_' + str(i) + '_' + bay : coefficient })
                                     #'w_' + str(i) + '_' + bay : -gamma      })
                                
            else:
                
                coefficients.update({'x_' + str(i) + '_' + bay : coefficient })

            gobal_index += 1


    #Combingin both objective functions
    #final_coefficients = alpha * (-1* z1_coefficients) +\
    #                     beta  *      z2_coefficients

    if fb:
        print ('Generating Coefficients & Weights: DONE (' + str(round(time.time()-start_time, 3)) +' seconds)\n')
    
    return coefficients



