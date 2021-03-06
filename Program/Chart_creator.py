# Imports
# --> Modules
import pandas as pd
import numpy as np
import time
import datetime
import pulp

# --> Module classes
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.dates as mdates
from math import *

# --> Home made files
import Data_importer as DI
import Converters as CONV

all_bays = list(DI.all_bays)[::-1]
midnight_today = pd.to_datetime('today').replace(hour=0, minute=0, second=0, microsecond=0)
midnight_tomorrow = midnight_today + datetime.timedelta(days=1)

def generate_charts(input_dataframe, output_dataframe, towings_dataframe, solve_status, fb=1):

    

    #Ground Times of aircraft
    ground_time_ranges = assign_time_data2FN(input_dataframe, sort_category='ata', ascending=False)
    gant_chart_ground(ground_time_ranges, 'Ground Times', show=0, save=1, fb=1)
    
    if solve_status.lower() == 'optimal':
        gant_chart_bays(input_dataframe, 'Bay Assignment Full' , Full=1.0, Arr=0.2, Park=0.2, Dep=0.2,  show=0, save=1, fb=1)
        gant_chart_bays(input_dataframe, 'Bay Assignment Arr'  , Full=0.2, Arr=1.0, Park=0.2, Dep=0.2,  show=0, save=1, fb=1)
        gant_chart_bays(input_dataframe, 'Bay Assignment Park' , Full=0.2, Arr=0.2, Park=1.0, Dep=0.2,  show=0, save=1, fb=1)
        gant_chart_bays(input_dataframe, 'Bay Assignment Dep'  , Full=0.2, Arr=0.2, Park=0.2, Dep=1.0,  show=0, save=1, fb=1)
        gant_chart_bays(input_dataframe, 'Bay Assignment All'  , Full=1.0, Arr=1.0, Park=1.0, Dep=1.0,  show=1, save=1, fb=1)




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
    
    

def gant_chart_ground(input_data, chart_title, show=0, save=1, fb=1):
    
    if show or save:
        if fb:
            print ('  ---> Gant Chart: Ground Times ...')
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





def gant_chart_bays(input_data, chart_title, Full=0.8, Arr=0.8, Park=0.8, Dep=0.8, show=0, save=1, fb=1):

    
    
    rect_height = 0.65

    edge_full = '#000000'
    edge_arr  = '#1464F4'
    edge_park = '#32AD32'
    edge_dep  = '#FF0000'
    
    fill_dom  = '#C6BC99' #'#DDD9C4'  #'#C6BC99' #'#6C6C6C'
    fill_int  = '#E5E5E5' #'#F0F0F0'
    
    text_dom  = '#2C2C2C'
    text_int  = '#3C3C3C'
    
    if show or save:
        if fb:
            print ('  ---> Gant Chart: ' + chart_title + ' ...')

        # Plot Characteristics
        fig_size_unit_x, fig_size_unit_y = [18,(0.20 * len(all_bays))]
        
        fig = plt.figure(figsize=(fig_size_unit_x, fig_size_unit_y))
        ax  = fig.add_subplot(111)
        
        myFmt = mdates.DateFormatter('%Hh')


        max_atd = datetime.datetime(1900, 12, 1)
        min_ata = midnight_today
        
        previous_bay_index = midnight_today
        for flight_data in input_data.to_dict('records'):
            bay_index = all_bays.index(flight_data['Bay'])

            # Characteristics
            move_type = flight_data['move type']
            ata = pd.to_datetime(flight_data['ata'], format='%H:%M (%d/%m)')
            atd = pd.to_datetime(flight_data['atd'], format='%H:%M (%d/%m)')

            ata = ata.replace(year= int(pd.to_datetime('today').year) )
            atd = atd.replace(year= int(pd.to_datetime('today').year) )

            
            # Domestic of International
            if flight_data['connection'] == 'DOM':
                fill_color = fill_dom 
                text_color = text_dom
                
            else:
                fill_color = fill_int
                text_color = text_int



            # Color and times of arrival & departure
            if move_type.lower() == 'full':
                edge_color = edge_full
                alpha_line = Full

                # Adding flight index
                ax.text( ata + (atd-ata)/2, bay_index+1 ,
                         flight_data['Fl No. Arrival']  ,
                         verticalalignment = 'center'   ,
                         horizontalalignment = 'center' ,
                         fontsize = 6                   ,
                         color = text_color             ,
                         zorder = 12                     )

            elif move_type.lower() == 'arr':
                edge_color = edge_arr
                alpha_line = Arr
                
            else:
                # Dotted line between parts of split flight
                if previous_bay_index != bay_index:
                    ax.plot([ata, ata], [previous_bay_index+1, bay_index+1], c = 'black', lw=0.8, ls=':', alpha = min(Arr, Park, Dep), zorder=  20)

                    
                if move_type.lower() == 'park':
                    edge_color = edge_park
                    alpha_line = Park

                    # Adding flight index
                    ax.text( ata + (atd-ata)/2, bay_index+1 ,
                             flight_data['Fl No. Arrival']  ,
                             verticalalignment = 'center'   ,
                             horizontalalignment = 'center' ,
                             fontsize = 6                   ,
                             color = text_color             ,
                             zorder = 12                     )
                    
                else:
                    edge_color = edge_dep
                    alpha_line = Dep

            
            # Plotting the rectangles
            Rect = patches.Rectangle((ata,(bay_index+1)-rect_height/2),
                                     (atd-ata)                        ,
                                     rect_height                      ,   
                                     linewidth = 0.8                  ,
                                     edgecolor = edge_color           ,
                                     facecolor = fill_color           ,
                                     alpha = alpha_line               ,
                                     zorder = 10                       )
            
            # Add the patch to the Axes
            ax.add_patch(Rect)

            
            previous_bay_index = bay_index
            

            if atd > max_atd:
                max_atd = atd

            if ata < min_ata:
                min_ata = ata


        
        #Other plot characteristics          
        ax.set_title(chart_title)
        
        ax.xaxis.set_major_formatter(myFmt)
        ax.xaxis.set_major_locator(mdates.HourLocator())
        
        ax.set_yticks(range(1, len(all_bays)+1))
        ax.set_yticklabels(all_bays, fontsize=10)
        
        ax.set_ylabel('Bays')
        ax.set_xlabel('Time')

        midnight_start = datetime.datetime(min_ata.year, min_ata.month, min_ata.day, hour=0, minute=0, second=0, microsecond=0)
        midnight_end   = datetime.datetime(max_atd.year, max_atd.month, max_atd.day, hour=0, minute=0, second=0, microsecond=0)

        ax.set_xlim([midnight_start, max_atd + datetime.timedelta(minutes=45)])

        #Legend
        full_stay_patch = patches.Patch(linewidth = 0.8, edgecolor = edge_full, facecolor = 'none' ,alpha = Full, label='Full stay'     )
        arr_stay_patch  = patches.Patch(linewidth = 0.8, edgecolor = edge_arr , facecolor = 'none' ,alpha = Arr , label='Arrival stay'  )
        park_stay_patch = patches.Patch(linewidth = 0.8, edgecolor = edge_park, facecolor = 'none' ,alpha = Park, label='Parking stay'  )
        dep_stay_patch  = patches.Patch(linewidth = 0.8, edgecolor = edge_dep , facecolor = 'none' ,alpha = Dep , label='Departure stay')

        dom_stay_patch  = patches.Patch(linewidth = 0.8, edgecolor = 'none', facecolor = fill_dom ,alpha = 0.8, label='Domestic Flight'      )
        int_stay_patch  = patches.Patch(linewidth = 0.8, edgecolor = 'none', facecolor = fill_int ,alpha = 0.8, label='International Flight' )
        
        
        ax.legend(handles=[full_stay_patch,
                           arr_stay_patch ,
                           park_stay_patch,
                           dep_stay_patch ,
                           dom_stay_patch ,
                           int_stay_patch ], loc='lower left')

        #Remove useless part of the box
        ax.spines[  'top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        #Others
        plt.grid(axis = 'x', alpha = 0.8, zorder = 0)   
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.99, top=0.94, wspace=0.1, hspace=0.4)

        ax.axvspan(midnight_start,
                   midnight_start + datetime.timedelta(hours=6) ,
                   facecolor='#0A0A0A',
                   alpha = 0.2        ,
                   zorder = 8         )

        ax.axvspan(midnight_end,
                   midnight_end + datetime.timedelta(hours=6) ,
                   facecolor='#0A0A0A',
                   alpha = 0.2        ,
                   zorder = 8         )



        # Horizontal grid lines (Hightlighting exception bays such as non-servicable and single gate)
        alpha_highlight_gridlines = min([Full, Arr, Park, Dep])
        for i in range(len(all_bays)):
            if i in [all_bays.index(x) for x in all_bays if x in ['J7', 'J8', 'J9']]:
                ax.plot([midnight_start, max_atd],[i+1, i+1], c='r', ls='--', lw=0.5, alpha=alpha_highlight_gridlines)
                
            elif i in [all_bays.index(x) for x in all_bays if x in ['5', '6', '10', '11']]:
                ax.plot([midnight_start, max_atd],[i+1, i+1], c='b', ls='--', lw=0.5, alpha=alpha_highlight_gridlines)
                
            else:
                ax.plot([midnight_start, max_atd],[i+1, i+1], c='k', ls='--', lw=0.3, alpha=0.2)

            
        
        if save:
            plt.savefig('./outputs/'+ chart_title.replace(' ', '_') + '.pdf')
        
        if show:
            plt.show()
        else:
            plt.close()
        
    






def time_bar_chart(data_x, data_y, chart_title,
                   resolution=5,
                   fill_color='#0000FF',
                   edge_color='#000000',
                   labelx_format='%Hh' ,
                   xlabel = ''         ,
                   ylabel = ''         ,
                   show = 1            ,
                   save = 0            ,
                   add_start_x = 0     ,
                   add_end_x   = 0     ): 

    if show or save:
        # Plotting    
        half_bar_width = datetime.timedelta(minutes=resolution)/4
        opacity   = 1

        fill_color = fill_color
        edge_color = edge_color 

        myFmt = mdates.DateFormatter(labelx_format)

        
        fig = plt.figure(figsize=(12, 6))
        ax  = fig.add_subplot(111)
        
        
        # Prob bars
        max_time = midnight_today
        for i in range(len(data_x)):
            
            duration    = data_x.iloc[i] + midnight_today #duration_data['Time' ].iloc[i] + today_midnight
            probability = data_y.iloc[i]                  #duration_data['Probs'].iloc[i]
            
            Rect = patches.Rectangle((duration - half_bar_width,0),
                                     half_bar_width*2           ,
                                     probability*100            ,   
                                     linewidth = 0.8            ,
                                     edgecolor = edge_color     ,
                                     facecolor = fill_color     ,
                                     alpha     = opacity        ,
                                     zorder    = 10             )
            
            if probability > 0 and duration > max_time:
                max_time = duration
            
            # Add the patch to the Axes
            ax.add_patch(Rect)

        #ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.HourLocator())
        ax.xaxis.set_major_formatter(myFmt)

        ax.set_xlim([midnight_today + datetime.timedelta(seconds=add_start_x),
                     max_time       + datetime.timedelta(seconds=add_end_x  )])
        ax.set_ylim([0,max(list(data_y))*100*1.05])

        # Setting title
        ax.set_title(chart_title + ' (every ' + str(resolution) + ' min)', fontsize=20)

        # Setting axis labels
        ax.set_xlabel(xlabel, fontsize=15)
        ax.set_ylabel(ylabel, fontsize=15)

        #Remove useless part of the box
        ax.spines[  'top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='both', labelsize=13)
        ax.tick_params(axis='x', rotation=45)

        #Others
        plt.grid(alpha = 0.8, zorder = 0)   
        plt.subplots_adjust(left=0.07, bottom=0.15, right=0.97, top=0.93, wspace=0.1, hspace=0.4)
        
        
        if save:
            plt.savefig('./outputs/'+ chart_title.replace(' ', '_') + '.pdf')

        if show:
            plt.show()
        else:
            plt.close()

            
