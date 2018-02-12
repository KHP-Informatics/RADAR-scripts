#!/usr/bin/env python3
import Util.load_csvs
import matplotlib
matplotlib.use('Agg')
import Visualisation.actogram
import sys

data_folder = '/home/chronos/user/Documents/Data/45a9af3a-8fde-484d-9d2f-082d716facfb/android_phone_acceleration'

accel_data = Util.load_csvs.read_csv_folder_type(data_folder, data_type='acceleration')
accel_data['magnitude'] = accel_data[['value.x', 'value.y',
                                      'value.z']].pow(2).sum(axis=1).pow(1/2)
accel_data['magnitude'] = accel_data['magnitude'] - 1
accel_data['magnitude'] = accel_data['magnitude'].abs()
accel_downsamp = accel_data.resample('T').mean() # resamples to every 1min
fig = Visualisation.actogram.plot(accel_downsamp, datacol='magnitude')
fig.savefig('figout.png')
