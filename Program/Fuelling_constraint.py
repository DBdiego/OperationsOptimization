#Non serviceable bays : J7, J8, J9 and the STPV bays (STPV1/2)

def add_fuelling_constraint(input_data, Bay_Assignement, flight_vars):
    print('  ---> Adding Fuelling Constraints ...')

    constraint_collection = {}

    # Going Through all flights
    for i, flight in enumerate(input_data):

        # Finding the flight type
        long_stay = flight['long stay']
        move_type=flight['move type']
        domestic=(flight['connection']=='DOM')

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

        if move_type== 'Full' or (domestic == 0 and move_type == 'Dep'): #Flight is move_type=='Full' or non-domestic during departure phase

            for j, bay in enumerate(fuelling_bays):
                constraint_variable = str(i) + '_' + bay

                constraint.update({constraint_variable: 1})
                constraint_vars.append(constraint_variable)

            constraint_collection.update({'F' + str(i): {'constraint': constraint,
                                                          'variables': constraint_vars}})
            Bay_Assignement += pulp.lpSum([constraint[i] * flight_vars[i] for i in constraint_vars]) == 1, 'F' + str(i)


        if (long_stay == 1 and domestic==1 and move_type=='Dep'): #Flight is in long stay (Just domestic during parking or departure phase) / long_stay == 1 and domestic==1 and move_type=='Park') or ... ejected because we use i-1 in constraint

            for j, bay in enumerate(fuelling_bays):
                constraint_variables = [str(i-1) + '_' + bay , str(i) + '_' + bay] #Take into account flight i (departure phase) and i-1 (parking phase)

                constraint.update({constraint_variables[0]: 1, constraint_variables[1]: 1})

                constraint_vars.append(constraint_variables[0])
                constraint_vars.append(constraint_variables[1])

            constraint_collection.update({'F' + str(i): {'constraint': constraint,
                                                          'variables': constraint_vars}})
            Bay_Assignement += pulp.lpSum([constraint[i] * flight_vars[i] for i in constraint_vars]) == 1, 'F' + str(i)


    return Bay_Assignement, constraint_collection