import mmap
import os
import struct
import math
import time
import json
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from AssetoReader import AssettoCorsaData
from CarData import  CarData
import os
import mplcyberpunk

plt.style.use("cyberpunk")
#car_name = "ks_bmw_m4"
#car_name = "ks_mclaren_p1"
#car_name = "ks_ferrari_f2004"
car_name = None
asseto_corsa_dir = "C:/Program Files (x86)/Steam/steamapps/common/assettocorsa"
time_stamp = 0.1
#plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
def format_time(tenths_of_seconds):
    # Convert tenths of seconds to minutes, seconds, and hundredths of a second
    minutes = tenths_of_seconds // 60000
    seconds = (tenths_of_seconds // 1000) % 60
    hundredths = tenths_of_seconds % 1000
    # Format the time string
    return str(f"{minutes:01d}:{seconds:02d}:{hundredths:03d}")
def capture_data(reader, data_list, x_list, metrics_lists, columns_ref,car_data):
    i = 0
    while True:
        data = reader.getData()
        #print('Assetto data:', data)
        if not data:
            continue  # Skip iteration if data is empty




        torque, power = car_data.get_torque_and_power_at_rpm(data.get('rpms',0))
        data['engine_torque'] = float(torque)
        data['engine_power'] = float(power)
        data['Time'] = round(float(i),2)
        #data['currentTime'] = format_time(data['iCurrentTime'])

        data_values = list(data.values())
        #print(data)
        data_list.append(data_values)
        x_list.append(i)
        #print(data.get('turboBoost',0))
        # Append data for each metric
        for key, y_list in metrics_lists.items():
            if key=='torque':
                y_list.append(torque)
            else:
                y_list.append(data.get(key, 0))

        if columns_ref['columns'] is None:
            columns_ref['columns'] = list(data.keys())

        time.sleep(time_stamp)
        i += time_stamp
        global stop_threads
        if stop_threads:
            break


def save_excel(data, columns, filename):
    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)


    # Reorder 'Time' column
    time_col = df.pop('Time')
    df.insert(1, 'Time', time_col)
    # Apply the format_time function
    df['currentTime'] = df['iCurrentTime'].apply(format_time)

    # Verify changes
    #print(df[['iCurrentTime', 'currentTime']])

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


def update_plot(frame, x_list, metrics_lists, lines, window_size=500):
    # Decide whether to use a fixed window or all data based on the amount of data collected
    if len(x_list) > window_size:
        # More data than window size, plot only the recent data for scrolling effect
        for metric, line in zip(metrics_lists.keys(), lines):
            y_list = metrics_lists[metric]
            line.set_data(x_list[-window_size:], y_list[-window_size:])
            line.axes.set_xlim(x_list[-window_size], x_list[-1])
            line.axes.relim()
            line.axes.autoscale_view()
    else:
        # Not enough data for scrolling, plot all data
        for metric, line in zip(metrics_lists.keys(), lines):
            y_list = metrics_lists[metric]
            line.set_data(x_list, y_list)
            line.axes.relim()
            line.axes.autoscale_view()

    return lines
def on_close(event):
    print("Closing figure and saving...")
    event.canvas.figure.savefig('outputs/dashboard_AC_12.png')

    print("Figure saved.")

if __name__ == '__main__':

    try:
        reader = AssettoCorsaData()
        reader.start()
        initial_data = None
        while initial_data is None:
            initial_data = reader.getData()
        car_name = initial_data['carModel']
        print(car_name)

        stop_threads = False
        car_data = CarData(asseto_corsa_dir, car_name)
        rpm_range = np.linspace(car_data.power_data.df['rpms'].min(), car_data.power_data.df['rpms'].max(), 100)

        # Calculate torque and power across the RPM range
        torque_values = car_data.torque_interp(rpm_range)
        power_values = car_data.power_interp(rpm_range)


        columns_ref = {'columns': None}
        data = []
        x= []
        metrics = {
            'speedKmh': [],
            'rpms': [],
            'brake': [],
            'gear': [],
            'torque':[],

        }

        # Set up the plot with subplots in a 2x2 grid
        fig, axs = plt.subplots(2, 3, figsize=(15, 10))  # Adjust figsize as needed
        fig.canvas.mpl_connect('close_event', on_close)

        axs = axs.flatten()  # Flatten the array to easily iterate over it
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan']
        titles = ['Speed (km/h)', 'Engine RPM', 'Brakes', 'Gear',"Torque(Nm)","Torque & Power characteristics Curve"]
        lines = [axs[i].plot(x, metrics[key], '-o', color=colors[i])[0] for i, key in enumerate(metrics) if
                 key in ['speedKmh', 'rpms', 'brake', 'gear','torque']]

        for i, (ax, title) in enumerate(zip(axs, titles)):
            ax.set_title(title)
            if title == 'Torque & Power characteristics Curve':
                ax.plot(rpm_range, torque_values, label='Torque (Nm)', color='blue')
                ax.plot(rpm_range, power_values, label='Power (bhp)', color='red')
                ax.set_title('Torque & Power characteristics Curve')
                ax.set_xlabel('RPM')
                ax.set_ylabel('Torque (Nm) / Power (bhp)')
                ax.legend()
                ax.grid(True)


        # Start the data capture in a separate thread
        data_thread = threading.Thread(target=capture_data, args=(reader, data, x, metrics, columns_ref,car_data))
        data_thread.start()

        ani = FuncAnimation(fig, update_plot, fargs=(x, metrics, lines, 500), blit=False, interval=1000)
        mplcyberpunk.add_glow_effects()
        plt.show()

        # Once the plot is closed, stop the data capture and save the data
        stop_threads = True
        data_thread.join()
        if columns_ref['columns'] is not None and data:
            # Convert the list of values to a list of dictionaries
            data_dicts = [dict(zip(columns_ref['columns'], row)) for row in data]
            save_excel(data_dicts, columns_ref['columns'], 'outputs/outputs_AC_12.csv')
        exit()
    except KeyboardInterrupt:
        stop_threads = True
        data_thread.join()
        plt.savefig('outputs/dashboard_AC_12.png')
        if columns_ref['columns'] is not None and data:
            # Convert the list of values to a list of dictionaries
            data_dicts = [dict(zip(columns_ref['columns'], row)) for row in data]
            save_excel(data_dicts, columns_ref['columns'], 'outputs/outputs_AC_12.csv')

            print("saved_fig")
