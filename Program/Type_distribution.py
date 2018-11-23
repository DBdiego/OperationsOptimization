import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import os

from datetime import datetime
import datetime
from math import *

# Imported data from data_importer script
import data_importer as DI


total_num_flights = len(DI.imported_data['Fl No. Arrival'].unique())

'''
A = DI.imported_data['Flight Type'].value_counts()
B = DI.imported_data['Flight Type'].value_counts().iloc[3]


# Split data into 'full' flights and 'split' flights
full_flight_indices = []
split_flight_indices = []

for i in range(len(DI.imported_data)):
    if DI.imported_data['Flight Type'].iloc[i] == 'Full':
        full_flight_indices.append(i)
    else:
        split_flight_indices.append(i)


full_flights = DI.imported_data.iloc[full_flight_indices]
split_flights = DI.imported_data.iloc[split_flight_indices]
'''

# Aircraft type distribution
AC_count = pd.DataFrame(DI.local_result['AC Type'].value_counts().reset_index())
AC_count.columns = ['AC Type', 'Count']

AC_count['Probs'] = AC_count['Count']/sum(list(AC_count['Count']))
AC_count = AC_count[['AC Type', 'Probs']]

AC_count.to_csv('../csv_data_appendices/AC_type_distribution.csv')
'''
np.random.choice
'''



