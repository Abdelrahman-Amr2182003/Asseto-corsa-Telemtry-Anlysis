import pandas as pd
import fastf1
from fastf1 import plotting
from matplotlib import pyplot as plt

# Enable the cache
fastf1.Cache.enable_cache('f1_cache')  # Define a cache directory path

# Load the session data
session = fastf1.get_session(2023, 'Bahrain', 'R')  # 'R' stands for the race session
session.load()

# Get telemetry data for a specific driver
driver = 'VER'  # Max Verstappen's driver code
laps = session.laps.pick_driver(driver)

# Combining all lap telemetry into a single DataFrame
all_telemetry = pd.DataFrame()  # Initialize an empty DataFrame
for lap in laps.iterlaps():
    telemetry = lap[1].get_telemetry()
    telemetry['LapNumber'] = lap[1]['LapNumber']
    all_telemetry = pd.concat([all_telemetry, telemetry], ignore_index=True)

# Example of plotting speed over time for all laps
plt.figure(figsize=(10, 6))
plt.plot(all_telemetry['Distance'], all_telemetry['Speed'], label='Speed (km/h)')
plt.title('Speed over Distance for Max Verstappen - 2021 Belgian GP')
plt.xlabel('Distance (m)')
plt.ylabel('Speed (km/h)')
plt.legend()
plt.show()

# Optionally, save this DataFrame to a CSV file
all_telemetry.to_csv('verstappen_bahrain_gp_2023_telemetry.csv', index=False)
