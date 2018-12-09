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

preference_keys = preferences['Fl No.'].unique()

def coefficient_calculator(input_data, fb = 1):

    # Creating Variables
    coefficients = {}
    pass_kpi_coeffs = {}
    pref_kpi_coeffs = {}
    tows_kpi_coeffs = {}

    all_bays = DI.all_bays
    
    # Creating arrays for coefficients of the 2 objective functions
    max_possibilities = len(input_data)*len(all_bays)
    

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
        flight_airline          = flight_data['airline']
        

        # Determining Aircraft Type Information
        aircraft_type      = flight_data['ac type'] 
        aircraft_capacity  = int(aircraft_type2characteristics[aircraft_type]['Capacity'])
        
        # Preference of Flight if any
        preference_bays = []
        if flight_number_arrival in preference_keys:
            flight_index_pref = list(preferences['Fl No.']).index(flight_number_arrival)
            preference_bays = (preferences['Bay'].iloc[flight_index_pref]).split(';')
            
        elif flight_number_departure in preference_keys:
            flight_index_pref = list(preferences['Fl No.']).index(flight_number_departure)
            preference_bays = (preferences['Bay'].iloc[flight_index_pref]).split(';')
        
        elif flight_airline in preference_keys:
            flight_index_pref = list(preferences['Fl No.']).index(flight_airline)
            preference_bays = (preferences['Bay'].iloc[flight_index_pref]).split(';')
            
            



        # Determining the reference point of the flight
        terminal_distances = bay_distances[['Bay', flight_data['terminal']]]

        # Loop over all possible bays
        for j, bay in enumerate(all_bays):
            

            # Find terminal Distance
            distance = int(terminal_distances.loc[terminal_distances['Bay'].isin([bay])].iloc[0, 1])

            # Calculating the weights
            max_distance_bay = max( list(bay_distances.loc[bay_distances['Bay'].isin([bay])].iloc[0, 1:]) )
            alpha = 1
            beta  = 2 * aircraft_capacity * max_distance_bay
            gamma = 3 * aircraft_capacity * max_distance_bay #beta     #max_distance_bay


            # Compute coefficient of first objective function
            
            if flight_data['move type'] in ['Arr', 'Park']:
                pass_coeff = 0  #(aircraft_capacity * distance)*(-1) * alpha
            else:
                pass_coeff = (aircraft_capacity * distance)*(-1) * alpha


            # Coefficient of second objective function
            if bay in preference_bays:
                pref_coeff = beta
            else:
                pref_coeff = 0

            if pref_coeff + pass_coeff == 0:
                coefficient = 1
            else:
                coefficient = 0
                
            coefficient += pass_coeff
            coefficient += pref_coeff




            # Assigning Coefficient to a decision variable name
            if flight_data['move type'] == 'Arr':
                coefficients.update({'x_' + str(i  ) + '_' + bay : coefficient ,
                                     'v_' + str(i  ) + '_' + bay : -gamma      ,
                                     'w_' + str(i+1) + '_' + bay : -gamma      })
                
                tows_kpi_coeffs.update({'v_' + str(i  ) + '_' + bay : gamma  ,
                                        'w_' + str(i+1) + '_' + bay : gamma  })
                
            elif flight_data['move type'] == 'Park':
                coefficients.update({'x_' + str(i  ) + '_' + bay : coefficient ,
                                     'v_' + str(i  ) + '_' + bay : -gamma      ,
                                     'w_' + str(i+1) + '_' + bay : -gamma      })
                
                tows_kpi_coeffs.update({'v_' + str(i  ) + '_' + bay : gamma  ,
                                        'w_' + str(i+1) + '_' + bay : gamma  })


            elif flight_data['move type'] == 'Dep':
                coefficients.update({'x_' + str(i) + '_' + bay : coefficient })
                                
            else:
                coefficients.update({'x_' + str(i) + '_' + bay : coefficient })


            # KPI's
            pass_kpi_coeffs.update({'x_' + str(i) + '_' + bay : -pass_coeff })
            pref_kpi_coeffs.update({'x_' + str(i) + '_' + bay :  pref_coeff })
            

            gobal_index += 1






    if fb:
        print ('Generating Coefficients & Weights: DONE (' + str(round(time.time()-start_time, 3)) +' seconds)\n')
    
    return coefficients, [pass_kpi_coeffs, pref_kpi_coeffs, tows_kpi_coeffs]



