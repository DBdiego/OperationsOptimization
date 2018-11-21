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
    
