# Imports
import pandas as pd
import csv



#Converts CSV to dictionary
def csv2dict(directory, sep=',', main_cat=''):
    f = open(directory)
    reader = csv.reader(f, skipinitialspace=True, delimiter = sep)
    categories_found = 0
    dictionary = {}

    for row in reader:
        # In the case more than 1 characteristic is given in the csv
        if len(row) > 2:
            if not categories_found:
                categories = row
                try:
                    main_cat_index = row.index(main_cat)
                except:
                    main_cat_index = 0

                categories_found = 1
                
            else:
                sub_dict = {}
                for i in range(len(categories)):
                    if i != main_cat_index:
                        sub_dict.update({categories[i]:row[i]})
                    
                dictionary.update({row[main_cat_index]:sub_dict})


        # When 2 columns in csv, a direct dictionary is more applicable
        else:
            dictionary = dict(csv.reader(f, skipinitialspace=True, delimiter = sep))
    
    f.close()

    return dictionary




# Function to convert input_data variable from list to pandas dataframe
def inputs_list2dataframe(input_data):

    input_dataframe = pd.DataFrame.from_records(input_data)
    input_dataframe['ata'] = input_dataframe['ata'].dt.strftime('%H:%M (%d/%m)')
    input_dataframe['atd'] = input_dataframe['atd'].dt.strftime('%H:%M (%d/%m)')
    input_dataframe = input_dataframe[['flight index'    ,
                                       'airline'         ,
                                       'move type'       ,
                                       'Fl No. Arrival'  ,
                                       'ata'             ,
                                       'Fl No. Departure',
                                       'atd'             ,
                                       'long stay'       ,
                                       'night stay'      ,
                                       'connection'      ,
                                       'ac type'         ]]
    
    return input_dataframe









    
