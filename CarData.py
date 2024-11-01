import json
import pandas as pd
import numpy as np
import os
from configparser import ConfigParser
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
def torque_to_power(torque, rpm):
    bhp_to_watts = 745.699872
    return rpm * torque / (bhp_to_watts / np.pi / 2 * 60)
class PowerData:
    def __init__(self,power_dir):
        self.power_dir = power_dir
        self.df = None
        self.torque_vals = None
        self.rpm_vals = None
        self.parse_power_lut()
    def parse_power_lut(self):
        self.df = pd.read_csv(self.power_dir, sep='|', header=None)
        self.df.columns = ['rpms',"torque"]
        self.df = self.df[self.df['rpms']>=0]
        self.torque_vals = self.df['torque']
        self.rpm_vals = self.df['rpms']
class Turbo:
    def __init__(self,config,name):
        self.config = config
        self.name = name
        self.max_boost = None
        self.reference_rpm = None
        self.lag_dn = None
        self.lag_up = None
        self.waste_gate = None
        self.gamma = None
        self.dispaly_max_boost = None
        self.cock_pit_adjustable = None
        self.set_turbo_data()
    def set_turbo_data(self):
        self.max_boost = float(self.config[self.name]['MAX_BOOST'].split()[0])
        self.reference_rpm = float(self.config[self.name]['REFERENCE_RPM'].split()[0])
        self.lag_dn = float(self.config[self.name]['LAG_DN'].split()[0])
        self.lag_up = float(self.config[self.name]['LAG_UP'].split()[0])
        self.wastegate = float(self.config[self.name]['WASTEGATE'].split()[0])
        self.gamma = float(self.config[self.name]['GAMMA'].split()[0])
        self.display_max_boost = float(self.config[self.name]['DISPLAY_MAX_BOOST'].split()[0])
        self.cockpit_adjustable = int(self.config[self.name]['COCKPIT_ADJUSTABLE'].split()[0])
    def calculate_multiplier(self, rpm):
        return min(self.wastegate, self.max_boost * min(1.0, np.power(rpm / self.reference_rpm, self.gamma)))


class EngineData:
    def __init__(self,engine_dir):
        self.engine_dir = engine_dir
        self.turbos = None
        self.parse_engine()
    def parse_engine(self):
        self.engine = ConfigParser()
        self.engine.read(self.engine_dir)
        self.get_turbos_data()
    def get_turbos_data(self):
        self.turbos = dict()
        for section in self.engine.sections():
            if section.startswith('TURBO_'):
                self.turbos[section] = Turbo(self.engine,section)



class CarData:
    def __init__(self,asseto_corsa_dir,car_name):
        self.asseto_corsa_dir = asseto_corsa_dir
        self.car_name = car_name
        self.power_dir = os.path.join(asseto_corsa_dir, 'content', 'cars', car_name, 'data', 'power.lut')
        self.engine_dir = os.path.join(asseto_corsa_dir, 'content', 'cars', car_name, 'data', 'engine.ini')
        self.power_data = PowerData(self.power_dir)
        self.engine_data = EngineData(self.engine_dir)
        self.calculate_torque_power_curves()

    def calculate_torque_power_curves(self):
        # Apply turbo multipliers to adjust torque for each RPM point
        adjusted_torque = self.power_data.df['torque'].copy()
        for _, turbo in self.engine_data.turbos.items():
            adjusted_torque *= 1.0 + self.power_data.df['rpms'].apply(turbo.calculate_multiplier)

        # Calculate power using the adjusted torque values
        power = torque_to_power(adjusted_torque, self.power_data.df['rpms'])

        # Create interpolation functions for torque and power
        self.torque_interp = interp1d(self.power_data.df['rpms'], adjusted_torque)
        self.power_interp = interp1d(self.power_data.df['rpms'], power)



    def get_torque_and_power_at_rpm(self,rpm):
        # Use the interpolation functions to estimate torque and power at the given RPM
        torque = self.torque_interp(rpm)
        power = self.power_interp(rpm)
        return torque, power

if __name__ == '__main__':
    car_name = "ks_bmw_m4"
    asseto_corsa_dir = "C:/Program Files (x86)/Steam/steamapps/common/assettocorsa"
    car_data = CarData(asseto_corsa_dir,car_name)

    rpm_range = np.linspace(car_data.power_data.df['rpms'].min(), car_data.power_data.df['rpms'].max(), 100)

    # Calculate torque and power across the RPM range
    torque_values = car_data.torque_interp(rpm_range)
    power_values = car_data.power_interp(rpm_range)

    # Plotting
    plt.figure(figsize=(10, 6))

    plt.plot(rpm_range, torque_values, label='Torque (Nm)', color='blue')
    plt.plot(rpm_range, power_values, label='Power (bhp)', color='red')

    plt.title('Engine Performance: Torque and Power vs RPM')
    plt.xlabel('RPM')
    plt.ylabel('Torque (Nm) / Power (bhp)')
    plt.legend()
    plt.grid(True)
    plt.show()