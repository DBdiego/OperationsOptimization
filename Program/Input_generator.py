import matplotlib.dates  as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import os

import datetime
from math import *

# Imported data from data_importer script
import data_importer as DI

# Directory definition
base_directory = '../csv_data_appendices/input_distributions'

# Reading AC type distribution
AC_type_distr = pd.read_csv(open(base_directory+'/AC_type_distribution.csv'), sep=',')

# Reading AC ATA distribution
time_slot_size = '10.csv'     
AC_ATA_distr = pd.read_csv(open(base_directory+'/arrival_sampling_'+time_slot_size), sep=',')
AC_ATA_distr['Time'] = pd.to_datetime(AC_ATA_distr['Time'])

AC_type = np.random.choice(list(AC_type_distr['AC Type']), p=list(AC_type_distr['Probs']))
AC_ATA = np.random.choice(list(AC_ATA_distr['Time']), p=list(AC_ATA_distr['Probs']))
