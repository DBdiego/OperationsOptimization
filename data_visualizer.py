import matplotlib.pyplot as plt
import numpy as np
from math import *
import os

files = [x for x in os.listdir('./csv_data_appendices') if 'Simulation Case ' in x]
files.sort()
for file in files:
    print(file)

