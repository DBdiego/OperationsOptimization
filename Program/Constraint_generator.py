# Imports
# --> Modules
import pandas as pd
import numpy as np
import time
import datetime
#import pulp

# --> Home made files
import Data_importer as DI



# [0] Importing data
aircraft_type2characteristics = DI.aircraft_type2characteristics
group2bay_compliance = DI.group2bay_compliance

all_bays = DI.all_bays


# [1] BAY COMPLIANCE Constraint
def add_bay_compliance(input_data, Bay_Assignment, flight_vars, fb=0):

    if fb:
        print ('  ---> Adding Bay Compliance Constraints ...')
    
    constraint_collection = {}
    number_constraints = 0
    
    #Going Through all flights
    for i, flight in enumerate(input_data):
        
        # Finding Compliant bays for the current flight
        group = aircraft_type2characteristics[flight['ac type']] ['Group']                                             
        compliant_bays = all_bays[np.array(group2bay_compliance[group])>0]

        # Defining constraint coefficient of constraint (for compliant bays)
        constraint = {}
        constraint_vars = []
        for j, bay in enumerate(compliant_bays):
            constraint_variable = 'x_' + str(i) + '_' + bay
            
            constraint.update({constraint_variable:1})
            constraint_vars.append(constraint_variable)
            
            
        constraint_collection.update({'BC'+str(i):{'constraint':constraint,
                                                   'variables' :constraint_vars}})
        
        #Bay_Assignment += pulp.lpSum([constraint[i]*flight_vars[i] for i in constraint_vars]) == 1, 'BC'+str(i)
        Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint[i]*flight_vars[i] for i in constraint_vars) == 1), ctname='BC'+str(i))
        
        number_constraints += 1

    if fb:
        print ('       Added '+str(number_constraints)+'\n')

    return Bay_Assignment, constraint_collection, number_constraints




# [2] TIME Constraint
def add_time_constraint(input_data, Bay_Assignment, flight_vars, Buffer_time, fb=0):

    if fb:
        print ('  ---> Adding Time Constraints ...')
    
    number_constraints = 0

    
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
                if (subject_arrival   <= comparator_data['atd'] + datetime.timedelta(minutes=Buffer_time)) and \
                   (subject_departure >= comparator_data['ata'] - datetime.timedelta(minutes=Buffer_time)) and \
                   (subject_data['Fl No. Arrival'] != comparator_data['Fl No. Arrival']):
                    
                    
                    time_conflict_matrix[i,j] = 1
                    time_conflict_matrix[j,i] = 1 #Not sure how usefull this is...

                    # Comparator Bay compliance
                    comparator_group = aircraft_type2characteristics[comparator_data['ac type']]['Group']
                    comparator_bays  = group2bay_compliance[comparator_group]

                    # Conflict Bays
                    if np.sum(subject_bays * comparator_bays) > 0:
                        
                        conflicting_bays = all_bays#[(subject_bays * comparator_bays) > 0]

                        # Creating a constraint for all conflict bays
                        for k, bay in enumerate(conflicting_bays):
                            constraint_name = 'TCI' + str(i) + 'O' + str(j) + 'B' + bay
                            
                            constraint_vars = ['x_' + str(i) + '_' + bay,
                                               'x_' + str(j) + '_' + bay]
                            constraint_coef = {'x_' + str(i) + '_' + bay: 1,
                                               'x_' + str(j) + '_' + bay: 1}
                            
                            #Bay_Assignment += pulp.lpSum([constraint_coef[i]*flight_vars[i] for i in constraint_vars]) <= 1, constraint_name
                            Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint_coef[i]*flight_vars[i] for i in constraint_vars) <= 1), ctname=constraint_name)

                            number_constraints += 1

    if fb:                            
        print ('       Added '+str(number_constraints)+'\n')
                            
    return Bay_Assignment, time_conflict_matrix,number_constraints





# [3] FUEL CONSTRAINT
#    Non serviceable bays : J7, J8, J9 and the STPV bays (STPV1/2)
def add_fuelling_constraint(input_data, Bay_Assignment, flight_vars, fb=0):

    if fb:
        print('  ---> Adding Fuelling Constraints ...')


    # Defining serviceable bays (STPV not removed because they don't even exist in the list of all bays)
    fuelling_bays = [x for x in all_bays if x not in ['J7', 'J8', 'J9']]
    non_fuelling_bays = [x for x in all_bays if x in ['J7', 'J8', 'J9']] #In case we downsize the model

    number_constraints = 0
    constraint_collection = {}

    # Going Through all flights
    for i, flight in enumerate(input_data):

        # Finding the flight type
        long_stay   = flight['long stay']
        move_type   = flight['move type']
        is_domestic = flight['connection']=='DOM'


        # Defining coefficient of constraint
        constraint = {}
        constraint_vars = []

    
        # Flight is move_type=='Full' or non-domestic during departure phase
        if move_type== 'Full' or (int(is_domestic) == 0 and move_type == 'Dep'):
            
            for j, bay in enumerate(non_fuelling_bays): #enumerate(fuelling_bays):
                
                constraint_variable = 'x_' + str(i) + '_' + bay

                constraint.update({constraint_variable: 1})
                constraint_vars.append(constraint_variable)

            #Bay_Assignment += pulp.lpSum([constraint[i] * flight_vars[i] for i in constraint_vars]) == 1, 'F' + str(i)
            Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint[i] * flight_vars[i] for i in constraint_vars) == 0), ctname='FC' + str(i))

            number_constraints += 1

            

        # Flight is in long stay (Just domestic during parking or departure phase)
        #   resulting in: (long_stay == 1 and domestic==1 and move_type=='Park'/'Dep') or ... ejected because we use i-1 in constraint
        if (long_stay == 1) and (is_domestic) and (move_type == 'Dep'):
            
            for j, bay in enumerate(non_fuelling_bays): #enumerate(fuelling_bays):
                constraint_vars = []
                constraint = {}
                
                #Take into account flight i (departure phase) and i-1 (parking phase)
                constraint_variables = ['x_' + str(i-1) + '_' + bay ,
                                        'x_' + str(i  ) + '_' + bay ]  

                constraint.update({constraint_variables[0]: 1,
                                   constraint_variables[1]: 1})

                constraint_vars = constraint_vars + constraint_variables

                #Bay_Assignment += pulp.lpSum([constraint[i] * flight_vars[i] for i in constraint_vars]) >= 1, 'F' + str(i)
                Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint[i] * flight_vars[i] for i in constraint_vars) <= 1), ctname='FCL' + str(i))
                

                number_constraints += 1

    if fb:
        print ('       Added '+str(number_constraints)+'\n')

    return Bay_Assignment, constraint_collection, number_constraints




# [4] SPLIT(TED) FLIGHT CONSTRAINT
def add_split_constraint(input_data, Bay_Assignment, flight_vars, fb=0):

    if fb:
        print ('  ---> Adding Split Flight Constraints ...')
    
    number_constraints = 0
    
    i = 0
    while i < len(input_data):


        if int(input_data[i]['move type'] == 'Full') == 0:

            for k, bay in enumerate(all_bays):
                # Defining coefficient of constraint
                constraint_1 = {}
                constraint_2 = {}
                constraint_vars_1 = []
                constraint_vars_2 = []


                constraint_variable_1 = 'x_' + str(i  ) + '_' + bay
                constraint_variable_2 = 'x_' + str(i+1) + '_' + bay
                constraint_variable_3 = 'x_' + str(i+2) + '_' + bay
                
                constraint_variable_4 = 'v_' + str(i  ) + '_' + bay
                constraint_variable_5 = 'v_' + str(i+1) + '_' + bay

                constraint_variable_6 = 'w_' + str(i+1) + '_' + bay
                constraint_variable_7 = 'w_' + str(i+2) + '_' + bay
                

                # Constraint 1
                constraint_1.update({constraint_variable_1:  1,
                                     constraint_variable_2: -1,
                                     constraint_variable_4: -1,#})
                                     constraint_variable_6:  1})
                constraint_vars_1 = constraint_vars_1 + [constraint_variable_1,
                                                         constraint_variable_2,
                                                         constraint_variable_4,#]
                                                         constraint_variable_6]

                # Constraint 2
                constraint_2.update({constraint_variable_2:  1,
                                     constraint_variable_3: -1,
                                     constraint_variable_5: -1,#})
                                     constraint_variable_7:  1})
                constraint_vars_2 = constraint_vars_2 + [constraint_variable_2,
                                                         constraint_variable_3,
                                                         constraint_variable_5,#]
                                                         constraint_variable_7]


                #Bay_Assignment += pulp.lpSum([constraint_1[l] * flight_vars[l] for l in constraint_vars_1]) == 0, 'SPF' + str(i  ) + 'B' + str(k) 
                #Bay_Assignment += pulp.lpSum([constraint_2[l] * flight_vars[l] for l in constraint_vars_2]) == 0, 'SPF' + str(i+1) + 'B' + str(k)
                
                Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint_1[l]*flight_vars[l] for l in constraint_vars_1) == 0), ctname='SPF' + str(i  ) + 'B' + str(k))
                Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint_2[l]*flight_vars[l] for l in constraint_vars_2) == 0), ctname='SPF' + str(i+1) + 'B' + str(k))
                


            

                number_constraints += 2
            
            i += 2 # To skip 'Park' & 'Dep'
        i += 1

    if fb:
        print ('       Added '+str(number_constraints)+'\n')

    return Bay_Assignment, number_constraints






# [5] ADJACENCY CONSTRAINT
def add_adjancy_constraint(input_data, Bay_Assignment, flight_vars, fb=0):

    if fb:
        print ('  ---> Adding Adjancy Constraints ...')

        
    time_departure_overlap    = np.zeros((len(input_data), len(input_data)))
    time_overlap_adjacent_bay = np.zeros((len(input_data), len(input_data)))

    number_constraints = 0
    
    # Find overlap in departure time between flights and note these flights
    for i in range(len(input_data)):

            # Defining the flight data and corresponding characteristics
            flight_data      = input_data[i]
            flight_departure = flight_data['atd']
            flight_arrival   = flight_data['ata']
            flight_type      = flight_data['move type']

            
            #check if the flight in question is departing or short stay
            if flight_type =='Full' or flight_type == 'Dep':
            
                for j, comparing_flight in enumerate(input_data):
                    
                    constraint1 = {}
                    constraint_vars1 = []
                    
                    constraint2 = {}
                    constraint_vars2 = []
                    
                    # Check if the flight in question (comparing flight) is departing or short stay
                    if (i < j) and (comparing_flight['move type'] in ['Full','Dep']):
                        
                        
                        # If comparator departure is within the stay of the subject flight, so there is overlap
                        if (flight_arrival <= comparing_flight['atd']) and (flight_departure  >= comparing_flight['ata']):
                            
                            # Now all the overlapping flights have an indication of 1.
                            time_departure_overlap[i,j] = 1
    
                            # Make constraints for bays 10 and 11 (share a gate)
                            constraint1.update({ 'x_' + str(i) + '_10' : 1 ,
                                                 'x_' + str(i) + '_11' : 1 ,
                                                 'x_' + str(j) + '_10' : 1 ,
                                                 'x_' + str(j) + '_11' : 1 })
        
                            constraint_vars1 = constraint_vars1 + ['x_' + str(i) + '_10' ,
                                                                   'x_' + str(i) + '_11' ,
                                                                   'x_' + str(j) + '_10' ,
                                                                   'x_' + str(j) + '_11' ]

                            #Bay_Assignment += pulp.lpSum([constraint1[k]*flight_vars[k] for k in constraint_vars1]) <= 1, 'ADJ1011I'+str(i)+'O'+str(j)
                            Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint1[k]*flight_vars[k] for k in constraint_vars1) <= 1),
                                                          ctname='ADJ1011I' + str(i) + 'O' + str(j) + 'B1011')


                            # Make constraints for bays 5 and 6 (share a gate)
                            constraint2.update({ 'x_' + str(i) + '_5' : 1 ,
                                                 'x_' + str(i) + '_6' : 1 ,
                                                 'x_' + str(j) + '_5' : 1 ,
                                                 'x_' + str(j) + '_6' : 1 })
        
                            constraint_vars2 = constraint_vars2 + [ 'x_' + str(i) + '_5' ,
                                                                    'x_' + str(i) + '_6' ,
                                                                    'x_' + str(j) + '_5' ,
                                                                    'x_' + str(j) + '_6' ]
                            
                            #Bay_Assignment += pulp.lpSum([constraint2[k]*flight_vars[k] for k in constraint_vars2]) <= 1, 'ADJ56I'+str(i)+'O'+str(j)
                            Bay_Assignment.add_constraint((Bay_Assignment.sum(constraint2[k]*flight_vars[k] for k in constraint_vars2) <= 1),
                                                          ctname='ADJ1011I' + str(i) + 'O' + str(j) + 'B0506')

                            number_constraints += 2

    if fb:
        print ('       Added '+str(number_constraints)+'\n')
    
    return Bay_Assignment, number_constraints



