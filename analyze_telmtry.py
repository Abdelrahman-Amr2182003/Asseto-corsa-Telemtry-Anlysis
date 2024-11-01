import os
import glob

import pandas
import matplotlib.pyplot as plt
dir = "outputs/New folder/*.csv"

col_name = "SpeedMs"
fig, axs = plt.subplots(4,2, figsize=(14, 11))
axs = axs.flatten()
colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan']
for i,(ax, name) in enumerate(zip(axs,glob.glob(dir))):
        print(name)
        df = pandas.read_csv(name)
        col = df[col_name]
        car_name = df['CarModel'][0]
        ax.plot(col)
        ax.set_title(car_name)
        ax.set_title(car_name, y=0.15, pad=-14)

plt.show()
