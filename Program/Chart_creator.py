# Imports
# --> Modules
import pandas as pd
import numpy as np
import time
import datetime

# --> Module classes
import matplotlib.dates  as mdates
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from math import *

# --> Home made files
import Data_importer as DI
import Converters as CONV

all_bays = list(DI.all_bays)[::-1]
midnight_today = pd.to_datetime('today').replace(hour=0, minute=0, second=0, microsecond=0)

def generate_charts(input_dataframe, output_dataframe, towings_dataframe):

    #Ground Times of aircraft
    ground_time_ranges = assign_time_data2FN(input_dataframe, sort_category='ata', ascending=False)
    gant_chart_ground(ground_time_ranges, 'Ground Times', show=0, save=1)

    gant_chart_bays(input_dataframe, 'Bay Assignment', show=1, save=1)




def assign_time_data2FN(input_dataframe, sort_category='', ascending=True):
    
    unique_flight_numbers = list(input_dataframe['Fl No. Arrival'].unique())
    FN_to_times = []
    for i, flight_number in enumerate(unique_flight_numbers):

        flight_number_index = list(input_dataframe['Fl No. Arrival']).index(flight_number)


        #Color and times of arrival & departure
        move_type = input_dataframe['move type'].iloc[flight_number_index]

        if move_type.lower() == 'full':
            ata = pd.to_datetime(input_dataframe['ata'].iloc[flight_number_index], format='%H:%M (%d/%m)')
            atd = pd.to_datetime(input_dataframe['atd'].iloc[flight_number_index], format='%H:%M (%d/%m)')
            
        else:
            ata = pd.to_datetime(input_dataframe['ata'].iloc[flight_number_index  ], format='%H:%M (%d/%m)')
            atd = pd.to_datetime(input_dataframe['atd'].iloc[flight_number_index+2], format='%H:%M (%d/%m)')

        ata = ata.replace(year = int(pd.to_datetime('today').year) )
        atd = atd.replace(year = int(pd.to_datetime('today').year) )
        
        FN_to_times.append({'Fl No. Arrival': flight_number,
                            'ata'           : ata          ,
                            'atd'           : atd          ,
                            'move type'     : move_type    })

    FN_to_times = pd.DataFrame(FN_to_times)

    # Sorting if wanted to
    if sort_category != '':
        FN_to_times.sort_values(by=sort_category, ascending=ascending, inplace=True)
        
    return FN_to_times
    
    

def gant_chart_ground(input_data, chart_title, show=0, save=1):

    if show or save:
        
        # Initial Values
        unique_flight_numbers = list(input_data['Fl No. Arrival'].unique())


        # Plot Characteristics
        fig_size_unit_x, fig_size_unit_y = [18,(0.20 * len(unique_flight_numbers))]
        
        fig = plt.figure(figsize=(fig_size_unit_x, fig_size_unit_y))
        ax  = fig.add_subplot(111)
        
        myFmt = mdates.DateFormatter('%H:%M')

        
        for i in range(input_data.shape[0]):

            # Characteristics
            move_type = input_data['move type'].iloc[i]
            ata = input_data['ata'].iloc[i]
            atd = input_data['atd'].iloc[i]

            # Color and times of arrival & departure
            if move_type.lower() == 'full':
                color = 'blue'
                label = 'short stay'
                
            else:
                color = 'red'
                label = 'long stay'

            #Ploting the data
            ax.plot([midnight_today, ata],[i+1, i+1], c='k', ls='--', lw=0.3, alpha=0.2)
            ax.plot([ata, atd],[i+1, i+1], c=color, lw=1.5)
            

        
        #Other plot characteristics          
        ax.set_title(chart_title)
        
        ax.xaxis.set_major_formatter(myFmt)
        
        ax.set_yticks(range(1, len(unique_flight_numbers)+1))
        ax.set_yticklabels(unique_flight_numbers, fontsize=10)
        
        ax.set_ylabel('Flight Numbers')
        ax.set_xlabel('Time')

        #Legend
        short_stay_line = mlines.Line2D([],[], color='b', label='short stay')
        long_stay_line  = mlines.Line2D([],[], color='r', label='long stay' )
        ax.legend(handles=[short_stay_line, long_stay_line],loc='lower left')

        #Remove useless part of the box
        ax.spines[  'top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        #Others
        plt.grid(axis = 'x', alpha = 0.8, zorder = 0)   
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.99, top=0.94, wspace=0.1, hspace=0.4)


        if save:
            plt.savefig('./outputs/'+ chart_title.replace(' ', '_') + '.pdf')
        
        if show:
            plt.show()
        else:
            plt.close()





def gant_chart_bays(input_data, chart_title, show=0, save=1):
    
    if show or save:

        # Plot Characteristics
        fig_size_unit_x, fig_size_unit_y = [18,(0.20 * len(all_bays))]
        
        fig = plt.figure(figsize=(fig_size_unit_x, fig_size_unit_y))
        ax  = fig.add_subplot(111)
        
        myFmt = mdates.DateFormatter('%H:%M')


        max_atd = midnight_today
        previous_bay_index = midnight_today
        for flight_data in input_data.to_dict('records'):
            bay_index = all_bays.index(flight_data['Bay'])

            #Characteristics
            move_type = flight_data['move type']
            ata = pd.to_datetime(flight_data['ata'], format='%H:%M (%d/%m)')
            atd = pd.to_datetime(flight_data['atd'], format='%H:%M (%d/%m)')

            ata = ata.replace(year= int(pd.to_datetime('today').year) )
            atd = atd.replace(year= int(pd.to_datetime('today').year) )


            # Color and times of arrival & departure
            if move_type.lower() == 'full':
                color = 'black'

            elif move_type.lower() == 'arr':
                color = 'blue'
                
            else:
                if previous_bay_index != bay_index:
                    ax.plot([ata, ata], [previous_bay_index+1, bay_index+1], c = 'black', lw=0.5, ls='--')

                    
                if move_type.lower() == 'park':
                    color = 'green'
                    
                else:
                    color = 'red'
            
            
            ax.plot([ata, atd],[bay_index+1, bay_index+1], c=color, lw=1, alpha=0.8)
            
            previous_bay_index = bay_index
            

            if atd > max_atd:
                max_atd = atd

        
        for i in range(len(all_bays)):
            ax.plot([midnight_today, max_atd],[i+1, i+1], c='k', ls='--', lw=0.3, alpha=0.2)
            

        
        #Other plot characteristics          
        ax.set_title(chart_title)
        
        ax.xaxis.set_major_formatter(myFmt)
        
        ax.set_yticks(range(1, len(all_bays)+1))
        ax.set_yticklabels(all_bays, fontsize=10)
        
        ax.set_ylabel('Bays')
        ax.set_xlabel('Time')

        ax.set_xlim([midnight_today, max_atd + datetime.timedelta(minutes=45)])

        #Legend
        full_stay_line = mlines.Line2D([],[], color='black', label='Full stay')
        arr_stay_line  = mlines.Line2D([],[], color='blue' , label='Arrival stay')
        park_stay_line = mlines.Line2D([],[], color='green', label='Parking stay')
        dep_stay_line  = mlines.Line2D([],[], color='red'  , label='Departure stay' )
        
        ax.legend(handles=[full_stay_line,
                           arr_stay_line ,
                           park_stay_line,
                           dep_stay_line ],loc='lower left')

        #Remove useless part of the box
        ax.spines[  'top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        #Others
        plt.grid(axis = 'x', alpha = 0.8, zorder = 0)   
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.99, top=0.94, wspace=0.1, hspace=0.4)


        if save:
            plt.savefig('./outputs/'+ chart_title.replace(' ', '_') + '.pdf')
        
        if show:
            plt.show()
        
    






            
