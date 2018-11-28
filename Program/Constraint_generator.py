# Imports
# --> Modules
import pandas as pd
import numpy as np
import time
import pulp

# --> Home made files
import Data_importer as DI



# Importing data
aircraft_type2characteristics = DI.aircraft_type2characteristics
group2bay_compliance = DI.group2bay_compliance

all_bays = np.array(group2bay_compliance['Bay'])


# BAY COMPLIANCE Constraint
def add_bay_compliance(input_data, Bay_Assignement, flight_vars):
    
    print ('  ---> Adding Bay Compliance Constraints ...')
    
    constraint_collection = {}
    
    #Going Through all flights
    for i, flight in enumerate(input_data):
        
        # Finding Compliant bays for the current flight
        group = aircraft_type2characteristics[flight['ac type']] ['Group']                                             
        compliant_bays = all_bays[np.array(group2bay_compliance[group])>0]

        # Defining constraint coefficient of constraint (for compliant bays)
        constraint = {}
        constraint_vars = []
        for j, bay in enumerate(compliant_bays):
            constraint_variable = str(i) + '_' + bay
            
            constraint.update({constraint_variable:1})
            constraint_vars.append(constraint_variable)
            
        constraint_collection.update({'BC'+str(i):{'constraint':constraint,
                                                   'variables' :constraint_vars}})
        Bay_Assignement += pulp.lpSum([constraint[i]*flight_vars[i] for i in constraint_vars]) == 1, 'BC'+str(i)

    return Bay_Assignement, constraint_collection




# TIME Constraint
def add_time_constraint(input_data, Bay_Assignement, flight_vars):
    
    print ('  ---> Adding Time Constraints ...')

    #Creation of matrix
    time_conflict_matrix = np.zeros((len(input_data), len(input_data)))

    #Comparing a subject flight to all other flights it has not been checked with yet (i < j)
    for i, subject_data in enumerate(input_data):
        # Subject times
        subject_arrival   = subject_data['ata']
        subject_departure = subject_data['atd']

        # Subject Bay compliance
        subject_group = aircraft_type2characteristics[subject_data['ac type']]['Group']
        subject_bays  = group2bay_compliance[subject_group]
        
        for j, comparator_data in enumerate(input_data):
            if (i < j):
                
                # if comparator arrival is within the stay of the subject flight
                if subject_arrival < comparator_data['ata'] < subject_departure:

                    time_conflict_matrix[i,j] = 1
                    time_conflict_matrix[j,i] = 1 #Not sure how usefull this is...

                    # Comparator Bay compliance
                    comparator_group = aircraft_type2characteristics[comparator_data['ac type']]['Group']
                    comparator_bays  = group2bay_compliance[comparator_group]

                    # Conflict Bays
                    if np.sum(subject_bays * comparator_bays) > 0:
                        
                        conflicting_bays = all_bays[(subject_bays * comparator_bays) > 0]

                        # Creating a constraint for all conflict bays
                        for k, bay in enumerate(conflicting_bays):
                            constraint_name = 'TCI'+str(i)+'O'+str(j)+'B'+bay
                            
                            constraint_vars = [str(i)+'_'+bay, str(j)+'_'+bay]
                            constraint_coef = {str(i)+'_'+bay: 1,
                                               str(j)+'_'+bay: 1}
                            Bay_Assignement += pulp.lpSum([constraint_coef[i]*flight_vars[i] for i in constraint_vars]) <= 1, constraint_name

    return Bay_Assignement, time_conflict_matrix





# FUEL Constraint
#Non serviceable bays : J7, J8, J9 and the STPV bays (STPV1/2)
def add_fuelling_constraint(input_data, Bay_Assignement, flight_vars):
    print('  ---> Adding Fuelling Constraints ...')

    constraint_collection = {}

    # Going Through all flights
    for i, flight in enumerate(input_data):

        # Finding the flight type
        long_stay = flight['long stay']
        move_type = flight['move type']
        domestic  = flight['connection']=='DOM'


        # Defining serviceable bays
        bay_list = list(group2bay_compliance['Bay'])
        bay_list.remove('J7')
        bay_list.remove('J8')
        bay_list.remove('J9')
            # STPV not removed because they don't even exist in the list of all bays

        fuelling_bays = bay_list

        # Defining coefficient of constraint
        constraint = {}
        constraint_vars = []

        # Flight is move_type=='Full' or non-domestic during departure phase
        if move_type== 'Full' or (domestic == 0 and move_type == 'Dep'): 

            for j, bay in enumerate(fuelling_bays):
                constraint_variable = str(i) + '_' + bay

                constraint.update({constraint_variable: 1})
                constraint_vars.append(constraint_variable)

            constraint_collection.update({'F' + str(i): {'constraint': constraint,
                                                          'variables': constraint_vars}})
            Bay_Assignement += pulp.lpSum([constraint[i] * flight_vars[i] for i in constraint_vars]) == 1, 'F' + str(i)

        # Flight is in long stay (Just domestic during parking or departure phase)
        #   resulting in: (long_stay == 1 and domestic==1 and move_type=='Park') or ... ejected because we use i-1 in constraint
        if (long_stay == 1 and domestic==1 and move_type=='Dep'): 

            for j, bay in enumerate(fuelling_bays):
                constraint_variables = [str(i-1) + '_' + bay , str(i) + '_' + bay]  #Take into account flight i (departure phase) and i-1 (parking phase)

                constraint.update({constraint_variables[0]: 1, constraint_variables[1]: 1})

                constraint_vars.append(constraint_variables[0])
                constraint_vars.append(constraint_variables[1])

            constraint_collection.update({'F' + str(i): {'constraint': constraint,
                                                          'variables': constraint_vars}})
            Bay_Assignement += pulp.lpSum([constraint[i] * flight_vars[i] for i in constraint_vars]) >= 1, 'F' + str(i)


    return Bay_Assignement, constraint_collection
